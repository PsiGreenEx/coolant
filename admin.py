# admin.py
import json

import discord
import random
from discord.ext import commands
# local modules
from log_print import log_print

# admin command access
with open("data/bot_data.json", 'r') as bot_data_file:
    access_list: list = json.loads(bot_data_file.read())["admin_access_list"]

# Status list
with open("data/status_movies.json", 'r') as status_movies_file:
    status_movies: list = json.loads(status_movies_file.read())


class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="s")
    async def say(self, context):
        if context.author.id in access_list:
            text = context.message.content.replace(".s", "")
            await context.send(text)
            await context.message.delete()
            await log_print(f"Said \"{text}\"")

    @commands.command(name="cst")
    async def change_status(self, context, choice=-1):
        if context.author.id in access_list:
            if choice == -1:
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(status_movies)))
            else:
                await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status_movies[choice]))
            await context.message.delete()
            await log_print("Switched status message!")

    @commands.command(name='op')
    async def op(self, context):
        if context.author.id == access_list:
            mention_id = context.mentions[0].id
            access_list.append(mention_id)
            await context.message.delete()
            await log_print(f"Gave \"{str(mention_id)}\" permissions!")

    @commands.command(name='deop')
    async def deop(self, context):
        if context.author.id == access_list:
            mention_id = context.mentions[0].id
            access_list.remove(mention_id)
            await context.message.delete()
            await log_print(f"Took away \"{str(mention_id)}\"'s permissions!")
