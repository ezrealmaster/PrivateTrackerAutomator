import datetime
from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime

import requests

from src.clients.torrent import Torrent

from .torrentinfo import TorrentInfo
from .trackernames import TrackerName


class DownloadHistory:
    def __init__(self):
        self.history = deque(maxlen=100)

    def add(self, torrent: TorrentInfo):
        if torrent.download_date is None:
            raise ValueError("Torrent download_date must be initialized.")
        self.history.append(torrent)

    def downloads_last_x_days(self, days):
        return sum(
            1 for torrent in self.history if torrent.download_date > datetime.now() - datetime.timedelta(days=days))

    def time_until_ban(self, torrents_per_timeframe):
        n_downs, day_limit = torrents_per_timeframe
        limit_date: datetime = self.history[-n_downs].download_date + datetime.timedelta(days=day_limit)
        timedelta = limit_date - datetime.now()
        hours, seconds = divmod(timedelta.seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return timedelta.days, hours, minutes, seconds


class Tracker(ABC):
    def __init__(self, name: TrackerName, base_url, username, password, torrents_per_timeframe: tuple[int, int],
                 login_interval: int, seed_time, seed_ratio, time_or_ratio=False, **kwargs):
        """
        Tracker definition. Includes inactivity and seeding rules, as well as post-download actions.
        :param name:
        :param base_url:
        :param username:
        :param password:
        :param torrents_per_timeframe: A tuple of ints (number of downloaded torrents, time limit in days)
        :param login_interval:
        :param seed_time:
        :param seed_ratio:
        :param time_or_ratio:
        """
        if seed_time == "override" or seed_ratio == "override":
            if type(self).can_remove == Tracker.can_remove:
                raise AssertionError("can_remove method has not been overriden.")
        if time_or_ratio and (
                (type(seed_ratio) is int and seed_ratio <= 0) or (type(seed_time) is int and seed_time <= 0)):
            raise ValueError("Tracker seed_ratio and seed_time cannot be 0 if time_or_ratio is True.")

        self.name = name

        self.base_url = base_url
        self.username = username
        self.password = password

        # Inactivity rules
        self.torrents_per_timeframe = torrents_per_timeframe

        self.log_in_every_days = login_interval

        # Seeding rules
        self.seed_time = seed_time
        self.seed_ratio = seed_ratio
        self.time_or_ratio = time_or_ratio

        self.download_history = DownloadHistory()
        self.session = requests.Session()

    @abstractmethod
    def login(self):
        raise NotImplementedError()

    def can_remove(self, torrent: Torrent):
        if self.seed_time == "override" or self.seed_ratio == "override":
            raise AssertionError("Subclass must override this method.")
        if torrent.seeding_time > self.seed_time and torrent.ratio > self.seed_ratio:
            return True
        elif self.time_or_ratio and (torrent.seeding_time > self.seed_time or torrent.ratio > self.seed_ratio):
            return True
        return False

    def download_action(self, torrent: TorrentInfo):
        pass
