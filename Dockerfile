FROM --platform=linux/amd64 python:3.8-slim-buster

RUN  apt-get update && apt-get install -y build-essential python3-dev sox libsox-fmt-mp3 git wget

# playwrite dependencies
RUN apt-get install -y libglib2.0-0 libnss3 libnspr4 libdbus-1-3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 ffmpeg

RUN pip install git+https://github.com/LIAAD/yake

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

RUN pip install pytest-playwright

RUN playwright install chrome

CMD [ "python", "main_v2.py"]