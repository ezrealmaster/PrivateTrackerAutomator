import math

from src.utils import urljoin, bytes_to_gib
from src.clients.torrent import Torrent

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
        self.torrent_page = urljoin(self.base_url, "torrent")

        self.headers_login = headers["login"]

    def login(self):
        print("Cinemaz login...")

    def can_remove(self, torrent: Torrent):
        _time = seed_time(torrent)
        if torrent.seeding_time > _time and torrent.ratio > self.seed_ratio:
            return True
        elif self.time_or_ratio and (torrent.seeding_time > _time or torrent.ratio > self.seed_ratio):
            return True
        return False