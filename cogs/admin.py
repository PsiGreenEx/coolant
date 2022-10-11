# admin.py

import json
import discord
import random
from discord.ext import commands
# local modules
import coolant


class Admin(commands.Cog):
    def __init__(self, client: coolant.CoolantBot):
        self.client = client

        # admin command access
        with open("./data/bot_data.json", 'r') as bot_data_file:
            self.access_list: list = json.loads(bot_data_file.read())["admin_access_list"]

        # Status list
        with open("./data/status_movies.json", 'r') as status_movies_file:
            self.status_movies: list = json.loads(status_movies_file.read())

    @commands.command(name="s")
    async def say(self, context):
        if context.author.id in self.access_list:
            text = context.message.content.replace(".s", "")
            await context.send(text)
            await context.message.delete()
            await coolant.log_print(f"Said \"{text}\"")

    @commands.command(name="cst")
    async def change_status(self, context, choice=-1):
        if context.author.id in self.access_list:
            if choice == -1:
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(self.status_movies)))
            else:
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=self.status_movies[choice]))
            await context.message.delete()
            await coolant.log_print("Switched status message!")

    @commands.command(name='op')
    async def op(self, context):
        if context.author.id in self.access_list:
            mention_id = context.mentions[0].id
            self.access_list.append(mention_id)
            await context.message.delete()
            await coolant.log_print(f"Gave \"{str(mention_id)}\" permissions!")

    @commands.command(name='deop')
    async def deop(self, context):
        if context.author.id in self.access_list:
            mention_id = context.mentions[0].id
            self.access_list.remove(mention_id)
            await context.message.delete()
            await coolant.log_print(f"Took away \"{str(mention_id)}\"'s permissions!")
