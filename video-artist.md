# VIDEO ARTIST

## Create video from Anything

#### AI driven API platform for generating high quality videos

Video artist is an API platform which uses AI to create the video according to content provided by user. Video artist can be used by developers to create applications for many purposes like news, articles to videos, how to videos, product videos (and many more) for platforms like youtube, linkedin, instagram, tiktok etc. 

For developers, Video Artist is an API where you provide minimum information and it will generate an awesome animated video within few seconds. For example, below json can be used send data to video artist and video artist will create a video with background according to keywords ( detected from text ), audio will be automatically generated by human-like best in the class text to speech engine.

```json
{
  "slides": [{
      "audio": {
        "type": "tts",
        "value": "Hi, welcome to video artist."
      },
      "overlay": [{
        "type": "text",
        "value": "Welcome to Video Artist!"
      }]
    }]
}
```

See the result of the above json in below video:

### todo video of above content

Or you can use the python sdk to make things easy.

```python
from video_artist import VideoArtist

# middleware IP, middleware port, Video server IP, video server port
va = VideoArtist("x.x.x.x", "xx", "x.x.x.x", "xx")

va.filename = "video.mp4" # required
va.resolution = {"width": 1080, "height": 1920}
va.fps = 30

# va.add_slide("{keyword for background}", "{text heading}", "{TTS audio}")
va.add_slide("Iphone","Heading of slide 1", "TTS to be played during slide 1")
va.add_slide("macbook","Heading of slide 2", "TTS to be played during slide 2")

# video will be downloaded in provided dir
va.make_video("downloads/")
```

Off course, this is just a demo, video artist provides absolute control over your videos, following are some options:

* Option to pass image or video URL directly. or It can use free media providers like pexels if automated selection of background based on keywords/text is required.

* Option to provide CSS styles for absolute control over text.

* Option to create your own custom template, if you don't like default one's.

* Multiple Option for tuning text to speech, you can change the gender, speaker, speed, emotion, accent etc.  

* You can even pass your own audio recording.

* Option to display multiple text, images or videos in videos.

* Video artist can also summerize the content passed in TTS, this way blog videos can be created with summerized content if the blog is too long.

* Choose from animated design templates and background music available by default. 

  

## Core Components

Video artist uses elements like text, background, TTS etc. Video artist tries to combine the elements passed in API in a smartest possible way to create best possible video. 

#### 1. Video Elements

1. **OVERLAY** - you can use overlay to put any text, image, video over the background, you can create as many overlays as you want:
   1. **Type** overlay can be text, image or video.
   2. **Value** Value of text, image or video. Supports only URLs of image and video.
   3. **Style** Custom valid CSS style for the font.
   4. **Position** Position of the font on screen, it could be top, middle, bottom with optional horizontal alignment like `top-left` or `bottom-right`. 
   5. **Delay** display the text with some delay.
2. **BACKGROUND** - background (Image/ Video/ Color) of the video. Properties of background are:
   1. **Type** background can be image, video or solid color. 
   2. **Value** URL of the image or video, if keywords are not provided.
   3. **Keywords** user can provide a keyword instead of manually entering video or image URL. Video artist's AI will automatically apply the background based upon the keyword. If keywords or background URL is not passed, keywords will be automatically from text or TTS.
   4. **Source** where to fetch the video in case of keywords are provided, sources could be pexels, shutterstock, unsplash, YouTube etc.
