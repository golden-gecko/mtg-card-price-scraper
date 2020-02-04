FROM python:3.8.1

WORKDIR /usr/local/app

COPY common/requirements.txt .

RUN pip3 install -r requirements.txt

COPY api .
COPY common .

EXPOSE 7000

CMD ["gunicorn", "--bind", "0.0.0.0:7000", "--log-level", "debug", "app:app"]
