from telethon import TelegramClient, events
from telegram import Bot

import re
import asyncio
import dotenv


config = dotenv.dotenv_values(".env")


api_id = config["api_id"]
api_hash = config["api_hash"]
source_channel = config["source_channel"]
target_chat = config["target_chat"]

link_replaced = config["link_replaced"]
name_replaced = config["name_replaced"]

client = TelegramClient('session', api_id, api_hash)

@client.on(events.NewMessage(chats=source_channel))
async def handler(event):
    final_message = re.sub(r'\[.*?\]\(https://t\.me/\S+?\)', f'[{name_replaced}]({link_replaced})', event.message.text)
    try:
        if event.message.media:
            await client.send_file(int(target_chat), file=event.message.media, caption=final_message)
        else:
            await client.send_message(int(target_chat), final_message)

        print(f"{event.message.text}")
        print("Message forwarded")
    except Exception as e:
        print(f"Cause an error while forwarding a message: {e}")

    chat = await event.get_chat()
    print(f"Название чата: {chat.title if hasattr(chat, 'title') else 'Личка'}")
    print(f"ID чата: {chat.id}")

async def main():
    print("Self bot has runned")
    await client.run_until_disconnected()

client.start()
client.run_until_disconnected()