''' 
Open website and record video using our own timecut server
'''

import requests
import json
import uuid
import utils


class SiteBackground:
    def __init__(self):
        self.site_url = ""
        self.duration = 10
        self.fps = 15
        self.waitUntil = "domcontentloaded"
        self.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        self.timeout = 30
        self.resolution = {"width": 1920, "height": 1080}
        self.EMULATE_DEVICE = 'Galaxy S5'

    def manager(self, url, request_settings):

        if not self.TIMECUT_URL : self.TIMECUT_URL = utils.get_env("TIMECUT_URL")
        if not self.TIMECUT_IP : self.TIMECUT_IP = utils.get_env("TIMECUT_IP")

        # check iff url is valid
        if not utils.is_valid_url(url):
            return None

        if "video" in request_settings and "resolution" in request_settings["video"]:
            self.resolution = request_settings["video"]["resolution"]

        # get the site url
        self.site_url = url

        bg_video_url = ""
        for retry_count in range(3):
            bg_video_url = self.request_timecut()
            if bg_video_url:
                return bg_video_url
            else:
                utils.wlog("retry count: " + str(retry_count))
                continue

        if not bg_video_url:
            utils.return_response({
                "status": "error",
                "message": f"Failed to create background video ffor URL : {url}"
            })

    def request_timecut(self):
        filename = str(uuid.uuid4()) + ".mp4"
        payload = {
            "url": self.site_url,
            "duration": self.duration,
            "resolution": self.resolution,
            "fps": self.fps,
            "filename": filename,
            "screenshotType": "jpeg",
            "waitUntil": self.waitUntil,
            "userAgent": self.userAgent,
            "deviceName": self._get_device_name()
        }

        headers = {"Content-Type": "application/json"}

        try:
            result = requests.post(
                self.TIMECUT_URL,
                headers=headers,
                data=json.dumps(payload),
                timeout=self.timeout,
            )
        except Exception as e:
            print(e)
            return False

        utils.wlog(f"Timecut URL: {self.site_url}, response : {result.text}")

        return result.text.replace("127.0.0.1", self.TIMECUT_IP)

    def _get_device_name(self):
        if self.resolution["width"] < self.resolution["height"]:
            return self.EMULATE_DEVICE
        else:
            return ""
