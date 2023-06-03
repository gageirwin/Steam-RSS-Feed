import argparse
import os
import re
from datetime import timedelta


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
    parser = argparse.ArgumentParser(
        description="Have the announcements feed for Steam games and groups sent over Discord webhooks."
    )
    parser.add_argument(
        "--webhook", type=str, required=True, help="Your Discord webhook. (Required)"
    )
    parser.add_argument(
        "--appid",
        type=str,
        nargs="+",
        help="Appid(s) of the Steam game whose announcements you want to monitor.",
        default=[],
    )
    parser.add_argument(
        "--group",
        type=str,
        nargs="+",
        help="Name(s) of the Steam group whose announcements you want to monitor.",
        default=[],
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
