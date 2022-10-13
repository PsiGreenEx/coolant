# jarvis.py

import json
import random
import asyncio
import discord
from discord.ext import commands, tasks
# local modules
import coolant
from jarvis_processor import JarvisProcessor


class Jarvis(commands.Cog):
    def __init__(self, bot_client: coolant.CoolantBot, jarvis: JarvisProcessor):
        self.bot = bot_client
        self.offset_values.start()
        self.jarvis = jarvis

        with open("./data/bot_data.json", "r") as f:
            bot_data = json.loads(f.read())
            self.ADMIN_LIST: list[int] = bot_data["admin_access_list"]

    @tasks.loop(minutes=5)
    async def offset_values(self):
        for key, data in self.jarvis.ball_values.items():
            value: int = data[0]
            if value < -100:
                top_offset = self.jarvis.SILLY_MULTIPLIER
                bottom_offset = self.jarvis.SILLY_DAMPENER
            elif value > 100:
                bottom_offset = self.jarvis.SILLY_MULTIPLIER
                top_offset = self.jarvis.SILLY_DAMPENER
            else:
                bottom_offset = 1
                top_offset = 1
            offset = random.randint(-self.jarvis.SILLY_INCREASE_MARGIN * bottom_offset, self.jarvis.SILLY_INCREASE_MARGIN * top_offset)
            if random.random() <= self.jarvis.INFLATION_CHANCE:
                print("INFLATED!")
                offset = offset * self.jarvis.INFLATION_MULTIPLIER
            self.jarvis.update_value(key, value + offset)

    @offset_values.before_loop
    async def before_offset_loop(self):
        await self.bot.wait_until_ready()

    @commands.slash_command(
        name="valueupdate",
        description="Coolant Admin: Update someone's ball wack/silly value.",
        options=[
            discord.Option(
                discord.User,
                name="user",
                description="User whose balls' value to update."
            ),
            discord.Option(
                int,
                name="value",
                description="The value to set."
            )
        ]
    )
    async def value_update(self, context: discord.ApplicationContext, user: discord.User, value: int):
        if context.author.id not in self.ADMIN_LIST:
            await context.interaction.response.send_message("Improper perms!", ephemeral=True)
            return

        self.jarvis.update_value(str(user.id), int(value))
        response = await context.respond("Value updated.")
        await coolant.log_print(f"Manually updated {user}'s balls to value {value}.")

        await response.delete_original_response(delay=3)

    @commands.slash_command(
        name="devscan",
        description="Coolant Admin: Perform a quick scan.",
        options=[
            discord.Option(
                discord.User,
                name="user",
                description="The user to scan."
            )
        ]
    )
    async def dev_scan(self, context: discord.ApplicationContext, user: discord.User):
        if context.author.id not in self.ADMIN_LIST:
            await context.interaction.response.send_message("Improper perms!", ephemeral=True)
            return

        await context.respond("Yes sir, commencing ball scan...")
        async with context.channel.typing():
            if not any(str(user.id) in key for key in self.jarvis.ball_values):  # if there is not a value present
                self.jarvis.update_value(str(user.id), random.randint(-50, 50))
            await asyncio.sleep(0.5)
            await context.send_followup(self.jarvis.ball_values[str(user.id)][1])
