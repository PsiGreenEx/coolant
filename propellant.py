# propellant_bot.py
import copy
import json
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

        # Game Information (such as item data)
        with open("./data/game_info.json", "r") as f:
            self.GAME_INFO_DICT: dict = json.loads(f.read())

        self.ITEM_INFO_DICT: dict = self.GAME_INFO_DICT['items']

        # Game Data (such as players' inventories)
        with open("./store/game_data.json", "r") as f:
            self.game_data_dict: dict = json.loads(f.read())

    async def log_print(self, text: str):
        print('[' + datetime.now().strftime("%x %X") + '] ' + text)
        self.logger.info(text)

    def save_data(self):
        with open('./store/game_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.game_data_dict, f, ensure_ascii=False, indent=2)

    # Get User Data and initialize if needed
    def get_user_data(self, user_id: int, reset=False) -> dict:
        if str(user_id) not in self.game_data_dict or reset:
            self.game_data_dict[str(user_id)] = copy.deepcopy(self.GAME_INFO_DICT["default_user"])
            self.save_data()
        return self.game_data_dict[str(user_id)]

    async def on_ready(self):
        await self.log_print(f'{self.user} has connected to Discord!')
