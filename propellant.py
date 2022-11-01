# propellant_bot.py
import copy
import json
import logging
from abc import ABC
import discord
from discord.ext import commands
from datetime import datetime
from enum import Enum


class Emojis:
    TOKEN = "<:token:1033006849190006914>"
    SHINY = "<:shiny:1033007188446290051>"


class PropellantBot(commands.Bot, ABC):
    def __init__(self, *args, **options):
        super().__init__(*args, **options)

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.INFO)
        log_formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s')

        file_handler = logging.FileHandler(filename='coolant.log', encoding='utf-8', mode='a')
        file_handler.setFormatter(log_formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        # Game Information (such as item data)
        with open("./data/game_info.json", "r") as f:
            self.GAME_INFO_DICT: dict = json.loads(f.read())

        self.ITEM_INFO_DICT: dict = self.GAME_INFO_DICT['items']

        # Game Data (such as players' inventories)
        with open("./store/game_data.json", "r") as f:
            self.game_data_dict: dict = json.loads(f.read())

    def save_data(self):
        with open('./store/game_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.game_data_dict, f, ensure_ascii=False, indent=2)

    # Get User Data and initialize if needed
    def get_user_data(self, user_id: int, reset=False) -> dict:
        if str(user_id) not in self.game_data_dict['users'] or reset:
            self.game_data_dict['users'][str(user_id)] = copy.deepcopy(self.GAME_INFO_DICT["default_user"])
            self.save_data()
        return self.game_data_dict['users'][str(user_id)]

    async def on_ready(self):
        self.logger.info(f'{self.user} has connected to Discord!')
