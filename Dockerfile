FROM python:slim

RUN mkdir /app
COPY / /app

RUN mkdir /feeds
VOLUME /feeds

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python","steam_rss.py", "--archive=/feeds/feed.txt"]