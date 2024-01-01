import json
from logging import PlaceHolder

import requests
import utils
from uuid import uuid4
from elements.audio import audio
from elements.background import background
from elements.slides import slides
from elements.template import template
from elements.template import boilerplate
from elements.overlay import overlay
from copy import deepcopy


class Preview:

    def __init__(self, request=None):

        if not request:
            self.request = utils.load_json_structure(
                "files/requests_json/simple.json")
        else:
            self.request = request

        self.audio_element = audio.Audio()
        self.background_element = background.Background()
        self.slides_element = slides.Slides()
        self.template_element = template.Template()
        self.boilerplate_element = boilerplate.Boilerplate()
        self.overlay_element = overlay.Overlay(self.request)

        self.request_params = ["default_elements",
                               "global_elements", "settings", "slides"]

        self.default_slide_structure = utils.load_json_structure(
            "files/structure/default_req.json")
        self.default_settings_structure = utils.load_json_structure(
            "files/structure/default_settings.json")

        SERVER_ADDRESS, SERVER_PORT = utils.get_server_details()
        self.SERVER_ADD = f"http://{SERVER_ADDRESS}:{SERVER_PORT}/"

    def process(self):
        ''' 
        Process will start from here request will come to this function for process 
        it returns the error or slide data if all things go fine
        '''
        request = self.request

        # Validations
        self.validate()
        self.validate_elements()

        # load a copy of default_slide_structure and replace default_elements
        default_slide_json = self.replace_default_elements(
            request, self.default_slide_structure)

        # fill default values in all slides
        request = self.fill_slides(request, default_slide_json)

        # update settings passed by the user in default settings elements
        request = self.fill_settings(request, self.default_settings_structure)

        # manage creation and placement of audio files
        audio_file, video_duration, slides = self.audio_element.process(
            deepcopy(request))

        # slides updated with duration
        request['slides'] = slides

        # add audio url in request
        self.update_global_elements(request, audio_file)

        # create a copy of boilerplate html and apply template
        # insert css and js of selected templates
        html_path = self.boilerplate_element.copy_boilerplate()

        # add video settings to index.html in html_path
        self.boilerplate_element.apply_boilerplate_placeholders(
            html_path, request)

        # NLP for text
        request = self.overlay_element.text_manager(deepcopy(request))

        # fill AI generated content in slides
        request = self.background_element.background_manager(
            deepcopy(request))

        request = self.slides_element.update_slide_duration(deepcopy(request))

        # load js, css and html, apply params to html
        page_html = utils.read_file(html_path+"/index.html")
        page_html = self.template_element.parse_js_css(page_html, request)
        page_html = self.process_html(page_html, deepcopy(request), html_path)

        return {"status": "success", "preview": html_path, "audio_file": audio_file, "video_duration": video_duration, "data": request}

    def validate(self):
        ''' Validate the whole json request for problems '''

        # request should contain something
        if not self.request:
            utils.return_response(
                {"status": "error", "message": "Request should contain atleast one of slides, default_elements key"})

        # check if any required key is missing
        if "default_elements" not in self.request and "slides" not in self.request:
            utils.return_response(
                {"status": "error", "message": "Request should contain atleast one of slides, default_elements key"})

        # check if there is any invalid key
        for key in self.request:
            if key not in self.request_params:
                utils.return_response(
                    {"status": "error", "message": f"{key} is unknown, please recheck the key name."})

        return True

    def validate_elements(self):
        ''' Validate all the elements present in the request '''
        request = self.request

        audio_validate_res = self.audio_element.validate(request)
        if audio_validate_res["status"] == "error":
            utils.return_response(audio_validate_res)

        background_validation_res = self.background_element.validate(request)
        if background_validation_res['status'] == "error":
            utils.return_response(background_validation_res)

    def replace_default_elements(self, request, default_slide):
        return self.slides_element.replace_default_elements(
            request, default_slide)

    def fill_slides(self, request, default_slide_json):
        """ for all slides, keep the settings passed by the user and
        fill the default values in default_slide_json """

        # If there is nothing in the slides
        # Then default elements should be present to create single slide video
        if "slides" not in request:
            request["slides"] = default_slide_json
            return request

        slides = []
        for slide in request['slides']:
            filled_slide = self.slides_element.fill_slide(
                slide, default_slide_json)
            slides.append(deepcopy(filled_slide))

        request["slides"] = slides
        return request

    def fill_settings(self, request, default_settings):
        """ fill the missing values with defaults in settings """

        filled_settings = self.slides_element.fill_default_settings(
            request, default_settings)
        request['settings'] = filled_settings

        return request

    def process_html(self, page_html, request, html_path):
        """ load the html and replace the params passed by user """
        slide_html = "\n"
        for slide_id, slide in enumerate(request['slides']):
            section_html_tmp = self.template_element.html_template_manager(
                slide, request)
            slide_html += "\n"+section_html_tmp+"\n"

        if not page_html:
            utils.return_response(
                {"status": "error", "message": f"error in parsing css and js {html_path}"})

        page_html = self.template_element.apply_html(page_html, slide_html)

        if not utils.write_file(html_path+"/index.html", page_html):
            utils.return_response(
                {"status": "error", "message": f"Unable to write file in template path {html_path}"})

        return page_html

    def update_global_elements(self, request, audio_file):
        if "global_elements" not in request:
            request["global_elements"] = {}

        if "audio" not in request['global_elements']:
            request["global_elements"]["audio"] = {}

        if "value" not in request['global_elements']['audio']:
            # audio was created by TTS and global elements needs to be updated
            request['global_elements']['audio']['value'] = self.SERVER_ADD + audio_file
            request['global_elements']['audio']['type'] = "file"
        elif "value" in request['global_elements']['audio'] and "type" in request['global_elements']['audio'] and request['global_elements']['audio']['type'] == "file":
            # URL is passed in global elements , not thing to be done
            pass
        else:
            utils.return_response(
                {"status": "error", "message": "Something not correct in global_elements > Audio, please check docs."})


if __name__ == "__main__":

    preview = Preview()
    data = preview.process()

    print(data)
