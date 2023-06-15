import os
import time
from datetime import datetime
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup
from discord import Embed, SyncWebhook

from args import parse_arguments

GREEN = 0x00FF00


def retry(retries=3, delay=30, backoff=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            current_delay = delay
            for retry_count in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if retry_count == retries:
                        print(f"Exception: {e}, all retries failed.")
                        return None
                    print(
                        f"Exception: {e}, trying again in {current_delay} seconds. ({retry_count+1}/{retries})"
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

        return wrapper

    return decorator


@retry()
def get_metatags(url: str):
    print(f"Getting metatags for {url}")
    response = requests.get(url)

    if not response.ok:
        print(f"Error: {response.status_code} | {response.reason} Getting metatag.")
        return None

    soup = BeautifulSoup(response.content, "html.parser")
    og_meta_tags = soup.find_all("meta", property=lambda p: p and p.startswith("og:"))

    opengraph_data = {}
    for tag in og_meta_tags:
        property_name = tag.get("property", "").replace("og:", "")
        content = tag.get("content", "")
        if property_name and content:
            opengraph_data[property_name] = content

    return opengraph_data


@retry()
def get_feed(url: str):
    print(f"Getting feed for {url}")
    response = requests.get(url)

    if not response.ok:
        print(f"Error: {response.status_code} | {response.reason} Getting feed.")
        return None

    return ElementTree.fromstring(response.text)


@retry()
def send_webhook(
    webhook: SyncWebhook, embed: dict, username: str = "", avatar_url: str = ""
):
    webhook.send(
        username=username,
        avatar_url=avatar_url,
        embed=Embed.from_dict(embed),
    )
    return True


def main():
    args = parse_arguments()

    username = "Steam RSS Feed"
    steam_icon = "https://cdn.cloudflare.steamstatic.com/valvesoftware/images/about/steam_logo.png"
    webhook = SyncWebhook.from_url(args.webhook)

    feeds = []
    feeds += [f"https://steamcommunity.com/ogg/{appid}/rss/" for appid in args.appid]
    feeds += [f"https://steamcommunity.com/groups/{group}/rss/" for group in args.group]

    while True:
        old_feed = []
        if os.path.exists(args.archive):
            with open(args.archive, "r") as f:
                old_feed = [line.strip() for line in f.readlines()]

        for feed_url in feeds:
            root = get_feed(feed_url)
            if root == None:
                continue
            channel = root.find("channel")

            for item in reversed(list(channel.findall("item"))):
                guid = item.find("guid").text
                if item.find("author") == None or guid in old_feed:
                    continue

                if old_feed != [] or args.force_old:
                    meta_tags = get_metatags(guid)
                    if meta_tags == None:
                        continue

                    embed = {
                        "author": {
                            "name": channel.find("title").text,
                            "url": f"{channel.find('link').text}/announcements",
                            "icon_url": "",  # how to get game icon?
                        },
                        "title": item.find("title").text,
                        "url": guid,
                        "color": GREEN,
                        "description": meta_tags.get("description", ""),
                        "thumbnail": {
                            "url": channel.find("image").find("url").text
                            if channel.find("image") != None
                            else ""
                        },
                        "image": {"url": meta_tags.get("image", "")},
                        "timestamp": datetime.strptime(
                            item.find("pubDate").text,
                            "%a, %d %b %Y %H:%M:%S %z",
                        )
                        .astimezone()
                        .isoformat(),
                    }
                    sent = send_webhook(webhook, embed, username, steam_icon)
                    if sent == None:
                        continue

                with open(args.archive, "a+") as f:
                    f.write(guid + "\n")

        if not args.continuous:
            break

        print(f"Sleeping for {args.interval}")
        time.sleep(args.interval.total_seconds())


if __name__ == "__main__":
    main()
