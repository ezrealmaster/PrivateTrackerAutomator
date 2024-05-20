import requests

from trackers import Tracker, TorrentInfo, initialized_trackers
from utils import bytes_to_gib


def new_torrent(torrent: TorrentInfo):
    # Download logic...
    tracker = initialized_trackers[torrent.tracker]


    tracker.download_action(torrent)
