import logging as log
from typing import Literal

import requests
from bs4 import BeautifulSoup

from utils import urljoin

from .torrentinfo import TorrentInfo
from .tracker import Tracker


class Sportscult(Tracker):
    def __init__(self, headers, **kwargs):
        super().__init__(**kwargs)

        self.login_page = urljoin(self.base_url, "index.php?page=login")

        self.headers_login = headers["login"]

    def login(self):
        log.info(f"Logging in into {self.name.value}.")
        self.session.cookies.clear()
        r = self.session.post(self.login_page, data={"uid": self.username, "pwd": self.password}, headers=self.headers_login)
        log.info("Log in page sent response: %s", r)
        if r.status_code == 200:
            log.info("Success.")
            super().login()
        else:
            log.warning(r)
            log.warning(r.text)
            raise RuntimeError("Failed login")

    def get_download_url(self, torrent: TorrentInfo):
        log.getLogger("output").info("Sportscult download...")
