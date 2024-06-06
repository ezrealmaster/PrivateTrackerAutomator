import logging as log

from src.utils import urljoin

from .torrentinfo import TorrentInfo
from .tracker import Tracker


class Divteam(Tracker):
    def __init__(self, headers, **kwargs):
        super().__init__(**kwargs)

        self.login_page = urljoin(self.base_url, "index.php?page=login")
        self.torrent_page = urljoin(self.base_url, "torrents")

        self.headers_login = headers["login"]
        self.headers_thank = headers["unit3dthank"]

    def login(self):
        log.info(f"Logging in into {self.name.value}.")
        r = self.session.get(self.base_url, headers=self.headers_login, allow_redirects=False)
        log.info("Log in page sent response: %s", r)
        if r.status_code == 302 and r.headers["location"] == self.login_page:
            log.warning("Divteam cookie is expired. Need to log in again.")
            raise RuntimeError("Couldn't log in.")
        elif r.status_code == 200:
            log.info("Success.")
            super().login()
        else:
            log.warning(r)
            log.warning(r.text)
            raise RuntimeError("Failed login")

    def get_download_url(self, torrent: TorrentInfo):
        print("Divteam download...")
        # TODO: divteam implementation
