import requests
import logging as log

from trackers import Tracker, TorrentInfo
from utils import bytes_to_gib
from initialized_variables import initialized_trackers


def new_torrent(torrent: TorrentInfo):
    log.info("Deciding download for torrent:")
    log.info(torrent)

    # Download logic...
    tracker = initialized_trackers[torrent.tracker]



    #tracker.post_download_action(torrent)
