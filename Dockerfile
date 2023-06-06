FROM python:slim

RUN mkdir /app
COPY README.md /app
COPY args.py /app
COPY steam_rss.py /app
COPY requirements.txt /app

RUN mkdir /feeds
VOLUME /feeds

WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python","steam_rss.py", "--archive=/feeds/feed.txt"]