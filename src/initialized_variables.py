import yaml

import clients
from trackers import TrackerName, Tracker

with open("config.yml") as f:
    config = yaml.safe_load(f)
if not config["required_free_space"] >= 0:
    raise ValueError()
if not config["min_time_until_ban"] >= 0:
    raise ValueError()
if not config["max_surplus_coef"] >= 1:
    raise ValueError()

initialized_trackers: dict[TrackerName, Tracker] = {}

client_config = config["client"]
match client_config["name"]:
    case "qbittorrent":
        torrent_client = clients.qBittorrent(**client_config)
