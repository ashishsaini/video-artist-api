import sys
#sys.path.append('/app')
from langdetect import detect
import  utils

class Language:

    def __init__(self):
        self.DEFALUT_LANGUAGE_DATA = {"name": "English","language_code": "en-US","voice_id": "en-US-GuyNeural","provider": "microsoft"} 
        self.LANGUAGE_ID_PATH = "files/datasets/tts-languages.json"

    def detect_language(self, text):
        """ 
        1. get the language id of the text
        2. get language data from language id
        3. if not found, return default language
        4. return language data
        """
        language_id = detect(text)
        language_data = self.load_language_data(self.LANGUAGE_ID_PATH)

        if not language_data:
            return self.DEFALUT_LANGUAGE_DATA

        if language_id in language_data:
            return language_data[language_id]
        else:
            return language_data["en"]
        

    def load_language_data(self, languages_file_path):
        """ load json data from language file which has id to tts language mapping """
        try:
            data = utils.load_json_structure(languages_file_path)
        except Exception as e:
            utils.wlog("Error loading language data: {}".format(e))
            data = {}
        return data


# if __name__ == "__main__":
#     language = Language()
    
#     print(language.detect_language("Geeksforgeeks is a computer science portal for geeks"))
#     print(language.detect_language("Geeksforgeeks geeks के लिए एक कंप्यूटर विज्ञान पोर्टल है"))
    