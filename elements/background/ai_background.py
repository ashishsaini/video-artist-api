import utils
from .pexels_video_downloader.image_downloader import ImageDownloader
from .pexels_video_downloader.video_downloader import VideoDownloader
import random


class AIBackground:

    def __init__(self) -> None:
        self.pexels_video = VideoDownloader("/tmp/pexels_downloader.log")
        self.pexels_image = ImageDownloader("/tmp/pexels_downloader.log")
        self.FALLBACK_VIDEO_URL = "https://player.vimeo.com/external/370845738.hd.mp4?s=84cededa6d639f4dc0ac6abb9debf898d828bcde&profile_id=175&oauth2_token_id=57447761"
        self.FALLBACK_IMAGE_KEYWORD = "black background"

    def manager(self, slide, request):
        """ Manage multiple options for AI content for background.
        Identify if AI is required in the slide or not
            if not required then return same result
            else forward the process to required process for video or image 

        Returns: request containing elements selected by AI
        """

        # video ai selection creteria
        if len(slide['background']['keywords']) >= 1 and slide['background']['type'] == "video":
            video_url = self._generate_video(
                slide['background']['keywords'], request)

            # insert generated content in slide json
            slide['background']['value'] = video_url

        elif len(slide['background']['keywords']) >= 1 and slide['background']['type'] == "image":
            # Generate image
            image_url = self._generate_image(
                slide['background']['keywords'], request)

            # insert generated content in slide json
            slide['background']['value'] = image_url

        slide['background']['value']

        return slide

    def _get_orientation(self, request):
        """
        Input: request containing settings
        Output: orientation of the background
        """
        if request['settings']['video']['resolution']['width'] > request['settings']['video']['resolution']['height']:
            return "landscape"
        elif request['settings']['video']['resolution']['width'] < request['settings']['video']['resolution']['height']:
            return "portrait"
        else:
            return "square"

    def _generate_video(self, keywords, request):
        """ 
        Input: list or single keyword to search video
        Output: URL of selected video
        """

        # set resolution of video to be downloaded
        self.pexels_video.resolution_width = request['settings']['video']['resolution']['width']
        self.pexels_video.media_cache_dir = "data/path/media_cache"
        self.pexels_video.orientation = self._get_orientation(request)

        video_file = ""
        random.shuffle(keywords)

        for keyword in keywords:
            if not video_file:
                selected_video_id = self.pexels_video.search_video(keyword)
                if not selected_video_id:
                    continue

                video_file = self.pexels_video.download(selected_video_id)

        # If no video found for given keywords then send a fallback video
        if not video_file:
            return self.FALLBACK_VIDEO_URL

        return video_file

    def _generate_image(self, keywords, request):
        """ search an image from pexels API """

        # set resolution of image to be downloaded
        self.pexels_image.resolution_height = request['settings']['video']['resolution']['height']
        self.pexels_image.resolution_width = request['settings']['video']['resolution']['width']
        self.pexels_image.media_cache_dir = "data/path/media_cache"
        self.pexels_image.orientation = self._get_orientation(request)

        image_url = ""
        for i in range(3):
            image_url = self.pexels_image.get_image(
                random.choice(keywords))

            if image_url:
                break

        if not image_url:
            image_url = self.pexels_image.get_image(
                self.FALLBACK_IMAGE_KEYWORD)

        return image_url
