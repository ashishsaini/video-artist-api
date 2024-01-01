#!/bin/bash

result=`curl -XPOST "http://localhost:7000/generate" -H "Content-Type: application/json" -d '{
    "name": "video name",
    "audio" : "asjdhj092hd092j3.mp3",
    "template": "slides-template-1",
    "slides" :[
        {
            "bg_image": "iphone",
	    "slide_duration": 10,
            "heading": "Should you buy iphone 12?"   
        },
	{
            "bg_image": "mobile apps",
            "slide_duration": 3,
            "heading": "Apple announcing soon"
        }
    ]
}'`

echo "$result"
