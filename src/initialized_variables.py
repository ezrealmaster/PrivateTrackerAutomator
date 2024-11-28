import yaml

import clients
from trackers import TrackerName, Tracker

# TODO: config file sanity checks
with open("config.yml") as f:
    config = yaml.safe_load(f)


def sanitize_config(config):
    if not config["required_free_space"] >= 0:
        raise ValueError()
    if not config["min_time_until_ban"] >= 0:
        raise ValueError()
    if not config["surplus_stop_coef"] >= 1:
        raise ValueError()


sanitize_config(config)


def reload_config():
    global config
    with open("config.yml") as f:
        config = yaml.safe_load(f)


initialized_trackers: dict[TrackerName, Tracker] = {}

client_config = config["client"]
match client_config["name"]:
    case "qbittorrent":
        torrent_client = clients.qBittorrent(**client_config)
