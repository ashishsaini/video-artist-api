import utils
from copy import deepcopy


class Slides:

    def __init__(self) -> None:
        self.slide_max_count = 20

        # duration of slide is more than it should be, reduce slide duration by this offset
        self.DURATION_OFFSET = 100 

    def replace_default_elements(self, request, default_slide):
        ''' replace default_elements passed by the user to slide boilerplate
        which will be copied to all slides '''

        if not "default_elements" in request:
            return default_slide

        new_element = self.fill_defaults(
            request["default_elements"], default_slide)
        return new_element

    def fill_slide(self, slide, default_slide_json):
        """ 
        Inputs: 
            1. A slide with user passed parameters
            2. default_slide_json which contains default values for all slides
        Output:
            Slide which contains user defined with all default values in default_slide_json
        """

        if not slide:
            return default_slide_json

        new_element = self.fill_defaults(slide, default_slide_json)

        return new_element

    def fill_default_settings(self, request, default_settings):
        """ 
        Inputs: 
            1. A slide with user passed parameters
            2. default_slide_json which contains default values for all slides
        Output:
            Slide which contains user defined with all default values in default_slide_json
        """

        if "settings" not in request:
            return default_settings

        new_element = self.fill_defaults(request["settings"], default_settings)
        return new_element

    def update_slide_duration(self, request):
        ''' if delay is added to the elements of a slide then total duration is reduced
            if slide has duration of 5 seconds and 2 elements in it has a delay of 1 seconds each 
            then total duration of the slide should be 3
            this is how revealjs does it

            Process
            Loop through request-> slides
                total_delay = for each slide sum up the duration of all elements
                final_duration = original duration - total_delay 

         '''

        for slide in request['slides']:
            total_delay = 0
            utils.wlog("## Slide , ", slide)
            for key in slide:
                if isinstance(slide[key], list):
                    for item in slide[key]:
                        if "delay" in item:
                            total_delay += item['delay']
                else:
                    if "delay" in slide[key]:
                        total_delay += slide[key]['delay']

            final_duration = int(slide["duration"]["value"]) - total_delay
            if final_duration < 0:
                utils.return_response(
                    {"status": "error", "message": "Sum of delays in an element must be less than slide duration"})

            slide["duration"]["value"] = final_duration - self.DURATION_OFFSET

        return request

    def fill_defaults(self, source, defaults):
        """ 
        Inputs:
            1. source: params passed by the user 
            2. defaults: default values of every element
        Output:
            updated_data with all default values filled in params passed by user

        Note: logic to be updated to use recursive calls, current logic 
                only handles 3 levels in json
        """

        new_element = deepcopy(defaults)
        for key, element in source.items():
            #print("\n ### element >  ", key, element)
            if key in source and key in defaults:

                if isinstance(element, dict):
                    #print("\n dict --> ", element, new_element[key])
                    new_element[key] = self._fill_defaults_parser(
                        element, new_element[key])
                elif isinstance(element, list) and isinstance(new_element[key], list):
                    element_default_data = deepcopy(new_element[key][0])
                    new_element[key] = []
                    for element_item in element:
                        #print("\n list --> ", key,element_item, element_default_data)
                        new_element[key].append(deepcopy(self._fill_defaults_parser(
                            element_item, deepcopy(element_default_data))))
                else:
                    #print("\n plain --> ", key, element)
                    new_element[key] = element

        return new_element

    def _fill_defaults_parser(self, element, element_default_data):
        for key_level_2, value_level_2 in element.items():
            # if key not in element_default_data:
            #     element_default_data = {}

            if isinstance(value_level_2, dict):
                for key_level_3, value_level_3 in value_level_2.items():
                    if key_level_2 not in element_default_data:
                        element_default_data[key_level_2] = {}

                    # print("level 3 -> ", key, key_level_2,key_level_3, value_level_3)
                    element_default_data[key_level_2][key_level_3] = value_level_3
            else:
                # print(element_default_data)
                # print("level2 -->", key,key_level_2, value_level_2)
                element_default_data[key_level_2] = value_level_2

        #print(">>> element_default_data : ", element_default_data)
        return element_default_data
