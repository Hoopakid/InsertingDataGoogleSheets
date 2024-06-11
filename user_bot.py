import os
from telethon.sync import TelegramClient, events
from dotenv import load_dotenv

load_dotenv()

api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')

with TelegramClient('name', api_id, api_hash) as client:
    @client.on(events.NewMessage(pattern='(?i).*Assalomu Alaykum'))
    async def handler(event):
        await event.reply(
            "Va Alaykum Assalom, Assalomu Alaykum, men Sherzodning yordamchisiman, Sherzod hozir dam olmoqda yoki ishda, iltimos, biror savol bo'lsa yozib qoldiring!")
        await event.reply('Rahmat 😊')


    @client.on(events.NewMessage(pattern='(?i).*qalesan'))
    async def handler(event):
        await event.reply(
            "Assalomu Alaykum, men Sherzodning yordamchisiman, Sherzod hozir dam olmoqda yoki ishda, iltimos, biror savol bo'lsa yozib qoldiring!")
        await event.reply('Rahmat 😊')


    @client.on(events.NewMessage(pattern='(?i).*qalesiz'))
    async def handler(event):
        await event.reply(
            "Assalomu Alaykum, men Sherzodning yordamchisiman, Sherzod hozir dam olmoqda yoki ishda, iltimos, biror savol bo'lsa yozib qoldiring!")
        await event.reply('Rahmat 😊')


    @client.on(events.NewMessage(pattern='(?i).*sher'))
    async def handler(event):
        await event.reply(
            "Assalomu Alaykum, men Sherzodning yordamchisiman, Sherzod hozir dam olmoqda yoki ishda, iltimos, biror savol bo'lsa yozib qoldiring!")
        await event.reply('Rahmat 😊')


    @client.on(events.NewMessage(pattern='(?i).*sherzod'))
    async def handler(event):
        await event.reply(
            "Assalomu Alaykum, men Sherzodning yordamchisiman, Sherzod hozir dam olmoqda yoki ishda, iltimos, biror savol bo'lsa yozib qoldiring!")
        await event.reply('Rahmat 😊')


    client.run_until_disconnected()
