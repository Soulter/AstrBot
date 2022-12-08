import botpy
from botpy.message import Message
import yaml
import asyncio
import cores.openai.core
import re

chatgpt = ""

session_list = []

class botClient(botpy.Client):
    async def on_at_message_create(self, message: Message):
        # 过滤@头
        pattern = r"<@!\d+>\s+(.+)"
        result = re.search(pattern, message.content)
        if result:
            qq_msg = "[ChatGPT]"+result.group(1).strip()
            chatgpt_res = await chatgpt.chat(qq_msg)
            await message.reply(content=f"{chatgpt_res}")

def initBot(chatgpt_inst):
    global chatgpt
    chatgpt = chatgpt_inst
    with open("./configs/config.yaml", 'r', encoding='utf-8') as ymlfile:
        cfg = yaml.safe_load(ymlfile)
        if cfg['qqbot']['appid'] != '' or cfg['qqbot']['token'] != '':
            print(cfg['qqbot']['appid'])
            intents = botpy.Intents(public_guild_messages=True) 
            client = botClient(intents=intents)
            client.run(appid=cfg['qqbot']['appid'], token=cfg['qqbot']['token'])
        else:
            raise BaseException("请在config中完善你的appid和token")