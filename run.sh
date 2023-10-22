#!/bin/bash
xhost +

docker build -t note_labeler -f code/Dockerfile .
#docker run -it --entrypoint bash note_labeler
docker run --rm \
           -e DISPLAY=host.docker.internal:0 \
           -v /tmp/.X11-unix:/tmp/.X11-unix \
           -v ${PWD}/finished_labeling:/usr/src/app/finished_labeling \
           -v ${PWD}/notes_to_label:/usr/src/app/notes_to_label \
           -v ${PWD}:'/app' \
           note_labeler

