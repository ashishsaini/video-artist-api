import utils
import openai
import os


class Pointers:

    def __init__(self) -> None:
        self.response_length = 100
        self.PROMPT_PATH = "files/datasets/overlay_ai_pointers_prompt.txt"
        self.MAX_POINTERS = 4

    def _get_prompt(self):
        """ load prompt for pointer from file"""
        prompt = ""
        try:
            with open(self.PROMPT_PATH, "r") as f:
                prompt = f.read()
        except Exception as e:
            utils.wlog(
                "error", "Unable to load prompt file from elements > overlay > ai > pointers")
            utils.return_response(
                {"status": "error", "message": "Internal error in AI module"})
        return prompt

    def _clean_response(self, text):
        """ OPenAI response text is raw, needs some cleaning"""
        lines = text.split("*")
        
        text = text.replace("\n", " ")

        # AI could return too many pointers, need to keep it in limit
        if len(lines) > self.MAX_POINTERS:
            lines = lines[:self.MAX_POINTERS]

        result = "<ul>"
        for i, line in enumerate(lines):

            if i == len(lines)-1 and len(lines) > 4:
                utils.wlog("notice", f"skipping line : {line}")
                continue;
                
            if len(line) > 10:
                line = line.strip()
                if line[-1] != ".":
                    line = line + "."
                result += "<li> "+line+"</li>"
            
        result += "</ul>"
        return result

    def text_to_pointers(self, text, settings):
        self.OPENAI_KEY = os.environ.get("OPENAI_KEY")
        """ use openAI API to convert text to pointers """
        prompt = self._get_prompt()
        openai.api_key = self.OPENAI_KEY
        utils.wlog("notice", "sending data to openAI")
        try:
            response = openai.Completion.create(
                engine="curie-instruct-beta",
                prompt=f"{prompt}#Summerize the text in short pointers with each pointer less than 15 words\n#return clean text without special chars other than * , and . \n{text}\n\n Pointers:",
                temperature=0.7,
                max_tokens=self.response_length,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
        except Exception as e:
            utils.wlog(
                "Warning: Unable to convert text to pointers OpenAI issue: ", e)

        utils.wlog("notice", f"openai response : {response}")

        return self._clean_response(response["choices"][0]["text"])
