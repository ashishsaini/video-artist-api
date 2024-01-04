import requests
import json
import utils 

class EmotiVoice:
    
    def __init__(self):
        self.text = ""
        self.voice_id = "92"
    
    def create(self, text, config, filename, diff_duration):
        try:
            emoti_add = utils.get_env("EMOTIVOICE_ADDRESS")
        except Exception as e:
            utils.return_response({
                "status": "error",
                "message": f"EMOTIVOICE_ADDRESS is not set in .env"
            })
            return "" 
        
        url = f"{emoti_add}v1/audio/speech"

        self.text = text
        if config['voice_id']:
            self.voice_id = config["voice_id"]

        payload = json.dumps({
            "input": self.text,
            "voice": self.voice_id,
            "prompt": "A exciting and happy voice",
            "language": "zh_us",
            "model": "emoti-voice",
            "response_format": "mp3",
            "speed": 1
        })
        headers = {
        'accept': 'audio/mp3',
        'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Write the content of the response to a file
            with open(filename, "wb") as file:
                file.write(response.content)
            utils.wlog(f"MP3 file saved as {filename}")
        else:
            utils.wlog(f" Error converting file using emotivoice, check if the server is running ")
            return ""            
        return filename 
        
