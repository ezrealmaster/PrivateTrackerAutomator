import json
import time
import copy
import logging as log

from bs4 import BeautifulSoup

from src.utils import urljoin, id_generator

from .trackernames import TrackerName
from .torrentinfo import TorrentInfo
from .tracker import Tracker


class UNIT3D(Tracker):
    def __init__(self, headers, **kwargs):
        super().__init__(**kwargs)

        self.login_page = urljoin(self.base_url, "login")
        self.torrent_page = urljoin(self.base_url, "torrents")

        self.headers_login = headers["login"]
        self.headers_thank = headers["unit3dthank"]

    def login(self):
        log.info(f"Logging in into {self.name.value}.")
        self.session.cookies.clear()
        self.session.cookies.set("laravel_cookie_consent", "1", domain=self.base_url.strip("/").split("/")[-1])
        r = self.session.get(self.login_page, headers=self.headers_login)
        log.info("Log in page sent response: %s", r)
        time.sleep(1)
        soup = BeautifulSoup(r.content, "lxml")
        token = soup.form.find('input', attrs={'name': '_token', 'type': 'hidden'})['value']
        captcha = soup.form.find('input', attrs={'name': '_captcha', 'type': 'hidden'})['value']
        tag = soup.form.findAll('input')[-1]
        rkey = tag["name"]
        rnum = tag["value"]
        data = {"_token": token, "_captcha": captcha, rkey: rnum, "_username": "", "username": self.username,
                "password": self.password, "remember": "on"}
        r = self.session.post(self.login_page, data=data, headers=self.headers_login)
        with open("logs/login_page.html", "w", encoding="utf-8") as f:
            f.write(BeautifulSoup(r.content, "lxml").prettify())
        if r.status_code == 200:
            log.info("Success.")
            super().login()
        else:
            log.warning(r)
            log.warning(r.text)
            raise RuntimeError("Failed login")

    def get_download_url(self, torrent: TorrentInfo):
        download_url = urljoin(self.torrent_page, "download", torrent.id)
        try:
            cookie = self.session.cookies.get_dict()["laravel_session"]
        except KeyError:
            # log in for the first time
            self.login()
            cookie = self.session.cookies.get_dict()["laravel_session"]
        return download_url, "laravel_session=" + cookie

    def post_download_action(self, torrent: TorrentInfo):
        self.thank(torrent.id)

    def thank(self, torrent_id):
        torrent_id = int(torrent_id)
        torrent_page = urljoin(self.torrent_page, torrent_id)
        r = self.session.get(torrent_page, headers=self.headers_login, allow_redirects=False)
        if r.status_code == 302 and r.headers["location"] == self.login_page:
            log.info("Need to log in...")
            self.login()
            r = self.session.get(torrent_page, headers=self.headers_login, allow_redirects=False)
        soup = BeautifulSoup(r.content, "lxml")
        with open("logs/torrent_page.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        headers = copy.deepcopy(self.headers_thank)
        headers["Origin"] = self.base_url
        headers["Referer"] = torrent_page

        # fingerprint/initial state extraction depends on Unit3d version
        token = soup.find("meta", attrs={"name": "csrf-token"})["content"]
        buttons = soup.find_all("button", attrs={"wire:id": True})
        button = buttons[1] if self.name == TrackerName.TORRENTLAND else buttons[0]
        if button.has_attr("wire:initial-data"):
            initial_data = button["wire:initial-data"]
            payload = json.loads(initial_data)
            payload.pop("effects", None)
            payload["updates"] = [{
                "type": "callMethod",
                "payload": {
                    "id": id_generator(),
                    "method": "store",
                    "params": [torrent_id]
                }
            }]
            headers["X-CSRF-TOKEN"] = token
            r = self.session.post(urljoin(self.base_url, "livewire/message/thank-button"), json=payload,
                                  headers=headers)
        elif button.has_attr("wire:snapshot"):
            snapshot = button["wire:snapshot"]
            payload = {
                "_token": token,
                "components": [{
                    "snapshot": snapshot,
                    "updates": {},
                    "calls": [{
                        "path": "",
                        "method": "store",
                        "params": [torrent_id]
                    }]
                }]
            }
            headers["X-Livewire"] = ''
            r = self.session.post(urljoin(self.base_url, "livewire/update"), json=payload,
                                  headers=headers)
        if r.status_code == 200:
            log.info(f"Successfully thanked torrent {torrent_page}.")
        else:
            log.warning(r)
            log.warning(r.text)
            raise RuntimeError(f"Could not thank {torrent_page}.")
