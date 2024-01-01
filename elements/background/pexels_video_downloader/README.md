## Pexels Downloader

This is a simple script to download pexels videos when provided the URL of the video, this project uses [Pexels API](https://www.pexels.com/api/documentation/) to download the videos, you need to register and get your API key which is very straight forward. 

This script does following things:

1. Extract `video id` from provided URL
2. Get `video data` from pexels get video API, which returns the different resolutions available for the video.
3. Select the video resolution according to the resolution provided in `resolution`, if required resolution is not available then select the highest resolution (max_resolution configuration also available).
4. Download the video and store it in provided `downloads_dir` 

### Setup

```python
pip install -r requirements.txt
```

### Register with pexels API to get API key and set the API key in environment variable

```bash
export PEXELS_API_KEY="your API key"
```

### For usage check main.py

```python

from pexels_downloader import PexelsDownloader

if __name__ == "__main__":

    pexels_url = "https://www.pexels.com/video/waves-rushing-and-splashing-to-the-shore-1409899/"
    pexels_d = PexelsDownloader("logs/pexels_downloader.log")
    pexels_d.downloads_dir = "downloads/"
    pexels_d.resolution = 1080
    result = pexels_d.download(pexels_url)
    print(result)

```

### You can change some configuration vairables in pexels_downloader.py __init__, some default variables are

```python

# set default resolution of the video to download
self.resolution = 1080

# script will automatically download the best resolution if self.default_res is not available
# self.max_resolution will limit the maximum resolution which can be downloaded 
# in case you do not want 4k 
self.max_resolution = 1440

# API url of pexels API
self.pexels_api_url = "https://api.pexels.com/videos/videos/"

# environnment variable which should be set to make pexels API work
self.pexels_api_key = os.environ.get("PEXELS_API_KEY")

# API timeout for pexels API's, higher because downloading videos
self.timeout = 30

# Directory where the video file will be downloaded
self.downloads_dir = "/tmp/"


```
