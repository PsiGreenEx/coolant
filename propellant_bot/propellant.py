# propellant_bot.py
import logging
from abc import ABC
import discord
from discord.ext import commands
from datetime import datetime


class PropellantBot(commands.Bot, ABC):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='propellant.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)

    async def log_print(self, text: str):
        print('[' + datetime.now().strftime("%x %X") + '] ' + text)
        self.logger.info(text)

    async def on_ready(self):
        await self.log_print(f'{self.user} has connected to Discord!')
