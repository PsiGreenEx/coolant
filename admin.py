# admin.py

import discord
import random
from datetime import datetime
from discord.ext import commands
# local modules
from log_print import log_print

# Put a user ID as any of these variables to target it.
admin = 688115255301242919
access_list = [admin, 244517712032825344]

# Status dictionary
status_movies = [
    "Iron Man",
    "Iron Man 2",
    "Iron Man 3",
    "Finding Nemo 11",
    "Spaceballs",
    "1992 space movie",
    "family guy",
    "Dragon Ball",
    "Dragon Ball Z",
    "Dragon Ball GT",
    "Dragon Ball Z Kai",
    "Dragon Ball Super",
    "Dragon Ball Super: Broly",
    "a pornography starring your mother",
    "you sleep!",
    "you always!",
    "danny devito make pasta",
    "cock rating 1!",
    "cock rating 2!",
    "cock rating 2 reloaded!",
    "cock rating 3!",
    "cock rating 4!",
    "cock rating 5!",
    "cock rating 6!",
    "cock rating 7!",
    "cock rating 8!",
    "cock rating 9!",
    "cock rating 10!",
    "cock rating 99!",
    "balls rating!",
    "balls rating 2!",
    "for bopa; death on sight",
    "seha make great brownies",
    "seha make pizza",
    "for the pizza",
    "for omori gifs; death on sight",
    "for mittence; do the funny voice",
    "the alloy discord server",
    "odin make Burnout",
    "smoothie art stream",
    "vlad make AlloyDungeon",
    "alloy direct",
    "alloy direct unofficial pre-show",
    "psi make AlloyAdventures",
    "Ulysses 31",
    "alloy direct 2022"
]


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
        if context.author.id == admin:
            mention_id = context.mentions[0].id
            access_list.append(mention_id)
            await context.message.delete()
            await log_print(f"Gave \"{str(mention_id)}\" permissions!")

    @commands.command(name='deop')
    async def deop(self, context):
        if context.author.id == admin:
            mention_id = context.mentions[0].id
            access_list.remove(mention_id)
            await context.message.delete()
            await log_print(f"Took away \"{str(mention_id)}\"'s permissions!")
