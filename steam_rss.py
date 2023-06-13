import os
import time
import traceback
from datetime import datetime
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup
from discord import Embed, SyncWebhook

from args import parse_arguments

RED = 0xFF0000
GREEN = 0x00FF00


def get_opengraph_meta_tags(url):
    response = requests.get(url)

    soup = BeautifulSoup(response.content, "html.parser")
    og_meta_tags = soup.find_all("meta", property=lambda p: p and p.startswith("og:"))

    opengraph_data = {}
    for tag in og_meta_tags:
        property_name = tag.get("property", "").replace("og:", "")
        content = tag.get("content", "")
        if property_name and content:
            opengraph_data[property_name] = content

    return opengraph_data


def main():
    args = parse_arguments()

    username = "Steam RSS Feed"
    steam_icon = "https://cdn.cloudflare.steamstatic.com/valvesoftware/images/about/steam_logo.png"
    webhook = SyncWebhook.from_url(args.webhook)

    max_retries = 10
    wait_time = 30

    feeds = []
    feeds += [f"https://steamcommunity.com/ogg/{appid}/rss/" for appid in args.appid]
    feeds += [f"https://steamcommunity.com/groups/{group}/rss/" for group in args.group]

    while True:
        old_feed = []
        if os.path.exists(args.archive):
            with open(args.archive, "r") as f:
                old_feed = [line.strip() for line in f.readlines()]

        for feed_url in feeds:
            retries = 0
            while True:
                try:
                    print(f"Getting feed for {feed_url}")
                    response = requests.get(feed_url)

                    if not response.ok:
                        print(
                            f"Error: {response.status_code} | {response.reason} Getting feed"
                        )
                        embed_dict = {
                            "author": {
                                "name": username,
                                "icon_url": steam_icon,
                            },
                            "title": f"Error: {response.status_code} | {response.reason}",
                            "description": f"{feed_url}",
                            "color": RED,
                        }
                        webhook.send(
                            username=username,
                            avatar_url=steam_icon,
                            embed=Embed.from_dict(embed_dict),
                        )
                        continue

                    root = ElementTree.fromstring(response.text)
                    channel = root.find("channel")

                    feed_title = channel.find("title").text
                    feed_link = channel.find("link").text
                    game_thumbnail = ""
                    if channel.find("image") != None:
                        game_thumbnail = channel.find("image").find("url").text

                    for item in reversed(list(channel.findall("item"))):
                        guid = item.find("guid").text
                        author = item.find("author")
                        if author == None or guid in old_feed:
                            continue

                        meta_tags = get_opengraph_meta_tags(guid)

                        date = datetime.strptime(
                            item.find("pubDate").text, "%a, %d %b %Y %H:%M:%S %z"
                        ).astimezone()

                        embed = {
                            "author": {
                                "name": feed_title,
                                "url": f"{feed_link}/announcements",
                                "icon_url": "",
                            },
                            "title": item.find("title").text,
                            "url": guid,
                            "color": GREEN,
                            "description": meta_tags.get("description", ""),
                            "thumbnail": {"url": game_thumbnail},
                            "image": {"url": meta_tags.get("image", "")},
                            "timestamp": date.isoformat(),
                        }

                        if old_feed != [] or args.force_old:
                            webhook.send(
                                username=username,
                                avatar_url=steam_icon,
                                embed=Embed.from_dict(embed),
                            )

                        with open(args.archive, "a+") as f:
                            f.write(guid + "\n")
                    continue
                except requests.exceptions.ReadTimeout as e:
                    retries += 1
                    if retries > max_retries:
                        print("All retires failed.")
                        embed_dict = {
                            "author": {
                                "name": username,
                                "icon_url": steam_icon,
                            },
                            "title": "Error: requests.exceptions.ReadTimeout",
                            "description": f"All retries failed.\n{feed_url} has been skipped.",
                            "color": RED,
                        }
                        webhook.send(
                            username=username,
                            avatar_url=steam_icon,
                            embed=Embed.from_dict(embed_dict),
                        )
                        break
                    print("Error occurred:", e)
                    print(
                        f"Retrying in {wait_time*retries} seconds. ({retries}/{max_retries})"
                    )
                    time.sleep(wait_time * retries)

        if not args.continuous:
            break

        print(f"Sleeping for {args.interval}")
        time.sleep(args.interval.total_seconds())


if __name__ == "__main__":
    main()
