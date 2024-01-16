## Video Artist

#### Smart and simple API for generating automated videos

Video Artist is an API platform that uses AI to create the video according to content provided by the user. Video artist can be used by developers to create applications for many purposes like news, articles to videos, how-to videos, product videos (and many more) for platforms like youtube, linkedin, instagram, tiktok etc. 


![video-artist-recording](https://github.com/ashishsaini/video-artist-api/assets/5359237/ef3bba3c-6502-4dae-8a16-10b8c58573b9)


### Clone the repo

```bash
git clone git@github.com:ashishsaini/video-artist-api.git
```

#### Setup enviroment variables in creds/.env file

```
SERVER_ADDRESS=localhost
SERVER_PORT=7070
```

### Pexels API key (required)

If you want Video Artist to select image, video according to content then create a pexels API key. and set it in creds/.env

```yaml
PEXELS_API_KEY=xxxxx
```

Pexels setup is currently required as video artist is made to do automated background selection based on keywords passed in the text. 

### Text to speech (Optional)

If you also need Text to speech, then you need to create Microsoft TTS key. Documentaion for it [https://docs.merkulov.design/how-to-get-microsoft-azure-tts-api-key/](https://docs.merkulov.design/how-to-get-microsoft-azure-tts-api-key/)

After creating a key set the key in creds/.env and restart container.

```yaml
MICROSOFT_TTS_KEY=xxxx
```


## Setup docker


#### Create docker image 

```bash
docker build .  -t video-artist:latest
```


#### Run container

```bash
docker run --rm -d --env-file creds/.env  -p 7070:7070 -v $(pwd):/app video-artist:latest
```

### Sample Request

Use this curl request to check if everything is working fine.

```bash
curl --location 'http://127.0.0.1:7070/preview' --header 'Content-Type: application/json' --data '{"slides": [{"overlay": [{"type": "text", "value": "Welcome to video artist"}]}]}'
```

This should return a json with ```slide``` and background automatically seleted using pexels. For full Documentation visit [Docs](https://github.com/ashishsaini/video-artist-api/blob/main/video-artist.md).

Note: this is not a production ready project, use in production at your own risk 


