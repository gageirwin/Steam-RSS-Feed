# Steam RSS Feed
Get the RSS Feed of a given steam appid and send a notification with Discord Webhooks.
## Usage
Install requirements
```bash
pip install -r requirements.txt
```
Run application
```bash
python steam_rss.py [OPTIONS] --appid "APPID" "YOUR DISCORD WEBHOOK URL"
```
## Options
 - `--appid` : Appid of the Steam game whose announcements you want to monitor.
 - `--indefinitely` : Indefinitely run the application and check the feed every hour.
## Note
- On the initial run it will send (10) webhooks for all events in the feed.
- All sent events will be recorded in `feed.txt` and won't be sent again.