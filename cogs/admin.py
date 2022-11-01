# admin.py

import json
import logging
import discord
import random
from discord.ext import commands
# local modules
import coolant


class Admin(commands.Cog):
    def __init__(self, bot_client: coolant.CoolantBot):
        self.bot = bot_client
        self.logger = logging.getLogger('discord')

        # admin command access
        with open("./data/bot_data.json", 'r') as bot_data_file:
            self.ADMIN_LIST: list = json.loads(bot_data_file.read())["admin_access_list"]

        # Status list
        with open("./data/status_movies.json", 'r') as status_movies_file:
            self.status_movies: list = json.loads(status_movies_file.read())

    @commands.command(name="s")
    async def say(self, context):
        if context.author.id in self.ADMIN_LIST:
            text = context.message.content.replace(".s", "")
            await context.send(text)
            await context.message.delete()
            self.logger.info(f"{context.author} said \"{text}\"")

    @commands.slash_command(
        name="changestatus",
        description="Coolant Admin: Change the status of coolant.",
        options=[
            discord.Option(
                int,
                name="choice",
                description="The index of the status message. Leave blank for random.",
                default=-1
            )
        ]
    )
    async def change_status(self, context: discord.ApplicationContext, choice: int):
        if context.author.id not in self.ADMIN_LIST:
            await context.interaction.response.send_message(content="Improper perms!", ephemeral=True)
            return

        if choice == -1:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(self.status_movies)))
        else:
            await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=self.status_movies[choice]))

        await context.interaction.response.send_message(content="Status changed.", ephemeral=True)
        self.logger.info("Switched status message!")
