#!/bin/bash

result=`curl -XPOST "http://localhost:7000/generate" -H "Content-Type: application/json" -d '{
    "name": "video name",
    "audio" : "asjdhj092hd092j3.mp3",
    "template": "drop-animation",
    "slides" :[
        {
            "bg_image": "beach",
            "tts_text": "this is text from voice artists, this will create videos",
            "heading": "beaches are awesome"
        },
	    {
            "bg_image": "sea",
            "tts_text": "wow good happy and mad , this is fun",
            "heading": "top 10 best beaches in the world",
            "template": "bubble-animation"
        },
        {
            "bg_image": "nature",
            "tts_text": "this is new tts text ",
            "heading": "do you want to visit it?"
        }
    ]
}'`

echo "$result"
