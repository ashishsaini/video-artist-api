import json
import os
import shutil
import utils
import uuid
from copy import deepcopy


class Template:

    def __init__(self):
        # access base templates
        self.TEMPLATES_DIR = os.getcwd()+"/templates/"

        # path where copy of boilerplate will be stored
        self.TEMPLATES_TMP = os.getcwd()+"/data/path/"
        self.TEMPLATES_TMP_REL = "data/path/"

        # placeholders for replacing css, js and html
        self.snippet_css_start = "<!-- ##css_start## -->"
        self.snippet_css_end = "<!-- ##css_end## -->"
        self.boilerplate_css_placeholder = "<!-- ##css_space## -->"
        self.snippet_js_start = "<!-- ##js_start## -->"
        self.snippet_js_end = "<!-- ##js_end## -->"
        self.boilerplate_js_placeholder = "<!-- ##js_space## -->"
        self.snippet_html_start = "<!-- ##html_start## -->"
        self.snippet_html_end = "<!-- ##html_end## -->"
        self.boilerplate_html_placeholder = "<!-- ##html_space## -->"

        self.template_class_placeholder = "$$template_class$$"

    def parse_js_css(self, page_html, req):
        ''' manage parse_js and parse_css functions '''
        templates = utils.get_templates_from_req(req)
        validate_template_result = utils.validate_templates(
            templates, self.TEMPLATES_DIR)

        if validate_template_result["status"] == "error":
            return validate_template_result

        # add template css in boilerplate\
        css_t_parser_result = self.parse_css(
            templates, page_html, self.TEMPLATES_DIR)

        if not css_t_parser_result:
            utils.return_response(
                {"status": "error", "message": "Internal Error: Unable to parse css"})

        js_t_parser_result = self.parse_js(
            templates, css_t_parser_result, self.TEMPLATES_DIR)

        if not js_t_parser_result:
            utils.return_response(
                {"status": "error", "message": "Internal Error: Unable to parse js"})

        return js_t_parser_result

    def load_template_placeholders(self, templates, template_dir_path):
        """ All templates have a json file which contains all possible placeholders """
        placeholders = {}
        for template in templates:
            placeholder_file_path = os.path.join(
                f"{template_dir_path}template-placeholders/", f"{template}.json")

            try:
                placeholder_json = json.loads(
                    utils.read_file(placeholder_file_path))
            except Exception as e:
                utils.return_response(
                    {"status": "error", "message": f"Unable to load placeholder json file {placeholder_file_path} error: {str(e)}"})

            placeholders[template] = placeholder_json

        return placeholders

    def parse_js(self, templates, page_html, template_dir_path):
        ''' add selected template js to boilerplate '''
        full_js = ""
        for template in templates:
            snippet_path = os.path.join(
                f"{template_dir_path}template-snippets/", f"{template}.html")
            snippet_js = self._parse_from_snippet(
                snippet_path, self.snippet_js_start, self.snippet_js_end)

            if not snippet_js:
                return False

            full_js += "\n" + snippet_js

        return page_html.replace(self.boilerplate_js_placeholder, full_js)

    def parse_css(self, templates, page_html, template_dir_path):
        ''' add selected template css to boilerplate '''

        full_css = ""
        for template in templates:
            snippet_path = os.path.join(
                f"{template_dir_path}template-snippets/", f"{template}.html")
            snippet_css = self._parse_from_snippet(
                snippet_path, self.snippet_css_start, self.snippet_css_end)

            if not snippet_css:
                return False

            full_css += "\n" + snippet_css

        return page_html.replace(self.boilerplate_css_placeholder, full_css)

    def html_template_manager(self, slide, req):
        """ Manages the process of finding and replacing placeholders in html"""

        templates = utils.get_templates_from_req(req)
        placeholders = self.load_template_placeholders(
            templates, self.TEMPLATES_DIR)

        template = slide['template']['value']
        snippet_html = self.get_html_from_template(
            slide, self.TEMPLATES_DIR, req)

        slide_html = utils.apply_placeholders(slide, deepcopy(snippet_html), placeholders[template], self.TEMPLATES_DIR)
        return self.apply_template_class(slide_html, slide)

    def apply_template_class(self, slide_html, slide):
        ''' add css class name same as template name for animations '''
        if "template" in slide and "value" in slide["template"]:
            template_class = slide["template"]["value"]
            return slide_html.replace(self.template_class_placeholder, template_class)
        return slide_html

    def get_html_from_template(self, slide, template_dir_path, req):
        ''' return the snippet html '''
        template = self.choose_template(slide, req)
        snippet_path = os.path.join(
            f"{template_dir_path}template-snippets/", f"{template}.html")
        snippet_html = self._parse_from_snippet(
            snippet_path, self.snippet_html_start, self.snippet_html_end)

        if not snippet_html:
            utils.return_response(
                {"status": "error", "message": f" template: {template} does not have snippet html"})
        return snippet_html

    def choose_template(self, slide, req):
        ''' priority of slide template is higher than global template '''
        slide_template = ""
        if "template" in req:
            slide_template = req["template"]['value']

        if "template" in slide:
            slide_template = slide['template']['value']

        return slide_template

    def apply_html(self, js_result, html_data):
        return js_result.replace(self.boilerplate_html_placeholder, html_data)

    def _parse_from_snippet(self, snippet_path, start_string, end_string):
        snippet_content = ""
        try:
            with open(snippet_path, "r") as f:
                snippet_content = f.read()
        except Exception as e:
            print("Unable to replace snippet", e)
            return False

        find_between_res = self._find_between(
            snippet_content, start_string, end_string)

        if find_between_res == "":
            print("cannot parse the content")
            return False

        return find_between_res

    def _find_between(self, s, first, last):
        try:
            start = s.index(first) + len(first)
            end = s.index(last, start)
            return s[start:end]
        except ValueError:
            return ""
