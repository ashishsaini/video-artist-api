#!/bin/bash

docker run --rm -ti --env-file creds/.env  -p 7000:7000 -v $(pwd):/app video-middleware:1.0 /bin/bash
