import math
import logging as log

import requests
from bs4 import BeautifulSoup

from utils import urljoin, bytes_to_gib
from clients.torrent import Torrent

from . import TorrentInfo
from .tracker import Tracker


def seed_time(torrent: Torrent):
    x = bytes_to_gib(torrent.size)
    if x <= 1:
        f = 72
    elif 1 < x < 50:
        f = 72 + 2 * x
    else:
        f = 100 * math.log(x) - 219.2023
    return f * 3600 * 1.1


class Cinemaz(Tracker):
    def __init__(self, headers, **kwargs):
        super().__init__(**kwargs)

        self.login_page = urljoin(self.base_url, "auth", "login")
        self.torrent_page = urljoin(self.base_url, "torrent")  # Will redirect when requesting torrent/id

        self.headers_login = headers["login"]

    def login(self):
        log.info(f"Logging in into {self.name.value}.")
        r = self.session.get(self.base_url, headers=self.headers_login, allow_redirects=False)
        log.info("Log in page sent response: %s", r)
        soup = BeautifulSoup(r.content, "lxml")
        title = soup.find("h1", attrs={"class": "title"})
        if title.string == "Welcome to CinemaZ":
            log.getLogger("output").info("Cinemaz cookie is expired. Update config file and restart.")
            log.warning("Cinemaz cookie is expired. Update config file and restart.")
            self.auto_login = False
            raise requests.exceptions.HTTPError("Cookie expired.")
        elif len(title.contents) > 1 and title.contents[1] == " CinemaZ":
            log.info("Success.")
            super().login()
        else:
            log.warning(r)
            log.warning(r.text)
            raise RuntimeError("Failed login")

    def get_download_url(self, torrent: TorrentInfo):
        log.getLogger("output").info('Cinemaz download...')

    def can_remove(self, torrent: Torrent):
        _time = seed_time(torrent)
        if torrent.seeding_time > _time and torrent.ratio > self.seed_ratio:
            return True
        elif self.time_or_ratio and (torrent.seeding_time > _time or torrent.ratio > self.seed_ratio):
            return True
        return False