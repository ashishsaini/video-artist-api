from google.cloud import texttospeech
import utils
import os


class GoogleTTS:
    def __init__(self):
        self.speaking_rate = 0.8
        self.volume = +4.0
        self.language = "en-GB"
        self.voice_id = "en-GB-Wavenet-F"

    def set_config(self, config):
        if "speaking_rate" in config:
            self.speaking_rate = config["speaking_rate"]

        if "volume" in config:
            self.volume = config["volume"]

        if "language" in config:
            self.language = config["language"]

        if "voice_id" in config:
            self.voice_id = config["voice_id"]

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
        self.client = texttospeech.TextToSpeechClient()
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

    def request_tts(self,  text, filename, end_silence=0):

        print("creating tts for text: ", text)

        ssml_text = f"<speak>{text}<break time=\"{end_silence}ms\" strength=\"weak\"/></speak>"

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.VoiceSelectionParams(
            language_code=self.language, name=self.voice_id
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=self.speaking_rate,
            volume_gain_db=self.volume
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = self.client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        if self.write_file(filename, response):
            return filename
        else:
            return ""
