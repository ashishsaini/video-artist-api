import utils
import requests 
import json 
import random

class WebImage:

    def __init__(self) -> None:
        pass

    def manager(self, slide, request):
        """ 
        Returns: request containing links of images according to keywords
        """
        if not self.image_server_url: self.image_server_url = utils.get_env("IMAGE_SERVER_URL")
        if not self.image_server_key: self.image_server_key = utils.get_env("IMAGE_SERVER_KEY")
        # video ai selection creteria
        if len(slide['background']['keywords']) >= 1:
            utils.wlog("Generating image...")
            # Generate image
            image_url = self.search(",".join(slide['background']['keywords']))
            # insert generated content in slide json
            slide['background']['value'] = image_url
            slide['background']['type'] = "image"

        return slide
        
    def search(self, query):
        """
        Input: query to search
        Output: list of images
        """
        utils.wlog("Searching for images...")
        try:
            url = self.image_server_url+"?query="+query
            headers = {
                'key': self.image_server_key
            }
            response = requests.request("GET", url, headers=headers)
            links = json.loads(response.text)['links']
        except Exception as e:
            utils.wlog(e)
            return ""
        
        # return random image from list
        return random.choice(links)        
    
        
        
