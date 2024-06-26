import logging as log
from datetime import datetime
import traceback

import requests

from trackers import Tracker, TorrentInfo
from utils import gib_to_bytes
from initialized_variables import initialized_trackers, torrent_client, config


def new_torrent(torrent: TorrentInfo):
    log.info("Deciding download for torrent:")
    log.info(torrent)

    # Download logic...
    tracker = initialized_trackers[torrent.tracker]
    free_space = torrent_client.remote_free_space()
    required_free_space = gib_to_bytes(config["required_free_space"])
    unfulfilled_reserved_space = gib_to_bytes(config["unfulfilled_reserved_space"])

    download = False
    # If enough space left for download:
    if torrent.size < free_space - required_free_space:
        # If torrent goal in time limit not fulfilled: download
        # (you would already be banned)
        if not tracker.requirements_fulfilled():
            download = True
        # Else, check not over surplus limit
        elif not tracker.requirements_fulfilled((tracker.torrents_per_timeframe[0], tracker.torrents_per_timeframe[1] / config["surplus_stop_coef"])):
            # Compare priority:
            emergency = False
            for other in initialized_trackers.values():
                if other is tracker:
                    continue
                if not other.requirements_fulfilled() and torrent.size > free_space - required_free_space - unfulfilled_reserved_space:
                    emergency = True

            if not emergency:
                download = True

    if download:
        url, cookie = tracker.get_download_url(torrent)
        good, bad = torrent_client.add_torrent(url, "Auto" + tracker.name.value.capitalize(), cookie)
        if len(bad) != 0:
            log.error(bad[0])
            log.error("Could not download torrent:", torrent)
        else:
            torrent.download_date = datetime.now()
            tracker.download_history.add(torrent)

            tracker.post_download_action(torrent)
