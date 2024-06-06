import logging as log
import asyncio
import datetime as dt
from datetime import datetime
import pickle
from trackers import Tracker


class LoginScheduler:
    def __init__(self):
        self.trackers = None
        self.tracker_names = None
        self.save_file = None

    def initialize(self, trackers: list[Tracker], save_file=None):
        log.info("LoginScheduler: Initializing with trackers and save file.")
        self.trackers = trackers

        self.save_file = save_file
        if save_file.exists():
            with open(self.save_file, "rb") as f:
                last_login = pickle.load(f)
            for tracker in self.trackers:
                try:
                    tracker.last_login = last_login[tracker.name]
                    log.info(f"LoginScheduler: Loaded last login for {tracker.name}: {tracker.last_login}.")
                except KeyError:
                    log.warning(f"LoginScheduler: No last login found for {tracker.name}.")

    def save_state(self):
        save_dict = {tracker.name: tracker.last_login for tracker in self.trackers}
        with open(self.save_file, "wb") as f:
            pickle.dump(save_dict, f)

    async def run(self):
        while True:
            now = datetime.now()
            for tracker in self.trackers:
                if now - tracker.last_login > dt.timedelta(tracker.login_interval):
                    log.info("LoginScheduler: Initiating login.")
                    tracker.login()

            await asyncio.sleep(60)
