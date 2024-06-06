import logging as log
import re
from datetime import datetime

from telethon import TelegramClient, events

from initialized_variables import initialized_trackers
from trackers import TrackerName, TorrentInfo
import downloadscheduler
from src.utils import gib_to_bytes, mib_to_bytes


class TelegramListener:
    def __init__(self, config):
        api_id = config["api_id"]
        api_hash = config["api_hash"]
        self.client = TelegramClient('anon', api_id, api_hash)

    def add_handler(self, handler):
        self.client.add_event_handler(handler)


@events.register(events.NewMessage(chats=[-1001397490649]))
async def message_handler_hdolimpo(event):
    url_pattern = r"http://hd-olimpo.club/torrents/(\d+)"
    try:
        torrent_id = re.search(url_pattern, event.raw_text).group(1)
    except AttributeError as e:
        log.info("Ignoring message:")
        log.info(event.raw_text)
        return

    name, *properties, uploader, info, link = event.raw_text.splitlines()
    log.info(f"{name=}")
    log.info(f"{properties=}")
    # Download logic here...
    if "🎖🎖🎖 Premium 🎖🎖🎖" in properties:
        log.info("Skipping premium torrent.")
        return

    freeleech = 0
    if "🔥🔥🔥 100% Free 🔥🔥🔥" in properties:
        log.info("Is freeleech")
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
        log.info(f"Downloading torrent {torrent_id}...")
        try:
            match = re.search(r"- (\d+\.\d+) (GiB|MiB)", info)
            size = float(match.group(1))
            unit = match.group(2)
            if unit == "GiB":
                size = gib_to_bytes(size)
            else:
                size = mib_to_bytes(size)
        except Exception as e:
            log.warning("Could not match size.")
            size = None
        torrent = TorrentInfo(name=name, tracker=TrackerName.HDOLIMPO, size=size, id=torrent_id, upload_date=datetime.now(),
                              freeleech=freeleech, doubleup=doubleup, featured=featured, hrless=hrless)
        downloadscheduler.new_torrent(torrent)


@events.register(events.NewMessage(chats=[-1001203629747]))
async def message_handler_torrentland(event):
    url_pattern = r"https://torrentland.li/torrents/(\d+)"
    try:
        torrent_id = re.search(url_pattern, event.text).group(1)
    except AttributeError as e:
        log.info("Ignoring message:")
        log.info(event.raw_text)
        return

    name, *stuff, info, _, discounts, _, uploader, _, link = event.raw_text.splitlines()
    log.info(f"{name=}")
    log.info(f"{discounts=}")
    # Download logic here...
    freeleech = 0
    if "🏅 100% Free " in discounts:
        log.info("Is freeleech")
        freeleech = 100

    doubleup = False
    featured = False
    if "⭐ Doble Carga" in discounts:
        doubleup = True
        # Check rss feed for featured
        # featured = featuredrss.search_rss(torrent_id)

    hrless = False

    if freeleech or featured:
        log.info(f"Downloading torrent {torrent_id}...")
        try:
            match = re.search(r"(\d+\.\d+)\s(GiB|MiB)", info)
            size = float(match.group(1))
            unit = match.group(2)
            if unit == "GiB":
                size = gib_to_bytes(size)
            else:
                size = mib_to_bytes(size)
        except Exception as e:
            log.warning("Could not match size.")
            size = None
        torrent = TorrentInfo(name=name, tracker=TrackerName.TORRENTLAND, size=size, id=torrent_id,
                              upload_date=datetime.now(),
                              freeleech=freeleech, doubleup=doubleup, featured=featured, hrless=hrless)
        downloadscheduler.new_torrent(torrent)


@events.register(events.NewMessage(chats=[-1001279197242]))
async def message_handler_xbytesv2(event):
    log.info(event.text)
    # TODO: ?xbytesv2 telegram?


@events.register(events.NewMessage(chats=[-1001201573336, "me"]))
async def message_handler_divteam(event):
    # TODO: divteam telegram
    url_pattern = r"https://divteam.com/torrents/(\d+)"
    try:
        torrent_id = re.search(url_pattern, event.text).group(1)
    except AttributeError as e:
        log.info("Ignoring message:")
        log.info(event.raw_text)
        return

    name, *stuff, info, _, discounts, _, uploader, _, link = event.raw_text.splitlines()
    log.info(f"{name=}")
    log.info(f"{discounts=}")
    # Download logic here...
    freeleech = 0
    if "🏅 100% Free " in discounts:
        log.info("Is freeleech")
        freeleech = 100

    doubleup = False
    featured = False
    if "⭐ Doble Carga" in discounts:
        doubleup = True
        # Check rss feed for featured
        # featured = featuredrss.search_rss(torrent_id)

    hrless = False

    if freeleech or featured:
        log.info(f"Downloading torrent {torrent_id}...")
        try:
            match = re.search(r"(\d+\.\d+)\s(GiB|MiB)", info)
            size = float(match.group(1))
            unit = match.group(2)
            if unit == "GiB":
                size = gib_to_bytes(size)
            else:
                size = mib_to_bytes(size)
        except Exception as e:
            log.warning("Could not match size.")
            size = None
        torrent = TorrentInfo(name=name, tracker=TrackerName.TORRENTLAND, size=size, id=torrent_id,
                              upload_date=datetime.now(),
                              freeleech=freeleech, doubleup=doubleup, featured=featured, hrless=hrless)
        downloadscheduler.new_torrent(torrent)


@events.register(events.NewMessage(chats=[-1001162655394]))
async def message_handler_redbits(event):
    log.info(event.text)
    # TODO: redbits telegram