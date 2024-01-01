import utils
from .nlp import NLP
from .ai import pointers
from .ai import web_image

class Overlay:

    def __init__(self, request):
        self.structure = {
            "type": "heading",
            "value": "",
            "style": 1,
            "position": 0,
            "delay": 0,
            "duration": "auto"
        }
        self.VALID_TYPES = ["text", "image", "video", "hw", "web-search"]
        self.validate(request)
        self.nlp = NLP()
        self.ai_pointers = pointers.Pointers()
        self.web_image = web_image.WebImage()
        self.DEFAULT_KEYWORD = "white background"

    def validate(self, request):
        ''' Validate the text param inputs '''

        if "slides" not in request:
            utils.return_response(
                {"status": "error", "message": "'slides' param is required."})

        for slide in request["slides"]:

            # Check if the text provided in a list
            if "overlay" not in slide or type(slide["overlay"]) is not list:
                utils.return_response(
                    {"status": "error", "message": "'overlay' list param is missing inside a slide, or 'overlay' not a list."})

            # check if required params are passed
            for element in slide['overlay']:
                if "type" not in element:
                    utils.return_response(
                        {"status": "error", "message": "'value' required in slides > overlay > element."})

                if type(element["type"]) is not str:
                    utils.return_response(
                        {"status": "error", "message": "slides > overlay > element > 'type' must be a string."})

                if element["type"] not in self.VALID_TYPES:
                    utils.return_response(
                        {"status": "error", "message": "slides > overlay > element could have only " + ", ".join(self.VALID_TYPES) + " types."})

                if "value" not in element:
                    utils.return_response(
                        {"status": "error", "message": " slides > overlay > element must contain value"})

                if type(element["value"]) is not str:
                    utils.return_response(
                        {"status": "error", "message": "slides > overlay > element > 'value' must be a string."})

                if len(element["value"]) > 2000:
                    utils.return_response(
                        {"status": "error", "message": " slides > overlay > element > value must be less than 2000 characters."})

                if "delay" in element and type(element["delay"]) is not int:
                    utils.return_response(
                        {"status": "error", "message": " slides > overlay > element > delay must be an integer."})

                if "delay" in element and element["delay"] < 0:
                    utils.return_response(
                        {"status": "error", "message": " slides > overlay > element > delay must be greater than 0."})

                if "position" in element and type(element["position"]) is not str:
                    utils.return_response(
                        {"status": "error", "message": " slides > overlay > element > position must be a string."})

                if "position" in element and len(element['position']) > 1000:
                    utils.return_response(
                        {"status": "error", "message": " slides > overlay > element > position must be less than 1000 characters."})

                if "style" in element and type(element["style"]) is not str:
                    utils.return_response(
                        {"status": "error", "message": " slides > overlay > element > style must be a string."})

                if "style" in element and len(element['style']) > 1000:
                    utils.return_response(
                        {"status": "error", "message": " slides > overlay > element > style must be less than 1000 characters."})

        return True

    def text_manager(self, request):
        '''  Manages the process of text manipulation using different AI's '''
        for slide in request["slides"]:
            if not slide["background"]["value"] and not slide["background"]["keywords"]:
                # keywords and value both are not given by the user
                # Ai should automatically select the keywords from text or tts
                keywords = self._text_manager_keywords(slide)

            if "overlay" in slide:
                slide = self._text_manager_pointers(slide)

        return request

    def _text_manager_pointers(self, slide):
        """ Manager for text to pointer conversion """
        for overlay in slide["overlay"]:
            ai_pointer = {}
            if "type" in overlay and overlay["type"] == "text" and "ai" in overlay:
                for ai in overlay["ai"]:
                    if ai["type"] == "pointers":
                        ai_pointer = ai

                        overlay['value'] = self.ai_pointers.text_to_pointers(
                            overlay["value"], ai_pointer)
                        del(overlay["ai"])
            if "type" in overlay and overlay["type"] == "image" and "ai" in overlay:
                for ai in overlay["ai"]:
                    if ai["type"] == "web-search":
                        overlay['value'] = self.web_image.search(overlay["value"])
                        overlay['type'] = "image"
                        del(overlay["ai"])
                        print("overlay['value'] > ", overlay['value'])
            ai_pointer = {}

            print(">>> slide", slide)    
        return slide

    def _text_manager_keywords(self, slide):
        """ Offloads text_manager(), handles the logic for creating keywords """

        text = ""
        # priority of tts is lower than heading
        if slide["audio"]["type"] == "tts" and len(slide["audio"]["value"]) > 20:
            text = slide["audio"]["value"]

        text_value = self._get_combined_text(slide)
        if text_value and len(text_value) > 20:
            text = text_value

        if len(text) > 20:
            keywords = self.nlp.get_common_keywords(text)
            print("Generated keywords > ", keywords)
        else:
            keywords = [self.DEFAULT_KEYWORD]

        slide["background"]["keywords"] = keywords
        if not slide["background"]["type"]:
            slide["background"]["type"] = "video"

        return keywords

    def _get_combined_text(self, slide):
        ''' If there are mutliple text inputs, we need to combine them to pass it into keyword detection '''
        combined_text = ""
        for element in slide["overlay"]:
            if element["type"] == "text":
                combined_text += " ."+element['value']
        return combined_text
