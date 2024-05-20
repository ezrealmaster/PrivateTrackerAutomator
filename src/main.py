import logging as log
import asyncio

import yaml

import telegram as te
import rssreader as rss

log.basicConfig(filename="logs/latest.log", filemode="w", encoding="utf-8", level=log.WARNING,
                format="%(asctime)s %(levelname)s: %(message)s", datefmt="%c")


async def print_chats(client):
    async for dialog in client.iter_dialogs():
        print(dialog.name, 'has ID', dialog.id)


async def main():
    with open("config.yml") as f:
        config = yaml.safe_load(f)

    telistener = te.TelegramListener(config["telegramlistener"])
    await telistener.client.start()
    # await print_chats(telistener.client)
    # exit()
    telistener.add_handler(te.message_handler_hdolimpo)
    telistener.add_handler(te.message_handler_torrentland)
    async with asyncio.TaskGroup() as tg:
        tg.create_task(telistener.client.run_until_disconnected())
        # telegram message handler calls DownloadScheduler

        # LoginScheduler running on the back to avoid inacivity bans
        # rssreader = rss.RSSReader("lol")
        # rssreader2 = rss.RSSReader("lmao")
        # tg.create_task(rssreader.poll_new_torrents())
        # tg.create_task(rssreader2.poll_new_torrents())


if __name__ == "__main__":
    asyncio.run(main())
