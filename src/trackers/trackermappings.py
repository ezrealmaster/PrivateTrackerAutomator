from .trackernames import TrackerName
from .unit3d import UNIT3D
from .cinemaz import Cinemaz
from .divteam import Divteam


TRACKER_CLASSES = {
    TrackerName.HDOLIMPO: UNIT3D,
    TrackerName.FEARNOPEER: UNIT3D,
    TrackerName.CINEMAZ: Cinemaz,
    TrackerName.XBYTESV2: UNIT3D,
    TrackerName.TORRENTLAND: UNIT3D,
    TrackerName.DIVTEAM: Divteam,
    TrackerName.REDBITS: UNIT3D
}
