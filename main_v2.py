from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from preview import Preview
import json
import base64
import os
import utils
from recorder import Recorder

SERVER_ADDRESS, SERVER_PORT = utils.get_server_details()
SERVER_ADD = f"http://{SERVER_ADDRESS}:{SERVER_PORT}/"

app = Flask(__name__)
CORS(app)


@app.route("/")
def get_video_data():
    return "Working!!"


@app.route("/data/<path:subpath>",  methods=['GET'])
def get_slide(subpath):
    '''allow static html slides to be served'''
    return send_from_directory('data/', subpath)


@app.route("/preview", methods=['POST'])
def create_preview():
    '''Receive the configuration of slide and returns the hosted slide url'''
    utils.wlog(json.dumps(request.json))

    preview = Preview(request.json)
    preview_response = preview.process()

    response = {
        "status": "success",
        "slide": SERVER_ADD + preview_response['preview']+"/index.html",
        "audio_file": preview_response['audio_file'] if "http" in preview_response['audio_file'] else  SERVER_ADD + preview_response['audio_file'],
        "video_duration": float(preview_response['video_duration']),
        "output_request": preview_response['data']
    }

    if utils.is_record_video(request.json):
        utils.wlog("recording video...")
        recorder = Recorder(response['output_request']['settings']['video']['resolution'])
        video_path = recorder.record(SERVER_ADD + preview_response['preview']+"/index.html", preview_response['video_duration'], preview_response['audio_file'])
        response['video_url'] = SERVER_ADD + video_path

    # cleanup before returning
    del preview

    utils.wlog(json.dumps(response))
    return json.dumps(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=SERVER_PORT, debug=True)
