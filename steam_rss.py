import argparse
import os
import time
from datetime import datetime
from xml.etree import ElementTree

import requests
from discord import SyncWebhook


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--appid",
        type=str,
        required=True,
        help="Appid of the Steam game whose announcements you want to monitor.",
    )
    parser.add_argument(
        "--indefinitely",
        action="store_true",
        help="Indefinitely run the application and check the feed every hour.",
    )
    parser.add_argument("webhook_url", type=str, help="Discord Webhook")
    return parser.parse_args()


def main():
    args = parse_arguments()

    webhook_avatar_url = "https://cdn.cloudflare.steamstatic.com/valvesoftware/images/about/steam_logo.png"
    webhook = SyncWebhook.from_url(args.webhook_url)

    url = f"https://steamcommunity.com/ogg/{args.appid}/rss/"

    while True:
        old_feed = []
        if os.path.exists("feed.txt"):
            with open("feed.txt", "r") as f:
                old_feed = [line.strip() for line in f.readlines()]

        response = requests.get(url)

        root = ElementTree.fromstring(response.text)
        channel = root.find("channel")

        feed_title = channel.find("title").text

        for item in reversed(list(channel.findall("item"))):
            title = item.find("title").text
            link = item.find("link").text
            date = datetime.strptime(
                item.find("pubDate").text, "%a, %d %b %Y %H:%M:%S %z"
            ).astimezone()

            if title in old_feed:
                continue

            webhook.send(
                username=feed_title,
                avatar_url=webhook_avatar_url,
                content=f"# {title}\n**Posted:** {date.strftime('%a, %b %d, %Y @ %I:%M %p %Z')}\n{link}",
            )
            with open("feed.txt", "a+") as f:
                f.write(title + "\n")

        if args.indefinitely == False:
            break

        print(f"Waiting for next update in 1 hour.")
        time.sleep(3600)


if __name__ == "__main__":
    main()
