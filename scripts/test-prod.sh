#!/bin/bash

result=`curl -XPOST "http://52.68.16.121:7000/generate" -H "Content-Type: application/json" -d '{
    "name": "video name",
    "audio" : "asjdhj092hd092j3.mp3",
    "template": "slides-template-2",
    "slides" :[
        {
            "bg_image": " https://cdn.wallpaper.com/main/styles/responsive_1680w_scale/s3/_a7r7466-hdr_hundven-clements_photography.jpg",
            "tts_text": "{text to play tts}",
            "heading": "Architecture is a way to show creativity"   
        },
        {
            "bg_image": "https://cdn.wallpaper.com/main/styles/wp_extra_large/s3/03_exterior_cadria_goula.jpg",
            "tts_text": "{text to play tts}",
            "heading": "Every building has a unique story"   
        },
        {
            "bg_image": " https://cdn.wallpaper.com/main/styles/responsive_1680w_scale/s3/_a7r7466-hdr_hundven-clements_photography.jpg",
            "tts_text": "{text to play tts}",
            "heading": "Be an architect, make your world"   
        }
    ]
}'`

echo "$result"

slide_url=`echo "$result" | jq '.result'`

video_url=`curl -XPOST "http://52.68.16.121:5000/create_video" -H "Content-Type: application/json" -d '{
    "url": '"${slide_url}"',
    "resolution": {
        "width": 1920,
        "height": 1080
    },
    "fps": 30,
    "duration": 15,
    "filename": "video-30fps-2.mp4"
}'`

`wget "${video_url}"`