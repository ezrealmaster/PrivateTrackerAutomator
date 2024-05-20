if __name__ != "__main__":
    raise RuntimeError("Only for use with the -m switch, not as a Python API")

import yaml

from .unit3d import UNIT3D
from .trackernames import TrackerName

with open("config.yml") as f:
    config = yaml.safe_load(f)
hdotracker = UNIT3D(config["headers"], **config["trackers"]["torrentland"], name=TrackerName("torrentland"))
hdotracker.thank("93130")
