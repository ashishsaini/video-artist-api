## Video middleware

#### It creates the html from the content provided in the API and returns the Url of the html 

## Setup docker

#### Setup enviroment variables in .env file

```
SERVER_ADDRESS=localhost
SERVER_PORT=7070
```

#### Create image 

```bash
docker build .  -t video-middleware:1.0
```

#### Run container

```bash
# for testing
docker run --rm -ti --env-file creds/.env -p 7070:7070 -v $(pwd):/app video-middleware:1.0 /bin/bash

docker run --rm -d --env-file creds/.env --cpus-shares="100"  -p 7000:7000 -v $(pwd):/app video-middleware:1.0
```


#### Run the test.sh script to test

Note: You may need to change the server ip and port in test.sh

```bash
cd scripts
bash test.sh
```

### Pexels API key

If you want Video Artist to select image, video according to content then create a pexels API key. and set it in creds/.env

```yaml
PEXELS_API_KEY=xxxxx
```

### Text to speech

If you also need Text to speech, then you need to create Microsoft TTS key. Documentaion for it [https://docs.merkulov.design/how-to-get-microsoft-azure-tts-api-key/](https://docs.merkulov.design/how-to-get-microsoft-azure-tts-api-key/)

After creating a key set the key in creds/.env and restart container.

```yaml
MICROSOFT_TTS_KEY=xxxx
```




