import utils
from . import ai_background
from . import site_background
from . import web_image

class Background:

    def __init__(self):
        self.structure = {
            "type": "video",
            "value": "",
            "keywords": [
                "black",
                "sunrise"
            ],
            "source": "pexels"
        }
        self.required_keys = ["type"]
        self.ai_background_element = ai_background.AIBackground()
        self.site_background_element = site_background.SiteBackground()
        self.web_image = web_image.WebImage()

    def validate(self, request):
        ''' Validate the request if audio element is correct or not '''

        # check keys for default elements
        res = utils.elements_validate_default_helper(
            request, self.required_keys, "background")

        if res:
            return res

        # check keys for slides
        res = utils.elements_validate_slides_helper(
            request, self.required_keys, "background")

        if res:
            return res

        return {"status": "success"}

    def background_manager(self, request):
        """ Manage multiple options for AI content for background.
        Identify if AI is required in the slide or not
            if not required then return same result
            else forward the process to required process for video or image

        Returns: request containing elements selected by AI
        """

        slides = []
        # check if video generation is required
        for slide in request['slides']:

            if slide['background']['value'] != "" and slide['background']['type'] in ["image", "video", "color"]:
                pass
            # video ai selection creteria
            elif len(slide['background']['keywords']) >= 1 and slide['background']['type'] in ["web-search"]:
                utils.wlog("web search: " + str(slide['background']['keywords']))
                slide = self.web_image.manager(slide, request)
            elif len(slide['background']['keywords']) >= 1 and slide['background']['type'] in ["image", "video"]:
                slide = self.ai_background_element.manager(slide, request)
            elif slide['background']['type'] == "website":
                if "value" in slide["background"] and utils.is_valid_url(slide['background']['value']):
                    slide = self.create_site_video(slide, request)
            slides.append(slide)

        request["slides"] = slides
        return request

    def create_site_video(self, slide, request):
        """
        Open website and record video using our own timecut server
        """
        bg_video_url = self.site_background_element.manager(
            slide["background"]["value"], request["settings"])

        utils.wlog("bg_video_url: " + str(bg_video_url))
        slide["background"]["type"] = "video"
        slide["background"]["value"] = bg_video_url

        return slide
