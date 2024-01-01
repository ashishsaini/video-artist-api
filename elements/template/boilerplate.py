import json
import os
import shutil
import utils
import uuid
from copy import deepcopy

class Boilerplate:

    def __init__(self):
        # access base templates
        self.TEMPLATES_DIR = os.getcwd()+"/templates/"

        # path where copy of boilerplate will be stored
        self.TEMPLATES_TMP = os.getcwd()+"/data/"
        self.TEMPLATES_TMP_REL = "data/"
        self.TEMPLATES_TMP_PATH = os.getcwd()+"/data/path/"
        self.TEMPLATES_TMP_PATH_REL = "data/path/"
        

    def copy_boilerplate(self, boilerplate="boilerplate"):
        ''' Copy the boilerplate to tmp directory for edits '''

        # create boilerplate dir which is linked to css and js files in templates
        base_boilerplate_dir = self.TEMPLATES_TMP + boilerplate
        if not os.path.isdir(base_boilerplate_dir):
            shutil.copytree(self.TEMPLATES_DIR+"/boilerplate", os.path.join(self.TEMPLATES_TMP,  "boilerplate"))

        preview_dir = str(uuid.uuid4())
        try:
            # create dir named with preview_dir in path
            utils.wlog("info", f"Creating dir {os.path.join(self.TEMPLATES_TMP_PATH,  preview_dir)}")
            os.mkdir(os.path.join(self.TEMPLATES_TMP_PATH,  preview_dir))
            # copy boilerplate to preview_dir
            html_path =  os.path.join(base_boilerplate_dir, "index.html")
            utils.wlog("info", f"html path {html_path}")
            utils.wlog("info", f"copying {html_path} to {os.path.join(self.TEMPLATES_TMP_PATH,  preview_dir)}")
            shutil.copy(html_path, os.path.join(self.TEMPLATES_TMP_PATH,  preview_dir))
        except Exception as e:
            msg = "Unable to copy boilerplate internal error" + str(e)
            utils.wlog("error", msg)
            utils.return_response( {"status": "error", "message": "Internal Error: Unable to copy boilerplate"} )

        return os.path.join(self.TEMPLATES_TMP_PATH_REL,  preview_dir)


    def apply_boilerplate_placeholders(self,  html_path, request):
        """ Replace boilerplate variables with settings passed in params """

        boilerplate_file = html_path+"/index.html"
        boilerplate_html = utils.read_file(boilerplate_file)
        if not boilerplate_html:
            utils.return_response({"status": "error", "message": f"Unable to read file {boilerplate_file}"})

        placeholders = self._load_boilerplate_placeholders(html_path)
        boilerplate_html =  utils.apply_placeholders(request, boilerplate_html, placeholders)

        write_response = utils.write_file(boilerplate_file, boilerplate_html)
        if not write_response:
            utils.return_response({"status": "error", "message": f"Unable to write file {boilerplate_file}"})

        return True


    def _load_boilerplate_placeholders(self, template_dir_path):
        """ All templates have a json file which contains all possible placeholders """
        
        placeholder_file_path = os.path.join(
            f"{self.TEMPLATES_TMP}", "boilerplate","boilerplate_placeholders.json" )

        try:
            placeholders = json.loads(utils.read_file(placeholder_file_path))
        except Exception as e:
            utils.return_response({"status": "error", "message": f"Unable to load placeholder json file {placeholder_file_path} error: {str(e)}"})
        
        return placeholders