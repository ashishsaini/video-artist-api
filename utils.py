from copy import deepcopy
import json
import time
import os
import subprocess
import requests
from urllib.parse import urlparse
import os
from flask import jsonify, abort

def wlog(level="notice", msg=""):
    print(level, msg)


def get_server_details():
    '''get API server env variables'''
    try:
        SERVER_ADDRESS = os.environ['SERVER_ADDRESS']
        SERVER_PORT = os.environ['SERVER_PORT']
    except Exception as e:
        wlog("required env variables are not set, check .env file")
        exit()

    return SERVER_ADDRESS, SERVER_PORT


def get_env(env_var):
    try:
        return os.environ[env_var]
    except Exception as e:
        return_response(
            {"status": "error", "message": f"ENV: {env_var} not found. exiting..."})
        return False


def load_json_structure(path):
    try:
        file_data = json.loads(read_file(path))
        if not file_data:
            return False
    except Exception as e:
        wlog("error", f"Unable to open file {path}, {e}")
        return_response(
            {"status": "error", "message": f"Unable to open file {path}, {e}"})

    return file_data


def read_file(filename):
    try:
        with open(filename, "r") as f:
            file_data = f.read()
    except Exception as e:
        wlog("error", str(e))
        return False

    return file_data


def write_file(filename, data):
    try:
        with open(filename, "w") as f:
            f.write(data)
    except Exception as e:
        wlog("error", str(e))
        return False
    return True


def run_sox(sox_input, filename):
    try:
        cmd = 'sox ' + sox_input + " " + filename
        wlog("Running sox command : "+cmd)
        os.system(cmd)
    except Exception as e:
        wlog("concat file, check sox")
        return_response(
            {"status": "error", "message": f"concat file, check sox"}
        )


def download_file(url, dir):
    path = ""
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            path = os.path.join(dir,
                                os.path.basename(urlparse(url).path))
            with open(path, 'wb') as f:
                for chunk in r:
                    f.write(chunk)
    except Exception as e:
        wlog("error", f"Unable to download file {url}, {e}")
        return_response(
            {"status": "error", "message": f"Unable to download file {url}, {e}"})

    return path


def get_duration(filename):
    # if file is a url, download it
    if filename.startswith("http"):
        wlog("info", f"Downloading file {filename}")
        filename = download_file(filename, "/tmp")

    wlog("info", f"Getting duration of file {filename}")
    if os.path.exists(filename):
        try:
            wlog("running command", "timeout 5s soxi -D "+filename)
            result = subprocess.run(['timeout','5s','soxi', '-D', filename], stdout=subprocess.PIPE).stdout.decode('utf-8')
            if not result:
                result = subprocess.run(['timeout','5s','soxi', '-D', filename], stdout=subprocess.PIPE).stdout.decode('utf-8')
            duration = result.strip()
            wlog("command output: ", duration)
            
            wlog("command completed", " timeout 5s soxi -D "+filename)
        except Exception as e:
            wlog("unable to check the duration of file check sox")
            exit()
    else:
        wlog(f"Audiofile does not exists {filename}")
        return 0.0
    return int(float(duration)*1000)


def remove_file(path):
    try:
        os.remove(path)
    except Exception as e:
        wlog("error", f"Unable to remove file {path}, {e}")
        return False
    return True


def elements_validate_default_helper(request, required_keys, class_key):
    # check if required keys exists in global elements
    if "default_elements" in request:
        if class_key in request['default_elements']:
            for key in required_keys:
                if key not in request['default_elements'][class_key]:
                    return_response(
                        {"status": "error", "message": f"Required keys { ','.join(required_keys)} not found in request -> default_elements -> {class_key}"})

    return {}


def elements_validate_global_helper(request, required_keys, class_key):
    # check if required keys exists in global elements
    if "global_elements" in request:
        if class_key in request['global_elements']:
            for key in required_keys:
                if key not in request['global_elements'][class_key]:
                    return_response(
                        {"status": "error", "message": f"Required keys { ','.join(required_keys)} not found in request -> global_elements -> {class_key}"})

    return {}


def elements_validate_slides_helper(request, required_keys, class_key):
    # check if required keys exists in all elements in slides
    if "slides" in request:
        for slide in request["slides"]:
            if class_key in slide:
                for key in required_keys:
                    if key not in slide[class_key]:
                        return_response(
                            {"status": "error", "message": f"Required keys { ','.join(required_keys)} not found in request -> slides -> {class_key}"})

    return {}


def get_templates_from_req(req):
    ''' Gets unique templates from all slides '''
    templates = []

    for slide in req['slides']:
        if 'template' in slide and slide['template']['value'] not in templates:
            templates.append(slide['template']['value'])

    return templates


