FROM python:3.8.1

WORKDIR /usr/local/app

COPY common/requirements.txt .

RUN pip3 install -r requirements.txt

COPY common .
COPY scraper_indexer .

CMD ["python3", "app.py"]
