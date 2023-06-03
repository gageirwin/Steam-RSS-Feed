# Steam RSS Feed
Have the announcements feed for Steam games and groups sent over Discord webhooks.
## Usage
Install requirements
```bash
pip install -r requirements.txt
```
Run application
```bash
python steam_rss.py [OPTIONS] --webhook "WEBHOOK"
```
## Options
 - `--webhook WEBHOOK` : Your Discord webhook. (Required)
 - `--appid APPID [APPID ...]` : Appid(s) of the Steam game whose announcements you want to monitor.
 - `--group GROUP [GROUP ...]` : Name(s) of the Steam group whose announcements you want to monitor.
 - `--continuous` : Continually check feed(s) based on --interval value. The default --interval is 1 hour.
 - `--interval 0d0h0m0s` : Specify the wait interval in days, hours, minutes, and seconds (e.g., 1d2h30m)
 - `--archive FILE` : Archive file to store previous feed(s) items. Default is `feed.txt` located in the current working directory (cwd).
 - `--force-old` Send webhook notifications when `--archive` file is empty.

## Examples
```bash
python steam_rss.py --appid "593110" --group "SteamClientBeta" --continuous --interval "3h" --webhook "DISCORD_WEBHOOK_URL"
```
Continually check the announcements feed for [Steam News](https://steamcommunity.com/games/593110/announcements) (593110) and [Steam Client Beta](https://steamcommunity.com/groups/SteamClientBeta/announcements) (SteamClientBeta) every 3 hours.
```bash
python steam_rss.py --appid "730" "570"--continuous --interval "1d" --webhook "DISCORD_WEBHOOK_URL"
```
Continually check the announcements feed for [Counter-Strike: Global Offensive](https://steamcommunity.com/games/CSGO/announcements) (730) and [Dota 2](https://steamcommunity.com/games/dota2/announcements) (570) every 1 day.

## Notes
- Using `--force-old` will send previous feed item notifications on **initial run**.