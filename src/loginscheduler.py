import asyncio

from trackers import Tracker


class LoginScheduler:
    def __init__(self, trackers: list[Tracker]):
        self.trackers = trackers

    async def run(self):
        pass
        # Calculate next login time
        # await asyncio.wait(until_next_time)
        # tracker.login()
