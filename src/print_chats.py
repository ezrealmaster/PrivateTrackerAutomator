import asyncio

import yaml

import telegram as te


async def print_chats(client, *args):
    async for dialog in client.iter_dialogs():
        print(dialog.name, 'has ID', dialog.id)


async def print_chat(client, chat):
    async for message in client.iter_messages(chat):
        sender = await message.get_sender()
        print(message.id, sender, message.text)


async def main():
    with open("config.yml") as f:
        config = yaml.safe_load(f)

    telistener = te.TelegramListener(config["telegramlistener"])
    await telistener.client.start()
    await print_chats(telistener.client)

if __name__ == "__main__":
    asyncio.run(main())
