from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import PeerChannel
from telethon import TelegramClient, events
from collections import deque

import re
import dotenv


config = dotenv.dotenv_values(".env")
processed_albums = deque(maxlen=10)

api_id = config["api_id"]
api_hash = config["api_hash"]
source_channel = int(config["source_channel"])
target_chat = int(config["target_chat"])

link_replaced = config["link_replaced"]
name_replaced = config["name_replaced"]

client = TelegramClient('session', api_id, api_hash, connection_retries=5, timeout=10)

async def resolve_chat_by_id(client, chat_id: int):
    peer = PeerChannel(chat_id)
    full = await client(GetFullChannelRequest(peer))
    return full.chats[0]


@client.on(events.NewMessage(chats=source_channel))
async def message_handler(event: events.NewMessage.Event):
    try:

        if event.message.grouped_id is not None:
            if event.message.grouped_id in processed_albums:
                return
            else:
                processed_albums.append(event.message.grouped_id)
                return

        chat_id = int(config["target_chat"])
        target_chat = await resolve_chat_by_id(client, chat_id)

        text = event.message.text or ""
        final_message = re.sub(r'\[.*?\]\(https://t\.me/\S+?\)', f'[{name_replaced}]({link_replaced})', text)
        super_final_message = re.sub(r'''Присоединяйся к нам 🔻 t\.me/\S+?\ 🔻
Приглашай друзей. Мы ждем тебя.''', ' ', final_message)
        if event.message.media:
            await client.send_file(target_chat, file=event.message, caption=super_final_message)
        else:
            await client.send_message(target_chat, super_final_message)

        print(f"{event.message.text}")

    except Exception as e:
        print(f"{e}")

@client.on(events.Album(chats=source_channel)) 
async def album_handler(event):
    text = event.text or ""
    final_message = re.sub(r'\[.*?\]\(https://t\.me/\S+?\)', f'[{name_replaced}]({link_replaced})', text)
    super_final_message = re.sub(r'''Присоединяйся к нам 🔻 t\.me/\S+?\ 🔻
Приглашай друзей. Мы ждем тебя.''', ' ', final_message)
    target_chat = await resolve_chat_by_id(client, int(config["target_chat"]))
    await client.send_message(
        entity=target_chat,
        file=event.messages,
        message=super_final_message,
    )

client.start()
client.run_until_disconnected()