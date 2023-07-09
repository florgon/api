# syntax=docker/dockerfile:1
FROM python:3.11.4-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /srv/api

RUN apk add build-base
RUN pip install --upgrade pip
COPY requirements.txt /srv/api
RUN pip install --upgrade --no-cache-dir -r requirements.txt

COPY . /srv/api
