FROM python:3.7.4-slim-buster

WORKDIR /usr/local/app

COPY common/requirements.txt .

RUN pip3 install -r requirements.txt

COPY api .
COPY common .
COPY tools .