3. **AUDIO** user can directly upload an audio file if required or text can be passed to generate TTS. This audio will be played instead of TTS. Properties are:
   1. **Voice_id** name of the voice in case of TTS, voice ID will identify a unique voice among many voices available. It is the combination of gender, region, language, name. complete list of voices are provided [here](http://google.com).
   2. **Type** Audio could be TTS or URL. 
   3. **Value** Text for TTS if type is TTS or URL if type is URL.
   4. **Speed** rate of speaking which defaults to 1, 0.8 means 20% slower and 1.2 means 20% faster.
   5. **Volume** loudness of the TTS speech.
   6. **Language** language of the audio to be played in case of TTS, complete list of voices are provided [here](http://google.com).
4. **MUSIC** background music to be played when video is playing. Properties are:
   1. **Volume** laudness of the music.
5. **TEMPLATE** is a quick way to generate the content, user can provide a template id to use animations and designs available provided by default in Video Artist. 
6. **Duration** of the video can be given in seconds or you can use `based_on` to make it dependent on some other element. for example you can directly assign the value 20 sec, or you can use `based_on : tts` to make the duration of slide based upon length of TTS audio. 

### 2. Video Settings

Settings are those values which can only be provided for whole video. 

1. **TRANSITION** there are few settings like `transition-animation` and `transition-delay` which are very  necessary:
   1. **Transition-animation** could be fade, slide, cube etc.
   2. **Transition-delay** delay between 2 slides (in seconds) to add pause.
2. **VIDEO SETTINGS** users can provide the required resolution, FPS. Properties are:
   1. **Resolution** User can provide the resolution in width and height.
   2. **FPS** frame per seconds can be provided to improve the smoothness of the videos.
   3. **Max duration** maximum duration of the video.

Example of a valid json is provided below:

```json
{
    "settings": {
        "video": {
            "resolution": {
                "height": 1080,
                "width": 1920
            },
            "fps": 30
        },
        "transition": {
            "delay": 2
        }
    },
    "slides": [
        {
            "template": "intro-1",
            "overlay": [{
                "type": "text",
                "value": "HEADING 1",
                "position": "top-left"
            }],
            "background": {
                "value": "",
                "keywords": [
                    "architecture",
                    "buildings"
                ],
                "type": "video",
                "source": "pexels"
            }
        },
        {
            "overlay": [{
                "type": "text",
                "value": "HEADING 2",
                "position": "top-left"
            }],
            "background": {
                "value": "black",
                "type": "solid"
            }
        }
    ]
}
```


### 4. Slides

Video Artist elements defined can be combined together in different ways, slides acts as a container for these elements which needs to be displayed at a particular section of the video. For example if you want to create a video where you want to show a video background, a heading over the video and TTS audio, this can be done by defining them in same slide.

Video artist elements combined with the slides can create many different type of videos:

1. **Text driven** video with multiple slides where backgrounds, Text and TTS changes in every slide.
2. **Audio driven** video where audio is provided by the user and single audio will be played in the whole video with backgrounds provided, Text provided by user.
3. **Video Driven** Video where there is a single video in the background. Text and TTS is created by video artist for the video.

### 4. Data Structure 

All three type of videos can be generated using different elements and slides. The combination of elements and slides can be defined by user in the form of JSON. Structure of JSON is explained below:

```
{
  "{Global Elements}"
  "{Settings}"
  "Slides"
}
```



Some important points regarding conbiniting the elements, settings and slides to form JSON:

* Inside the slides all the combination of elements are valid.
* All of the elements can also be defined in `global_elements` to apply them to full video length. Global elements can be overriden if same element is defined inside a slide. For example if you want template to be `news-1` in all slides, even then first can have a different template if template element is provided in the first slide.
* Video can also be created without `slides` , only using `global_elements` and `settings` will work. 
* Videos can be created without the `global_elements` too, only `settings ` is required. but should contain atleast one of `global_elements` or `slides`.
* Video artist will try to guess the element values based on the parameters provided, for example 
  * If TTS is provided in slide then video artist will automatically set `duration.based_on: tts` if duration element is not provided in  `global_elements` or `slides`.
  * To the small details like, background music will be louder when no TTS is provided, and less louder when TTS or audio is provided.

### 5. Templates

Video Artist makes it easy to apply different type of styles to your videos, templates are created based on the category of the video like news, inspirational, DIY, educational etc. Template will automatically: 

* Change the text properties (like color, size, style, position) for creating beautiful headings and subheadings. Which users can override by defining text properties in global or slide settings.
* Add dynamic javascript animations for text and can also have predefined animated objects like bubbles, snow etc. 

Each template is created with custom CSS and javascript, you can also upload your custom template if you need some custom design.



## Usage Categories

### 1. VIDEO ARTIST AS PLATFORM

Main purpose of video artist to act as a platform where developers can use video artist to create `automated videos` and `manual videos`.  

**Automated Videos**  developers can use video artist for generating automated and great quality video content for youtube, instagram, facebook, etc. Developers can use video artist API / SDK and can integrate platform of their choice with video artist. Some examples are:

* **Content to video** there are many companies which has very good organised content/information related to a particular topic, company can use video artist to generate automated videos from content and increase their presence on social media platforms like youtube, facebook, instagram etc. For example companies like feedspot.com can use thier content to create videos like https://youtu.be/gZGoKbYeqmA or companies like top10.com can generate videos like https://youtu.be/WpjIEi7vxaU. Same thing can be used by e-commerce sites to generate content.
* **Article to video** whenever a new post is created, developers can use voice artist to create the video. It can be done by scraping the blog article, using the voice artist text summerizer if required which will keep only important information from article and images related to blog article can be used as background for video. Similar use cases: companies can use this to create youtube training videos from their blog or wiki, news companies can create videos from articles just published.
* **Music videos ** If you want to create a music channel on youtube, you can also upload the music files to video artist, and provide the keywords for background videos, video artist will generate awesome music videos for you. You can automate this process if you have great selection of music.

You must have got an idea about how awesome video artist can be, it depends on the creativity of the developers on how they use petabytes of information available on the Internet to create videos. Please, do not use copyright material without proper authority, video artist is not responsible for the content you provide.



### 2. VIDEO ARTIST FOR APPLICATIONS

**Manual Videos ** developers can use video artist to create apps for generating videos from content provided by its users. Some of the ideas are:

* **Video Editor App**  create videos by providing the content (text and/or images), developers can use their talent to provide interface for user to choose the background image or videos, users can choose text font, color , position according to requirement. for example developer can create apps like lumen5.com and rephrase.ai.
* **Video Chrome Plugin** Developers can create plugins which can work with different sites like medium, wikipedia, IMDB etc, where users can use the chrome plugin for creating videos from content selected by users.

Developers can create platform for specific needs of the users by providing them new templates designed for specific needs, for example apps can be created for creating product videos, or educational videos with subtitles or architects showing their renders and many more.  