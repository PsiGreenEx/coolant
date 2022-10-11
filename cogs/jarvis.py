# jarvis.py
import random
import asyncio
from discord.ext import commands, tasks
# local modules
import coolant
from jarvis_processor import JarvisProcessor


class Jarvis(commands.Cog):
    def __init__(self, bot_client: coolant.CoolantBot, jarvis: JarvisProcessor):
        self.bot = bot_client
        self.offset_values.start()
        self.jarvis = jarvis

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

    @commands.command(name="value_update")
    async def value_update(self, context, user_id, value):
        if context.author.id == 244517712032825344:
            self.jarvis.update_value(user_id, int(value))
            await coolant.log_print(f"Manually updated {user_id} to value {value}.")

    @commands.command(name="dev_scan")
    async def dev_scan(self, context, user_id):
        if context.author.id == 244517712032825344:
            message = context.message
            await asyncio.sleep(0.5)
            await message.channel.send("Yes sir, commencing ball scan...")
            async with message.channel.typing():
                if not any(user_id in key for key in self.jarvis.ball_values):  # if there is not a value present
                    self.jarvis.update_value(user_id, random.randint(-50, 50))

                await asyncio.sleep(0.5)
                await message.channel.send(self.jarvis.ball_values[user_id][1])
