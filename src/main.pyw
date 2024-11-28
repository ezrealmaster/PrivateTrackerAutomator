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


def setup_output_logger():
    formatter = log.Formatter('%(asctime)s %(levelname)s: %(message)s')

    handler = log.FileHandler("logs/output.txt", mode='w')
    handler.setFormatter(formatter)
    output_handler = log.StreamHandler()
    output_handler.setFormatter(formatter)

    logger = log.getLogger("output")
    logger.setLevel(log.INFO)
    logger.addHandler(handler)
    logger.addHandler(output_handler)


setup_output_logger()


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

    # Keep telegram handler alive
    telegram_task = asyncio.create_task(telistener.client.run_until_disconnected())

    # Keep RSSReaders alive
    # for rssreader in rssreaders:
    #     tg.create_task(rssreader.poll_new_torrents())

    # Keep LoginScheduler alive
    login_task = asyncio.create_task(login_scheduler.run())

    tasks = {"telegram_task": telegram_task, "login_task": login_task}
    while True:
        done, pending = await asyncio.wait(tasks.values(), return_when=asyncio.FIRST_EXCEPTION)
        for task in done:
            if task is tasks["telegram_task"]:
                if isinstance((e := task.exception()), ConnectionError):
                    log.error("Telegram disconnected. Reconnecting after 1 minute.", exc_info=e)
                    await asyncio.sleep(60)
                    log.info('Rescheduling the task\n')
                    tasks["telegram_task"] = asyncio.create_task(telistener.client.run_until_disconnected())
                elif isinstance(e, Exception):
                    log.getLogger("output").exception(e)
                    log.exception(e)
                    del tasks["telegram_task"]
                else:
                    log.getLogger("output").error("What the hell?")
                    raise RuntimeError("Debug this")
            elif task is tasks["login_task"]:
                if isinstance((e := task.exception()), Exception):
                    log.getLogger("output").exception(e)
                    log.exception(e)
                    del tasks["login_task"]
                else:
                    log.getLogger("output").error("What the hell?")
                    raise RuntimeError("Debug this")


if __name__ == "__main__":
    asyncio.run(main())
