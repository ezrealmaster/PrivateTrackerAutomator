import datetime as dt
from datetime import datetime
from abc import ABC, abstractmethod
from collections import deque
import pickle
from pathlib import Path
import logging as log

import requests
import requests.cookies

from clients.torrent import Torrent

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
            1 for torrent in self.history if torrent.download_date > datetime.now() - dt.timedelta(days=days))

    def time_until_ban(self, torrents_per_timeframe):
        n_downs, day_limit = torrents_per_timeframe
        if len(self.history) == 0:
            return 0, 0, 0, 0
        elif len(self.history) >= n_downs:
            limit_date: datetime = self.history[-n_downs].download_date + dt.timedelta(days=day_limit)
        else:
            limit_date: datetime = self.history[0].download_date + dt.timedelta(days=day_limit)
            # TODO: incorrect logic
        timedelta = limit_date - datetime.now()
        hours, seconds = divmod(timedelta.seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return timedelta.days, hours, minutes, seconds


class Tracker(ABC):
    def __init__(self, name: TrackerName, base_url, torrents_per_timeframe: tuple[int, int],
                 login_interval: int, seed_time, seed_ratio, username=None, password=None, cookie=None, time_or_ratio=False, save_file=None, login_scheduler=None, **kwargs):
        """
        Tracker definition. Includes inactivity and seeding rules, as well as post-download actions.
        :param name:
        :param base_url:
        :param username:
        :param password:
        :param cookie:
        :param torrents_per_timeframe: A tuple of ints (number of downloaded torrents, time limit in days)
        :param login_interval: in days
        :param seed_time:
        :param seed_ratio:
        :param time_or_ratio: If True fulfilling any of the time or ratio requirements makes it safe to remove the
        torrent. If False, both conditions must be fulfilled.
        """
        assert save_file is not None
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

        self.login_interval = login_interval

        # Seeding rules
        self.seed_time = seed_time
        self.seed_ratio = seed_ratio
        self.time_or_ratio = time_or_ratio

        self.save_file = Path(save_file)
        if self.save_file.exists():
            with open(self.save_file, "rb") as f:
                history = pickle.load(f)
            self.download_history = history
        else:
            log.getLogger("output").info(f"Warning: savefile {self.save_file} not found. Starting {self.name} with empty history.")
            self.download_history = DownloadHistory()
        self.last_login = datetime.now()
        self.login_scheduler = login_scheduler
        self.session = requests.Session()
        self.set_session_cookies(cookie)
        self.auto_login = True

    def set_session_cookies(self, cookie):
        if cookie is not None:
            cookie_dict = {}
            for cook in cookie.split(';'):
                k, v = cook.strip().split('=')
                cookie_dict[k] = v
            jar = requests.cookies.cookiejar_from_dict(cookie_dict)
            self.session.cookies = jar
        else:
            self.session.cookies.clear()

    def save_history(self):
        with open(self.save_file, "wb") as f:
            pickle.dump(self.download_history, f)

    def requirements_fulfilled(self, torrents_per_timeframe=None, min_time_until_ban=0):
        if torrents_per_timeframe is not None:
            dl_requirement, time_limit = torrents_per_timeframe
        else:
            dl_requirement, time_limit = self.torrents_per_timeframe
        return self.download_history.downloads_last_x_days(time_limit) >= dl_requirement and self.download_history.time_until_ban([dl_requirement, time_limit])[0] >= min_time_until_ban

    def daily_limit_reached(self, daily_limit):
        return self.download_history.downloads_last_x_days(1) >= daily_limit

    @abstractmethod
    def login(self):
        self.last_login = datetime.now()
        self.login_scheduler.save_state()

    def get_torrent_info(self, torrent_id: str):
        pass

    def search(self, name: str):
        pass

    @abstractmethod
    def get_download_url(self, torrent: TorrentInfo) -> tuple[str, str]:
        raise NotImplementedError()

    def can_remove(self, torrent: Torrent):
        if self.seed_time == "override" or self.seed_ratio == "override":
            raise AssertionError("Subclass must override this method.")
        if torrent.seeding_time > self.seed_time and torrent.ratio > self.seed_ratio:
            return True
        elif self.time_or_ratio and (torrent.seeding_time > self.seed_time or torrent.ratio > self.seed_ratio):
            return True
        return False

    def post_download_action(self, torrent: TorrentInfo):
        pass
