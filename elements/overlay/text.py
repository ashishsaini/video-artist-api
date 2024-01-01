import utils
from .nlp import NLP


class Text:

    def __init__(self, request):
        self.structure = {
            "type": "heading",
            "value": "",
            "style": 1,
            "position": 0,
            "delay": 0,
            "duration": "auto"
        }
        self.validate(request)
        self.required_keys = ["value"]
        self.nlp = NLP()
        self.DEFAULT_KEYWORD = "black background"
