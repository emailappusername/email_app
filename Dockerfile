# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /email-analytics-app

COPY requirements.txt .  

RUN pip3 install -r requirements.txt 

COPY main.py . 

COPY dash_app_functions.py . 

COPY /assets . 

EXPOSE 8050

CMD [ "python3", "main.py"]

