#!/bin/bash

result=`curl -XPOST "http://localhost:7000/generate" -H "Content-Type: application/json" -d '{
    "name": "video name",
    "audio" : "asjdhj092hd092j3.mp3",
    "template": "slides-template-3",
    "slides" :[
        {
            "bg_image": "https://stat1.bollywoodhungama.in/wp-content/uploads/2016/03/Taapsee-Pannu-34.jpg",
            "tts_text": " National Icon Taapsee Pannu has been basking in glory with her back-to-back hits.  After working for more than a decade in Indian Cinema, Taapsee adds another milestone in her career, as she launches her production house Outsiders Films.",
            "heading": "<span style=\"-webkit-text-stroke-width: 3px; -webkit-text-stroke-color: #eee; color:red; font-size:80px;\">Taapsee Pannu announces her production house CALLED outsider films</span>"   
        },
        {
            "bg_image": "https://stat1.bollywoodhungama.in/wp-content/uploads/2016/03/Taapsee-Pannu-003.jpg",
            "tts_text": "For Outsiders Films, she has joined forces with Pranjal Khandhdiya who is a content creator and producer for over 20 years.  He has been involved in the production of renowned films",
            "heading": "<span style=\"font-size:80px;\"> For Outsiders Films, she has joined forces with Pranjal Khandhdiya </span> "   
        },
        {
            "bg_image": "https://stat1.bollywoodhungama.in/wp-content/uploads/2016/03/Taapsee-Pannu-1-1.jpg",
            "tts_text": " Having my business ventures, management comes naturally to me.  Hence, I always thought of setting my own production house. The audience and the industry have given me a lot of support and love over the 11 years of my career.",
            "heading": "<span style=\"font-size:80px;\"> I am thrilled to embark upon this new journey </span>"   
        }
    ]
}'`

echo "$result"
