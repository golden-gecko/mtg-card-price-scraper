FROM python:3.8.1

WORKDIR /usr/local/app

COPY common/requirements.txt .

RUN pip3 install -r requirements.txt

COPY common .
COPY ui .

EXPOSE 80

CMD ["gunicorn", "--bind", "0.0.0.0:80", "--log-level", "debug", "app:app"]
