FROM python:3.7.4-slim-buster

WORKDIR /usr/local/app

COPY common/requirements.txt .

RUN pip3 install -r requirements.txt

COPY common .
COPY ui .

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--log-level", "debug", "app:app"]
