import requests
import utils
from .tts import TTS


class Audio:

    def __init__(self):
        self.structure = {
            "type": "url",
            "value": "",
            "volume": 1,
            "delay": 0,
            "duration": "auto"
        }
        self.required_keys = ["type"]
        self.tts = TTS()

    def validate(self, request):
        ''' Validate the request if audio element is correct or not '''

        # check keys for default elements
        res = utils.elements_validate_global_helper(
            request, self.required_keys, "audio")

        if res:
            return res

        # check keys for slides
        res = utils.elements_validate_slides_helper(
            request, self.required_keys, "audio")

        if res:
            return res

        return {"status": "success"}

    def process(self, request):
        ''' manage the audio file or TTS '''

        if "global_elements" in request and "audio" in request["global_elements"]:
            audio_file, video_duration, slides = self._handle_global_audio(
                request["global_elements"]["audio"], request)
        else:
            # audio could be of type tts or file url
            audio_file, video_duration, slides = self._handle_tts_audio(
                request)

        return audio_file, video_duration, slides



    def _handle_tts_audio(self, request):
        ''' manage the audio file or TTS'''
        # create tts files to all slides
        audio_files = self.tts.bulk_create(request)

        transition_delay = int(request['settings']['transition']['delay'])

        # concat all files
        audio_file, video_duration = self.tts.concat_files(
            audio_files, transition_delay)

        # add/update duration in slide
        slides = self._apply_slide_duration(
            request['slides'], audio_files, transition_delay)

        utils.wlog("AFter applying slide duration", slides)

        return audio_file, video_duration, slides

    def _handle_global_audio(self, audio_global_element, request):
        ''' manage the audio file or TTS 
            # 1. Download audio file from url and place it in preview folder
            # 2. Get the duration of the audio file
            # 3. Update the duration of the preview  with the duration of the audio file    
        '''

        # 1. Download audio file from url and place it in tmp folder
        audio_file = utils.download_file(
            audio_global_element['value'], "/tmp/")

        # 2. Get the duration of the audio file
        audio_duration = utils.get_duration(audio_file)

        # 3. remove the file from tmp folder
        utils.remove_file(audio_file)

        return audio_global_element['value'], audio_duration, request["slides"]

    def _apply_slide_duration(self, slides, audio_files, transition_delay):
        ''' update duration parameter of the slides with tts audio file length '''

        if len(audio_files) != len(slides):
            utils.return_response(
                {"status": "error", "message": "Internal error: length of tts is not equal to audio files"})

        updated_slides = slides
        for id, slide in enumerate(slides):
            if 'duration' in slide and 'depends_on' in slide['duration'] and slide['duration']['depends_on'] == "audio":
                # if min slide duration is set, then check if the duration of the audio file is greater than the min slide duration
                if 'min_duration' in slide['duration'] and audio_files[id]['duration'] < int(slide['duration']['min_duration']):
                    updated_slides[id]['duration']['value'] = slide['duration']['min_duration'] + transition_delay
                else:
                    updated_slides[id]['duration']['value'] = audio_files[id]['duration'] + transition_delay

        return updated_slides
