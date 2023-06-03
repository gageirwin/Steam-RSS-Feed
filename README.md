# Steam RSS Feed
Get notifications for steam games or steam groups RSS Feed with Discord Webhooks.
## Usage
Install requirements
```bash
pip install -r requirements.txt
```
Run application
```bash
python steam_rss.py [OPTIONS] --webhook WEBHOOK
```
## Options
 - `--webhook WEBHOOK` : Your Discord webhook. (Required)
 - `--appid APPID [APPID ...]` : Appid(s) of the Steam game whose announcements you want to monitor.
 - `--group GROUP [GROUP ...]` : Name(s) of the Steam group whose announcements you want to monitor.
 - `--continuous` : Continually check feed(s) based on --interval value. The default --interval is 1 hour.
 - `--interval 0d0h0m0s` : Specify the wait interval in days, hours, minutes, and seconds (e.g., 1d2h30m)
 - `--archive FILE` : Archive file to store previous feed(s) items. Default is `feed.txt` located in the current working directory (cwd).
 - `--force-old` Send webhook notifications when --archive file is empty.

## Notes
- Using `--force-old` will send previous feed item notifications on **initial run**.