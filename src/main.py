import logging as log
import asyncio
from pathlib import Path

from initialized_variables import initialized_trackers, config
import telegram as te
import rssreader as rss
from loginscheduler import LoginScheduler
from trackers.trackernames import TrackerName
from trackers.trackermappings import TRACKER_CLASSES


log.basicConfig(filename="logs/latest.log", filemode="w", encoding="utf-8", level=log.INFO,
                format="%(asctime)s %(levelname)s: %(message)s", datefmt="%c")


async def main():
    save_folder = Path(config["save_folder"])
    save_folder.mkdir(exist_ok=True)

    login_scheduler = LoginScheduler()

    # Initialize trackers
    for tracker in config["trackers"]:
        if (name := TrackerName(tracker)) in TRACKER_CLASSES:
            initialized_trackers[name] = TRACKER_CLASSES[name](config["headers"], **config["trackers"][tracker], name=name, save_file=save_folder / f"{tracker}.pickle", login_scheduler=login_scheduler)
            log.info(f"Instantiated class for {tracker}.")
        else:
            log.warning(f"No class mapped to {tracker}")

    # Initialize LoginScheduler
    login_scheduler.initialize(list(initialized_trackers.values()), save_file=save_folder / "login.pickle")

    # Initialize update handlers
    telistener = te.TelegramListener(config["telegramlistener"])
    await telistener.client.start()
    for tracker in config["trackers"]:
        if "handler" in config["trackers"][tracker] and config["trackers"][tracker]["handler"] == "telegram":
            telistener.add_handler(getattr(te, f"message_handler_{tracker}"))
            log.info(f"Added telegram handler to {tracker}.")

    # Initialize RSSReaders

    async with asyncio.TaskGroup() as tg:
        # Keep telegram handler alive
        tg.create_task(telistener.client.run_until_disconnected())

        # Keep RSSReaders alive
        # for rssreader in rssreaders:
        #     tg.create_task(rssreader.poll_new_torrents())

        # Keep LoginScheduler alive
        tg.create_task(login_scheduler.run())


if __name__ == "__main__":
    asyncio.run(main())
