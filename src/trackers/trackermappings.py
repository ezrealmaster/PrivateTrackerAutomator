from .trackernames import TrackerName
from .unit3d import UNIT3D
from .cinemaz import Cinemaz


TRACKER_CLASSES = {
    TrackerName.HDOLIMPO: UNIT3D,
    TrackerName.FEARNOPEER: UNIT3D,
    TrackerName.CINEMAZ: Cinemaz,
    # TrackerName.XBYTESV2: Xbytesv2,
    TrackerName.TORRENTLAND: UNIT3D
}

initialized_trackers = {}