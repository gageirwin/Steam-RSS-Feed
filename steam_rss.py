import argparse
import os
import time
from datetime import datetime
from xml.etree import ElementTree

import requests
from discord import Embed, SyncWebhook


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

    steam_icon = "https://cdn.cloudflare.steamstatic.com/valvesoftware/images/about/steam_logo.png"
    webhook = SyncWebhook.from_url(args.webhook_url)

    rss_url = f"https://steamcommunity.com/ogg/{args.appid}/rss/"

    feed_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "feed.txt")
    print(feed_file)
    while True:
        old_feed = []
        if os.path.exists(feed_file):
            with open(feed_file, "r") as f:
                old_feed = [line.strip() for line in f.readlines()]

        response = requests.get(rss_url)

        if not response.ok:
            embed_dict = {
                "author": {
                    "name": "Steam RSS Feed",
                    "url": rss_url,
                    "icon_url": steam_icon,
                },
                "title": f"Error: {response.status_code} | {response.reason}",
                "color": 0xFF0000,
            }
            webhook.send(
                username="Steam RSS Feed",
                avatar_url=steam_icon,
                embed=Embed.from_dict(embed_dict),
            )
            quit()

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
                avatar_url=steam_icon,
                content=f"# {title}\n**Posted:** {date.strftime('%a, %b %d, %Y @ %I:%M %p %Z')}\n{link}",
            )
            with open(feed_file, "a+") as f:
                f.write(title + "\n")

        if args.indefinitely == False:
            break

        print(f"Waiting for next update in 1 hour.")
        time.sleep(3600)


if __name__ == "__main__":
    main()
