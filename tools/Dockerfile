FROM python:3.8.1

WORKDIR /usr/local/app

COPY common/requirements.txt .

RUN pip3 install -r requirements.txt

COPY api .
COPY common .
COPY tools .