def validate_templates(templates, template_path):
    """ Check if the template snippet exists """
    if not templates:
        return_response(
            {"status": "error", "message": f"pass atleast 1 template"})

    for template in templates:
        if not os.path.exists(os.path.join(f"{template_path}template-snippets/", f"{template}.html")) \
                or not os.path.exists(os.path.join(f"{template_path}template-placeholders/", f"{template}.json")):
            return_response(
                {"status": "error", "message": f"template {template} does not exist."})

    return {"status": "success"}


def return_response(response_data):
    print(json.dumps(response_data))
    
    response = jsonify(response_data)
    status_code = 400
    if "status_code" in response_data:
        status_code = response_data["status_code"]
    response.status_code = status_code
    abort(response)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception as e:
        return False


def apply_placeholders(slide, snippet_html, placeholders, template_path=""):
    """
    Placeholders are static and dynamic

    Static placeholders are non-overlays
    Dynamic placeholders are overlays like text, image, video 

    """
    snippet_html = apply_static_placeholders(slide, snippet_html, placeholders)

    # dynamic placeholders
    if "dynamic" in placeholders:
        snippet_html = apply_dynamic_placeholders(
            slide, snippet_html, placeholders, template_path)

    return snippet_html


def apply_static_placeholders(slide, snippet_html, placeholders):
    '''
    for static placeholders:
    Replce all the placeholders for a template
    1. for every placeholder
        a. check if placeholder exists in snippet_html
        b. map the placeholder mapping with the slide and load the value
        c. replace the loaded value in the snippet_html
    '''

    for key, placeholder in placeholders["static"].items():

        if key in snippet_html:
            # heading.value = [heading][value]
            mapping_keys = placeholder["mapping"].split(".")
            placeholder_value = placeholders_mapper(mapping_keys, slide)

            if not placeholder_value and "default" in placeholder:
                # user has not passed param , so applying default value supplies in snippet json
                placeholder_value = placeholder['default']
            elif not placeholder_value:
                placeholder_value = ""

            snippet_html = snippet_html.replace(key, str(placeholder_value))

    return snippet_html


def apply_dynamic_placeholders(slide, snippet_html, placeholders, template_path):
    '''
    for dynamic placeholders:
    1. for every placeholder
        a. check if placeholder exists in snippet_html
        b. map the placeholder mapping with the slide and load the value
        c. replace the loaded value in the snippet_html
    '''

    overlay_elements_placeholder = "__overlay_elements_html__"

    overlay_elements_html = ""

    for element in slide["overlay"]:

        for key, placeholder in placeholders["dynamic"].items():

            if key == element["type"]:
                # if element type matches with placeholder type
                # e.g. slide["overlay"][0]["type"] = placeholder["dynamic"]["text"]
                element_snippet = read_file(os.path.join(
                    f"{template_path}element-snippets/", f"{element['type']}.html"))

                element_final_data = ""
                for element_key, element_placeholder in placeholder.items():
                    if element_key in element_snippet:
                        mapping_keys = element_placeholder["mapping"].split(
                            ".")
                        placeholder_value = placeholders_mapper(
                            mapping_keys, {key: element})
                        element_snippet = element_snippet.replace(
                            element_key, str(placeholder_value))

                        element_final_data = element_snippet

                overlay_elements_html += "\n\n"+element_final_data

    snippet_html = snippet_html.replace(
        overlay_elements_placeholder, overlay_elements_html)

    return snippet_html


def placeholders_mapper(mapping_keys, slide):
    """ Convert placeholder list [heading, value] to specific key [heading][value]
    and returns the value of config"""

    mapper_data = slide
    result = {}
    for key in mapping_keys:
        if key not in mapper_data:
            # user has not passed the param so passing default value
            wlog(f"Key {key} not found in mapping data {mapper_data}")
            return False

        result = mapper_data[key]
        if isinstance(result, dict):
            mapper_data = result
        else:
            param_value = result

    return param_value


def get_element_by_type(slide, mapping_keys, type):
    '''
    Select element from list with given type
    this is helpful when an element is provided as a list like text or overlay
    in these cases we need to find the element from the list with matching type

    Return: element from list, mapping changed to inner level

    '''

    element_name = mapping_keys[0]

    selected_element = {}
    if element_name in slide:
        for element_item in slide[element_name]:
            #print(element_item, slide[element_name])
            if type == element_item['type']:
                selected_element = element_item

    # because the first mapping is name of element
    new_mapping = mapping_keys[1:]

    return selected_element, new_mapping


def is_record_video(request):
    if "settings" in request:
        if "record_video" in request["settings"] and request["settings"]["record_video"] == True:
            return True
    return False
