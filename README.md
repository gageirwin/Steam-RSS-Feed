# Steam RSS Feed
Get notifications for steam games or steam groups RSS Feed with Discord Webhooks.
## Usage
Install requirements
```bash
pip install -r requirements.txt
```
Run application
```bash
python steam_rss.py [OPTIONS] "YOUR DISCORD WEBHOOK URL"
```
## Options
 - `--appid` : Appid of the Steam game whose announcements you want to monitor.
 - `--group` : Name fo the steam group whose announcements you want to monitor. (Must be public.)
 - `--indefinitely` : Indefinitely run the application and check the feed every hour.
## Note
- On the initial run it will send (10) webhooks for all events in the feed.
- All sent events will be recorded in `{appid}_feed.txt` or `{group}_feed.txt` and won't be sent again.