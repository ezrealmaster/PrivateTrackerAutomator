# Run this with "python -m src.trackers.run_submodule"

if __name__ != "__main__":
    raise RuntimeError("Only for use with the -m switch, not as a Python API")

import yaml
import datetime as dt

from src.loginscheduler import LoginScheduler
from src.clients.qbittorrent import qBittorrent

from .unit3d import UNIT3D
from .trackernames import TrackerName
from .torrentinfo import TorrentInfo

with open("config.yml") as f:
    config = yaml.safe_load(f)
torrent_client = qBittorrent(**config["client"])
login_scheduler = LoginScheduler()
hdotracker = UNIT3D(config["headers"], **config["trackers"]["hdolimpo"], name=TrackerName("hdolimpo"),
                    save_file="temp/hdolimpo.pickle", login_scheduler=login_scheduler)
login_scheduler.initialize([hdotracker], save_file="temp/login.pickle")

torrent = TorrentInfo(name="El caso sancho", tracker=TrackerName.HDOLIMPO, size=0, id="58117",
                      upload_date=dt.datetime.now(), freeleech=100, doubleup=False, featured=False, hrless=False)
url, cookie = hdotracker.get_download_url(torrent)
good, bad = torrent_client.add_torrent(url, "AutoHdolimpo", cookie)
print(bad)
print(good)
# import yaml
#
# from .divteam import Divteam
# from .trackernames import TrackerName
#
# with open("config.yml") as f:
#     config = yaml.safe_load(f)
#
# divteamtracker = Divteam(config["headers"], **config["trackers"]["divteam"], name=TrackerName("divteam"), save_file="temp/divteam.pickle")
# print(divteamtracker.get_torrent_info("542c9c4a144bb699e42dc369ac9de6fc3ebf332d", "ocio"))

# import yaml
#
# from .sportscult import Sportscult
# from .trackernames import TrackerName
#
# with open("config.yml") as f:
#     config = yaml.safe_load(f)
#
# sportstracker = Sportscult(config["headers"], **config["trackers"]["sportscult"], name=TrackerName("sportscult"), save_file="temp/sportscult.pickle")
# print(sportstracker.session.cookies)
# sportstracker.login()
# print(sportstracker.session.cookies)

# import yaml
#
# from .cinemaz import Cinemaz
# from .trackernames import TrackerName
#
# with open("config.yml") as f:
#     config = yaml.safe_load(f)
#
# cztracker = Cinemaz(config["headers"], **config["trackers"]["cinemaz"], name=TrackerName("cinemaz"), save_file="temp/cinemaz.pickle")
# cztracker.login()
