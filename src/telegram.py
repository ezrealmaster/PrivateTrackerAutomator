import re
from datetime import datetime

from telethon import TelegramClient, events

import downloadscheduler
from src.trackers.torrentinfo import TorrentInfo
from trackers import TrackerName


class TelegramListener:
    def __init__(self, config):
        api_id = config["api_id"]
        api_hash = config["api_hash"]
        self.client = TelegramClient('anon', api_id, api_hash)

    def add_handler(self, handler):
        self.client.add_event_handler(handler)


@events.register(events.NewMessage(chats=[-1001397490649, "me"]))
async def message_handler_hdolimpo(event):
    url_pattern = r"http://hd-olimpo.club/torrents/(\d+)"
    try:
        torrent_id = re.search(url_pattern, event.raw_text).group(1)
    except AttributeError as e:
        print("Ignoring message:")
        print(event.raw_text)
        return

    name, *properties, uploader, info, link = event.raw_text.splitlines()
    print(f"{name=}")
    print(f"{properties=}")
    print(f"{uploader=}")
    print(f"{info=}")
    print(f"{link=}")
    # Download logic here...
    if "🎖🎖🎖 Premium 🎖🎖🎖" in properties:
        print("Skipping premium torrent.")
        return

    freeleech = 0
    if "🔥🔥🔥 100% Free 🔥🔥🔥" in properties:
        print("Is freeleech")
        freeleech = 100

    doubleup = False
    featured = False
    if "💎💎💎 Doble carga 💎💎💎" in properties:
        doubleup = True
        # Check rss feed for featured
        # featured = featuredrss.search_rss(torrent_id)

    hrless = False
    if "🚨🚨🚨 Sin Hit&Run 🚨🚨🚨" in properties:
        hrless = True

    if freeleech or featured:
        print(f"Downloading torrent {torrent_id}...")
        try:
            size = re.search(r"- (\d+\.\d+) GiB", info).group(1)
        except Exception as e:
            print("Could not match size.")
            size = None
        torrent = TorrentInfo(name=name, tracker=TrackerName.HDOLIMPO, size=size, id=torrent_id, upload_date=datetime.now(),
                              freeleech=freeleech, doubleup=doubleup, featured=featured, hrless=hrless)
        downloadscheduler.new_torrent(torrent)


@events.register(events.NewMessage(chats=[-1001203629747, "me"]))
async def message_handler_torrentland(event):
    print(event.message.entities[0].url)


@events.register(events.NewMessage(chats=[-1001279197242, "me"]))
async def message_handler_xbytesv2(event):
    print(event.message.entities[0].url)