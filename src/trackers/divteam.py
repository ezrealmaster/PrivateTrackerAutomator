import logging as log
from typing import Literal

import requests
from bs4 import BeautifulSoup

from utils import urljoin

from .torrentinfo import TorrentInfo
from .tracker import Tracker


class Divteam(Tracker):
    def __init__(self, headers, **kwargs):
        super().__init__(**kwargs)

        self.login_page = urljoin(self.base_url, "index.php?page=login")
        self.torrent_page_ocio = urljoin(self.base_url, "index.php?page=torrent-details-ocio&id=")
        self.torrent_page_cultura = urljoin(self.base_url, "index.php?page=torrent-details-cultura&id=")

        self.download_page = urljoin(self.base_url, "download.php?id=")

        self.headers_login = headers["login"]

    def login(self):
        log.info(f"Logging in into {self.name.value}.")
        r = self.session.get(self.login_page, headers=self.headers_login, allow_redirects=False)
        log.info("Log in page sent response: %s", r)
        if r.status_code == 302 and r.headers["location"] == "index.php":
            self.session.get(self.base_url, headers=self.headers_login)
            log.info("Success.")
            super().login()
        elif r.status_code == 200:
            log.getLogger("output").info("Divteam cookie is expired. Update config file and restart.")
            log.warning("Divteam cookie is expired. Update config file and restart.")
            self.auto_login = False
            raise requests.exceptions.HTTPError("Cookie expired.")
        else:
            log.warning(r)
            log.warning(r.text)
            raise RuntimeError("Failed login")

    def get_torrent_info(self, torrent_id: str, category: Literal["ocio"] | Literal["cultura"] = "ocio"):
        torrent_page = self.torrent_page_ocio if category == "ocio" else self.torrent_page_cultura
        r = self.session.get(torrent_page + torrent_id, headers=self.headers_login, allow_redirects=False)
        log.debug(f"Obtaining torrent info. Response {r}")
        if "No tienes permiso para ver el Torrents!" in r.text:
            log.getLogger("output").info("Divteam cookie needs to be reset!")
            self.login()
        soup = BeautifulSoup(r.content, "lxml", from_encoding="utf-8")
        with open("logs/divteam_torrent.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        log.debug("Parsed torrent page.")
        size, unit = str(soup.find("li", attrs={"class": "list-group-item bot-flex"}).contents[1]).split()
        res = soup.find("span", attrs={"class": "label label-gold"})
        if res is None:
            log.debug("Couldn't find gold torrent element.")
            freeleech = 0
        else:
            log.debug("Found gold torrent element!")
            freeleech = 100
        return float(size), unit, freeleech

    def get_download_url(self, torrent: TorrentInfo):
        download_url = self.download_page + torrent.id
        uid = self.session.cookies.get_dict()["uid"]
        return download_url, "uid=" + uid
