"""Synthesizes speech from the input string of text or ssml.

Note: ssml must be well-formed according to:
    https://www.w3.org/TR/speech-synthesis/
"""
from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import AudioOutputConfig
# from google.cloud import texttospeech
import time
import string
import os
from subprocess import call
import sys
import utils
from .ai import auto_emotion

class MicrosoftTTS:
    def __init__(self):
        self.speaking_rate = 0.8    
        self.speaking_style = "general"
        self.volume = +1.0
        self.language = "en-US"
        self.voice_id = "en-US-AriaNeural"
        self.ssml_path = "files/datasets/ssml.xml"
        self.emotion_ai = auto_emotion.AutoEmotion()
        
    def _get_speech_config(self):
        region = "centralindia"
        try:
            return SpeechConfig(
                subscription=utils.get_env("MICROSOFT_TTS_KEY"), region=region
            )
        except Exception as e:
            utils.wlog("Error in Microsoft TTS "+str(e))
            return None

    def _get_ssml(self, text, end_silence=0):

        try:
            ssml_string = open(self.ssml_path, "r").read()
        except Exception as e:
            utils.wlog(str(e))
            utils.return_response({
                "status": "error",
                "message": f"Failed to read ssml file in {self.ssml_path}."
            })
            return ""

        # text_with_emotion = self.emotion_ai.emotion_audio(text, {})
        # ssml_string = ssml_string.replace("##text##", text_with_emotion)
        ssml_string = ssml_string.replace("##text##", text)
        ssml_string = ssml_string.replace(
            "##speaking_rate##", str(int((self.speaking_rate - 1) * 100)))
        ssml_string = ssml_string.replace(
            "##volume##", str(self.volume))
        ssml_string = ssml_string.replace(
            "##voice_id##", self.voice_id)
        ssml_string = ssml_string.replace(
            "##language##", self.language)
        ssml_string = ssml_string.replace(
            "##speaking_style##", self.speaking_style)
        ssml_string = ssml_string.replace(
            "##break_time##", str(end_silence))

        return ssml_string

    def set_config(self, config):

        if "speaking_rate" in config:
            self.speaking_rate = config["speaking_rate"]

        if "volume" in config:
            self.volume = config["volume"]

        if "language" in config:
            self.language = config["language"]

        if "voice_id" in config:
            self.voice_id = config["voice_id"]

        if "speaking_style" in config:
            self.speaking_style = config["speaking_style"]

    def write_file(self, filename, response):

        try:
            with open(filename, "wb") as out:
                # Write the response to the output file.
                out.write(response.audio_content)
                print(f"Audio content written to file {filename}")
        except Exception as e:
            utils.wlog(str(e))
            return False

        if os.stat(filename).st_size < 10:
            return False

        return True

    def create(self, text, config, filename, end_silence=0):
        self.speech_config = self._get_speech_config()
        self.set_config(config)

        for retry_count in range(3):
            filename = self.request_tts(text, filename, end_silence)
            if filename:
                return filename
            else:
                utils.wlog("retry count: " + str(retry_count))
                continue

        utils.return_response(
            {"status": "error", "message": "Failed to create TTS audio file using Google TTS."})
        return ""

    def request_tts(self, text, filename, end_silence=0):

        if not self.speech_config:
            utils.return_response(
                {
                    "status": "error",
                    "message": """Microsoft TTS config error. You need to create microsoft azure key and set it in environment variable MICROSOFT_TTS_KEY."""
                }
            )

        self.speech_config.set_speech_synthesis_output_format(
            SpeechSynthesisOutputFormat["Audio48Khz192KBitRateMonoMp3"])

        utils.wlog(f"Requesting TTS file {filename} for {text}")
        audio_config = AudioOutputConfig(filename=filename)

        synthesizer = SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=audio_config)

        ssml_string = self._get_ssml(text)
        utils.wlog("ssml_string: ", ssml_string)

        try:
            result = synthesizer.speak_ssml_async(ssml_string).get()
            stream = AudioDataStream(result)
            stream.save_to_wav_file(filename)
            utils.wlog("MS TTS result: ", result)
        except Exception as e:
            utils.wlog("Error in Microsoft TTS")
            utils.wlog(str(e))
            return ""

        utils.wlog("Filesize: "+str(os.stat(filename).st_size))
        
        return filename
