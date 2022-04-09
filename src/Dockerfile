# syntax=docker/dockerfile:1
FROM python:3.10.4-alpine

# Disable python buffering and bytecode *.pyc compiling. 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Project directory.
WORKDIR /srv/www/florgon/auth-api

# Install requirements.
COPY requirements.txt /srv/www/florgon/auth-api/
RUN pip install --upgrade pip
RUN pip install --upgrade --no-cache-dir -r requirements.txt

# Copy whole project.
COPY . /srv/www/florgon/auth-api/