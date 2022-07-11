# syntax=docker/dockerfile:1

FROM python:3.9-slim-bullseye

WORKDIR /app

RUN apt update -y && apt install -y git
COPY requirements.txt requirements.txt
RUN pip3 install -r ./requirements.txt
COPY vesta vesta
COPY entrypoint.sh entrypoint.sh
ENV LOGGING_LEVEL=20

ENTRYPOINT entrypoint.sh