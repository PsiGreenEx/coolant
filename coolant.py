# coolant.py

import logging
import json
from abc import ABC
import discord
from discord.ext import commands
import random
import asyncio
from datetime import datetime
# local modules
from processors.jarvis import JarvisProcessor
from processors.permion import PermionProcessor


class CoolantBot(commands.Bot, ABC):
    def __init__(self, jarvis: JarvisProcessor, permion_processor: PermionProcessor, *args, **options):
        super().__init__(*args, **options)
        self.PHRASE_CHANCE = 0.02
        self.REPEATS_NEEDED = 2
        self.repeat_message = ""
        self.repeat_message_author = ""
        self.repeat_message_count = 0

        self.jarvis = jarvis
        self.permion_processor = permion_processor

        with open("data/reactions.json", 'r') as reactions_file:
            reactions_dict = json.loads(reactions_file.read())
            self.PHRASE_DICT = reactions_dict["phrases"]
            self.REACT_DICT = reactions_dict["reactions"]

        self.logger = logging.getLogger('discord')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename='coolant.log', encoding='utf-8', mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        self.logger.addHandler(handler)

    async def log_print(self, text: str):
        print('[' + datetime.now().strftime("%x %X") + '] ' + text)
        self.logger.info(text)

    async def on_ready(self):
        await self.log_print(f'{self.user} has connected to Discord!')

    async def on_message(self, message: discord.Message):
        message_content: str = message.content.lower()

        if message.author == self.user:
            return

        author_name = message.author

        # Permion Activation
        role_data = load_role_data()

        try:
            user_role_data: dict or None = role_data[str(message.author.id)]
        except KeyError:
            user_role_data = None

        if user_role_data and user_role_data['permion'] and user_role_data['keyword']:
            if user_role_data['keyword'] in message.content:
                await self.permion_processor.activate_permion(user_role_data, message)

        # Message Repetition
        if message.content == self.repeat_message and author_name != self.repeat_message_author:
            self.repeat_message_count += 1
        else:
            self.repeat_message_count = 0

        if self.repeat_message_count == self.REPEATS_NEEDED and message.content != "":
            async with message.channel.typing():
                await asyncio.sleep(1)
                await message.channel.send(message.content)

        self.repeat_message = message.content
        self.repeat_message_author = author_name

        # Jarvis
        if message_content.startswith("jarvis,"):
            await self.jarvis.jarvis_command(message, message_content.split(" ", 1)[1])

        # Gif Reply
        elif message_content == 'https://tenor.com/view/jarvis-gif-21248397':
            await asyncio.sleep(1)
            await message.reply("https://tenor.com/view/jarvis-gif-21248407")

        # Responses
        if random.random() <= self.PHRASE_CHANCE:
            for key in self.PHRASE_DICT:
                if key in message.content.lower():
                    await message.reply(self.PHRASE_DICT[key])
                    await self.log_print(f"Auto replied to {key} with {self.PHRASE_DICT[key]}")
                    break

        # Reactions
        for key in self.REACT_DICT:
            if key in message.content.lower():
                await message.add_reaction(self.get_emoji(self.REACT_DICT[key]))
                await self.log_print(f"Auto reacted to {key} with emoji {self.REACT_DICT[key]}.")

        await self.process_commands(message)


def load_role_data() -> dict:
    with open("./store/roles.json", 'r') as f:
        return json.loads(f.read())


def save_role_data(role_data: dict):
    with open("./store/roles.json", "w") as f:
        json.dump(role_data, f, ensure_ascii=False, indent=2)
