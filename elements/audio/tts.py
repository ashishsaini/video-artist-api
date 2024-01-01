from google.cloud import texttospeech
import uuid
import os
import utils
import subprocess
import hashlib
from helpers.media_cache import MediaCache
import shutil
from uuid import uuid4
from .google_tts import GoogleTTS
from .microsoft_tts import MicrosoftTTS
from .ai import language

class TTS():

    def __init__(self):
        audio_tmp_dir_name = str(uuid.uuid4())
        self.AUDIO_DIR = os.getcwd()+"/data/audio/"+audio_tmp_dir_name+"/"
        self.AUDIO_DIR_REL = "data/audio/"+audio_tmp_dir_name+"/"
        self.SEC_SILENCE_GOOGLE = os.getcwd() + '/files/1sec_silence.wav'
        self.SEC_SILENCE_MICROSOFT = os.getcwd() + '/files/1sec_silence_48k.wav'
        self.DEFAULT_PROVIDER = "microsoft"
        self.DEFAULT_SPEAKING_STYLE = "general"
        self.media_cache_dir = "data/path/media_cache"
        self.media_cache = MediaCache(self.media_cache_dir)
        self.config_tts = {}
        self.google_tts = GoogleTTS()
        self.microsoft_tts = MicrosoftTTS()
        self.language_ai = language.Language()

        SERVER_ADDRESS, SERVER_PORT = utils.get_server_details()
        self.SERVER_ADD = f"http://{SERVER_ADDRESS}:{SERVER_PORT}/"

    def __del__(self):
        print("TTS Object destroyed")

    def create_tts_cache_name(self, slide):
        """
        Create a unique name for the cache file
        """
        return slide['audio']['value'] + \
            slide['audio']['language'] + \
            slide['audio']['voice_id'] + \
            str(slide['audio']['volume']) + \
            str(slide['audio']['speaking_rate']) + \
            slide["audio"]["provider"]

    def bulk_create(self, request):
        """
        Create a bulk of TTS files

        For each slide in the request:
            1. validate tts params passed by user in slide["audio"]
            2. create dir if not exists for tts files
            3. create tts file or blank file if not tts passed
            4. append the file to audio list
        return : list of (filename, duration) of tts files

        """

        slides = request['slides']

        self.transition_delay = request['settings']['transition']['delay']
        audio_list = []

        for id, slide in enumerate(slides):

            # if audio type is url, this means URL is passed and can be directly used
            if slide['audio']['type'] == "url":
                audio_list.append(
                    {"filename": slide['audio']['value'], "duration": utils.get_duration(slide['audio']['value']) })
                continue

            # autodetect and apply settings of language
            slide = self.detect_and_apply_language(slide)
            
            # update volume, language as passed by user
            self._apply_settings(slide)

            # if not tts text and slide duration present then
            # we cant continue
            if 'audio' not in slide or 'duration' not in slide:
                utils.wlog(
                    "Error: either tts or slide duration must be present")
                break

            # create directory to hold tts files
            self.check_and_create_dir(self.AUDIO_DIR)

            # no tts text passed, create a blank audio file, if not create tts
            if slide['audio']['type'] != "tts" and 'duration' in slide:
                cache_name = "silence_"+str(slide['duration']['value'])
            elif slide['audio']['type'] == "tts":
                cache_name = self.create_tts_cache_name(slide)

            filename, duration = self.manage_audio_creation(
                slide, cache_name)

            slide['audio']['value'] = self.SERVER_ADD + \
                filename.replace("/app", "")
            slide['audio']['type'] = "url"
            utils.wlog("TTS file created or recevied from cache: " + filename)
            audio_list.append({"filename": filename, "duration": duration})

        return audio_list

    def manage_audio_creation(self, slide, cache_name):
        """
        Checks the file in cache:
            if found move to slide dir
            if not found create file according to TTS or silence
        returns the file path and duration
        """
        cache_name_md5 = hashlib.md5(cache_name.encode()).hexdigest()
        cache_result = self.media_cache.get(cache_name_md5)
        utils.wlog(
            f"Cache key : {cache_name_md5}, Cache Result: {cache_result}")

        min_duration = 0
        if "duration" in slide and "min_duration" in slide["duration"]:
            min_duration = slide["duration"]["min_duration"]

        audio_name = str(uuid4())
        if self.move_cache_file(cache_result, self.AUDIO_DIR):
            # cache found
            utils.wlog("Cache found")
            filename = self.AUDIO_DIR+cache_result.split("/")[-1]
            duration = float(utils.get_duration(filename))
        else:
            utils.wlog("Cache not found, generating TTS")
            if slide["audio"]["type"] == "tts" and slide["audio"]["value"] != "":
                filename = self.get_tts(
                    slide["audio"]["value"], self.config_tts,
                    self.AUDIO_DIR+audio_name+".mp3", min_duration)
                duration = float(utils.get_duration(filename))
            else:
                filename = self.generate_silence(
                    int(slide['duration']['value'])/1000, self.AUDIO_DIR+audio_name+".mp3")
                duration = float(slide['duration']['value'])

            # save the file in cache for next access
            self.media_cache.save(
                self.AUDIO_DIR+audio_name+".mp3", cache_name_md5)

        return filename, duration

    def get_tts(self, text, config_tts, audio_file, min_duration=0):
        ''' Add silence if audio duration is less than min duration '''
        filename = self.route_provider(text, config_tts, audio_file)

        audio_duration = utils.get_duration(filename)
        utils.wlog(f" Audio duration: {audio_duration} {min_duration}")

        if audio_duration < min_duration:
            audio_name = str(uuid4())
            diff_duration = min_duration - audio_duration
            filename = self.route_provider(
                text, config_tts, self.AUDIO_DIR+audio_name+".mp3", diff_duration)

        return filename

    def route_provider(self, text, config_tts, audio_file, diff_duration=0):
        """
        Create a tts file according to provider
        """
        if config_tts['provider'] == "google":
            return self.google_tts.create(
                text, config_tts, audio_file, diff_duration)
        elif config_tts['provider'] == "microsoft":
            return self.microsoft_tts.create(
                text, config_tts, audio_file, diff_duration)
        else:
            utils.return_response({
                "status": "error", "message": "Invalid provider, or no provider provided"
            })

    def detect_and_apply_language(self, slide):
        """
        Detect language and apply it to the slide
        """
        if "audio" not in slide:
            utils.wlog("1")
            return slide

        if "language" not in slide["audio"]:
            utils.wlog("2")
            return slide

        if "type" in  slide["audio"] and slide["audio"]["type"] != "tts":
            utils.wlog("3")
            return slide

        if slide["audio"]["language"] == "auto" and slide["audio"]["value"] != "":
            tts_language_data = self.language_ai.detect_language(slide["audio"]["value"])
            utils.wlog(tts_language_data)
            slide["audio"]["language"] = tts_language_data["language_code"]
            slide["audio"]["voice_id"] = tts_language_data["voice_id"]
            slide["audio"]["provider"] = tts_language_data["provider"]

        return slide        

    def move_cache_file(self, source, destination):
        # check if tts exists in cache
        if source and os.path.exists(source):
            try:
                shutil.copy(source, destination)
            except Exception as e:
                print("unable to copy tts file", source, destination, str(e))
                return False

            return True
        else:
            return False

    def check_and_create_dir(self, dir):
        if not os.path.isdir(dir):
            try:
                os.makedirs(dir)
            except:
                utils.wlog("Unable to create TTS directory "+dir)
                exit()
        return True

    def generate_cache_name(self, sox_input):
        """ 
        1. remove directory names of audio files in sox input
        2. remove output file name from sox input
        3. remove " " from sox input
        """
        inputs = sox_input.strip().split(" ")
        cache_name = ""
        for i, input in enumerate(inputs):
            if not input:
                continue

            if "/" in input:
                cache_name += input.split("/")[-1]
            else:
                cache_name += input
        return cache_name

    def concat_files(self, files, transition_delay):
        """ 
        concat audio files of all slides according to slide duration
            and transition delay

        1. create sox input string with all audio files and silence bwtwen them
            according to transition delay
        2. check the file media cache, with key md5( [sox input string] - [output_filename] )
        3. if found, use that audio file and move to slide folder
        4. if not found, create audio file and save in cache

        """
        sox_input = " "

        out_filename = str(uuid4())+".mp3"
        silence_str = self._generate_silence_str(transition_delay)
        for idx, file in enumerate(files):
            if not idx:
                sox_input += " "+file['filename']+" "
            else:
                sox_input += " "+silence_str+" "+file['filename']+" "

        cache_name = self.generate_cache_name(sox_input)
        # try the file in cache first
        cache_name_md5 = hashlib.md5(cache_name.encode()).hexdigest()
        cache_result = self.media_cache.get(cache_name_md5)

        utils.wlog("sox input: "+sox_input)

        self.check_and_create_dir( self.AUDIO_DIR)

        # if self.move_cache_file(cache_result, self.AUDIO_DIR):
        #     # cache found
        #     out_filename = cache_result.split("/")[-1]
        # else:
        utils.run_sox(sox_input, self.AUDIO_DIR+out_filename)

        # save the file in cache for next access
        self.media_cache.save(
            self.AUDIO_DIR+out_filename, cache_name_md5
        )

        audio_duration = utils.get_duration(self.AUDIO_DIR+out_filename)

        utils.wlog("audio duration: "+str(audio_duration))

        return self.AUDIO_DIR_REL+out_filename, audio_duration

    def _generate_silence_str(self, transition_delay):
        """ Create silence string according to the duration of silence provided """

        silence_file = self.SEC_SILENCE_MICROSOFT
        if "provider" in self.config_tts and self.config_tts['provider'] == "google":
            silence_file = self.SEC_SILENCE_GOOGLE
        
        silence_str = ""
        for i in range(round((transition_delay)/1000)):
            silence_str += " "+silence_file+" "
        return silence_str

    def generate_silence(self, duration, file):
        # generates a slience file of n seconds
        silence_file = self.SEC_SILENCE_MICROSOFT
        if self.config_tts['provider'] == "google":
            silence_file = self.SEC_SILENCE_GOOGLE
        try:
            result = subprocess.run(['sox', silence_file, file, 'repeat', str(duration - 1)],
                 stdout=subprocess.PIPE).stdout.decode('utf-8')
            result = result.strip()
            # result = (subprocess.check_output(
            #     ['sox', silence_file, file, 'repeat', str(duration - 1)]).decode().strip())
        except Exception as e:
            utils.wlog("error", "Could not generate silence file")
            print(e)
            result = ""

        return file

    def _apply_settings(self, slide):
        ''' load tts settings passed by user '''
        if "language" in slide['audio']:
            self._validate_language(slide['audio']['language'])
            self.config_tts["language"] = slide['audio']['language']

        if "voice_id" in slide['audio']:
            self._validate_voice_id(slide['audio']['voice_id'])
            self.config_tts["voice_id"] = slide['audio']['voice_id']

        if "volume" in slide['audio']:
            self._validate_volume(slide['audio']['volume'])
            self.config_tts["volume"] = slide['audio']['volume']

        if "speaking_rate" in slide['audio']:
            self._validate_speaking_rate(slide['audio']['speaking_rate'])
            self.config_tts["speaking_rate"] = slide['audio']['speaking_rate']

        if "speaking_style" in slide['audio']:
            self._validate_speaking_style(slide['audio']['speaking_style'])
            self.config_tts["speaking_style"] = slide['audio']['speaking_style']
        else:
            self.config_tts["speaking_style"] = self.DEFAULT_SPEAKING_STYLE

        if "provider" in slide["audio"]:
            self._validate_provider(slide["audio"]["provider"])
            self.config_tts["provider"] = slide["audio"]["provider"]
        else:
            self.config_tts["provider"] = self.DEFAULT_PROVIDER

    def _validate_language(self, language):
        if not language:
            utils.return_response(
                {"status": "error", "message": f"Language code is Invalid : {language}"})
        return True

    def _validate_voice_id(self, voice_id):
        if not voice_id:
            utils.return_response(
                {"status": "error", "message": f"Voice id is invalid : {voice_id}"})
        return True

    def _validate_volume(self, volume):
        if not volume:
            utils.return_response(
                {"status": "error", "message": f"volume value is invalid : {volume}"})
        return True

    def _validate_speaking_rate(self, speaking_rate):
        if not speaking_rate:
            utils.return_response(
                {"status": "error", "message": f"speaking_rate is invalid : {speaking_rate}"})
        return True

    def _validate_speaking_style(self, speaking_style):
        if not speaking_style and speaking_style not in ["general", "cheerful"]:
            utils.return_response(
                {"status": "error", "message": f"speaking_style is invalid : {speaking_style}"})
        return True

    def _validate_provider(self, provider):
        if not provider or provider not in ["google", "microsoft", "auto"]:
            utils.return_response(
                {"status": "error", "message": f"provider is invalid : {provider}"})
        return True
