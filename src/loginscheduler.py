import asyncio
import datetime as dt
from datetime import datetime
import logging as log

from trackers import Tracker


class LoginScheduler:
    def __init__(self, trackers: list[Tracker]):
        self.trackers = trackers

        self.last_login = []
        for i, tracker in enumerate(trackers):
            self.last_login[i] = datetime.now()

    async def run(self):
        while True:
            # Calculate next login time
            next_is = []
            next_time: datetime | None = None
            for i, last_login in enumerate(self.last_login):
                new_time = last_login + dt.timedelta(days=self.trackers[i].login_interval)
                if next_time is None or new_time < next_time:
                    next_is = [i]
                    next_time = new_time
                elif new_time == next_time:
                    next_is.append(i)
            log.info("Next log in time:", next_time)
            log.info("Next trackers to log in:", [self.trackers[i] for i in next_is])

            await asyncio.sleep((next_time - datetime.now()).total_seconds())

            for i in next_is:
                try:
                    self.trackers[i].login()
                    self.last_login[i] = datetime.now()
                except RuntimeError as e:
                    log.exception(f"Exception when logging in to {self.trackers[i].name.value}. Waiting 30 minutes to retry.", e)
                    self.last_login[i] = self.last_login[i] + dt.timedelta(minutes=30)

