import utils
import openai
import os


class AutoEmotion:

    def __init__(self) -> None:
        self.response_length = 100
        self.PROMPT_PATH = "files/datasets/tts_emotion_ai_prompt.txt"

    def _get_prompt(self):
        """ load prompt for pointer from file"""
        prompt = ""
        try:
            with open(self.PROMPT_PATH, "r") as f:
                prompt = f.read()
        except Exception as e:
            utils.wlog(
                "error", "Unable to load prompt file from elements > audio > ai > auto_emotion")
            utils.return_response(
                {"status": "error", "message": "Internal error in AI module"})
        return prompt

    def emotion_audio(self, text, settings):
        """ use openAI API to text to text with emotion ssml to microsoft tts """
        self.OPENAI_KEY = os.environ.get("OPENAI_KEY")
        prompt = self._get_prompt()

        openai.api_key = self.OPENAI_KEY
        request_string = f"{prompt} \n\n "+text+ "\n\n result:"
        utils.wlog("notice", "sending data to openAI")
        utils.wlog("notice", f"openai request : {request_string}")
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=request_string,
                temperature=0.7,
                max_tokens=2480,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        except Exception as e:
            utils.wlog(
                "Warning: Unable to convert text to emotion ssml OpenAI issue: ", e)

        utils.wlog("notice", f"openai response : {response}")

        result = response['choices'][0]['text'].replace("rate=\"0%\"", "rate=\"##speaking_rate##%\"")
        result = result.replace("rate=\"0.0%\"", "rate=\"##speaking_rate##%\"")

        return result
