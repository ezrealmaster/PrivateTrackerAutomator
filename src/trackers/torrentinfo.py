from dataclasses import dataclass
from datetime import datetime

from .trackernames import TrackerName


@dataclass
class TorrentInfo:
    name: str = None
    tracker: TrackerName = None
    size: int = None

    # Pre-download info
    id: int = None
    upload_date: datetime = None
    freeleech: int = None
    doubleup: bool = None
    featured: bool = None
    hrless: bool = None
    download_date: datetime = None
