import argparse
import os
import re
import time
from datetime import datetime, timedelta
from xml.etree import ElementTree

import requests
from discord import Embed, SyncWebhook


def validate_archive(path):
    if not os.path.exists(os.path.dirname(path)):
        raise argparse.ArgumentTypeError(
            f"Invalid path: Directory {os.path.dirname(path)} does not exist."
        )
    return path


def parse_time_interval(value):
    pattern = (
        r"^((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?$"
    )
    match = re.match(pattern, value)
    if not match:
        raise argparse.ArgumentTypeError(
            "Invalid time interval format. Please provide a valid interval (e.g., 1d2h30m)"
        )

    groups = match.groupdict()
    time_dict = {key: int(value) for key, value in groups.items() if value is not None}

    return timedelta(**time_dict)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--webhook", type=str, required=True, help="Your Discord webhook. (Required)"
    )
    parser.add_argument(
        "--appid",
        type=str,
        nargs="+",
        help="Appid(s) of the Steam game whose announcements you want to monitor.",
    )
    parser.add_argument(
        "--group",
        type=str,
        nargs="+",
        help="Name(s) of the Steam group whose announcements you want to monitor.",
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Continually check feed(s) based on --interval value. The default --interval is 1 hour.",
    )
    parser.add_argument(
        "--interval",
        type=parse_time_interval,
        metavar="0d0h0m0s",
        help="Specify the wait interval in days, hours, minutes, and seconds (e.g., 1d2h30m)",
        default=timedelta(hours=1),
    )
    parser.add_argument(
        "--archive",
        metavar="FILE",
        type=validate_archive,
        help="Archive file to store previous feed(s) items. Default is feeds.txt located in the current working directory (cwd).",
        default=os.path.join(os.getcwd(), "feed.txt"),
    )
    parser.add_argument(
        "--force-old",
        action="store_true",
        help="Send webhook notifications when --archive file is empty.",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_arguments()

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
            print(f"Getting feed for {feed_url}")
            response = requests.get(feed_url)

            if not response.ok:
                print(f"Error: {response.status_code} | {response.reason} Getting feed")
                embed_dict = {
                    "author": {
                        "name": "Steam RSS Feed",
                        "url": feed_url,
                        "icon_url": steam_icon,
                    },
                    "title": f"Error: {response.status_code} | {response.reason}",
                    "description": f"{feed_url}",
                    "color": 0xFF0000,
                }
                webhook.send(
                    username="Steam RSS Feed",
                    avatar_url=steam_icon,
                    embed=Embed.from_dict(embed_dict),
                )
                continue

            root = ElementTree.fromstring(response.text)
            channel = root.find("channel")

            feed_title = channel.find("title").text

            for item in reversed(list(channel.findall("item"))):
                guid = item.find("guid").text
                if guid in old_feed:
                    continue

                title = item.find("title").text
                link = item.find("link").text
                date = datetime.strptime(
                    item.find("pubDate").text, "%a, %d %b %Y %H:%M:%S %z"
                ).astimezone()

                if old_feed != [] or args.force_old:
                    webhook.send(
                        username=feed_title,
                        avatar_url=steam_icon,
                        content=f"# {title}\n**Posted:** {date.strftime('%a, %b %d, %Y @ %I:%M %p %Z')}\n{link}",
                    )
                with open(args.archive, "a+") as f:
                    f.write(guid + "\n")

        if not args.continuous:
            break

        print(f"Sleeping for {args.interval}")
        time.sleep(args.interval.total_seconds())


if __name__ == "__main__":
    main()
