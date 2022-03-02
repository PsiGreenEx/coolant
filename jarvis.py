# jarvis.py
import discord
import random
import asyncio
import json
from discord.ext import commands, tasks
# local modules
from log_print import log_print

VALUE_CATEGORY = {
    "SUPERWACK": 0,
    "WACK": 1,
    "ZERO": 2,
    "SILLY": 3,
    "SUPERSILLY": 4
}

INFLATION_CHANCE = 0.01
INFLATION_MULTIPLIER = 15
SILLY_CHANGE_TIME = 5  # in minutes
SILLY_INCREASE_MARGIN = 10
SILLY_DAMPENER = 0.5
SILLY_MULTIPLIER = 2.0

SCAN_READING = (" `{}%` wack.", " `{}%` silly.")
VALUE_EXCLUSION = (
    "868744451244302346",
    "594323388705538069",
    "155149108183695360",
    "159985870458322944",
    "783772765962240022",
    "534589798267224065",
    "235088799074484224",
    "856326057400598590"
)
SPECIAL_VALUES = {
    "624738893543243786": (9393, 93, 0, 39, 3939),  # smoothie
    "402026123086528518": (777, 77, 0, 77, 777),  # neo
    "517122589718741022": (3232, 32, 0, 23, 2323)   # 23prez
}

with open("messages.json", "r") as message_file:
    SCAN_MESSAGES = json.loads(message_file.read())

ball_values = {}


def update_value(user_id, value):
    ball_values[user_id] = []
    ball_values[user_id].append(value)
    is_excluded = user_id in VALUE_EXCLUSION
    has_messages = any(user_id in key for key in SCAN_MESSAGES)
    shown_value = value

    # determine value category
    if value < -100:
        category_value = VALUE_CATEGORY["SUPERWACK"]
    elif -100 < value < 0:
        category_value = VALUE_CATEGORY["WACK"]
    elif value == 0:
        category_value = VALUE_CATEGORY["ZERO"]
    elif 0 < value < 100:
        category_value = VALUE_CATEGORY["SILLY"]
    else:
        category_value = VALUE_CATEGORY["SUPERSILLY"]

    # determine static values
    if any(user_id in key for key in SPECIAL_VALUES):
            shown_value = SPECIAL_VALUES[user_id][category_value]

    # apply value and message
    if category_value == VALUE_CATEGORY["SUPERWACK"]:
        if has_messages and len(SCAN_MESSAGES[user_id][0]) != 0: message = random.choice(SCAN_MESSAGES[user_id][0])
        else: message = SCAN_MESSAGES["0"][0][0]
        if not is_excluded: message = message + SCAN_READING[0].format(abs(shown_value))
    elif category_value == VALUE_CATEGORY["WACK"]:
        if has_messages and len(SCAN_MESSAGES[user_id][1]) != 0: message = random.choice(SCAN_MESSAGES[user_id][1])
        else: message = SCAN_MESSAGES["0"][1][0]
        if not is_excluded: message = message + SCAN_READING[0].format(abs(shown_value))
    elif category_value == VALUE_CATEGORY["ZERO"]:
        if has_messages and len(SCAN_MESSAGES[user_id][2]) != 0: message = random.choice(SCAN_MESSAGES[user_id][2])
        else: message = SCAN_MESSAGES["0"][2][0]
    elif category_value == VALUE_CATEGORY["SILLY"]:
        if has_messages and len(SCAN_MESSAGES[user_id][3]) != 0: message = random.choice(SCAN_MESSAGES[user_id][3])
        else: message = SCAN_MESSAGES["0"][3][0]
        if not is_excluded: message = message + SCAN_READING[1].format(shown_value)
    else:
        if has_messages and len(SCAN_MESSAGES[user_id][4]) != 0: message = random.choice(SCAN_MESSAGES[user_id][4])
        else: message = SCAN_MESSAGES["0"][4][0]
        if not is_excluded: message = message + SCAN_READING[1].format(shown_value)

    ball_values[user_id].append(message)


async def jarvis_command(message: discord.Message, command: str):
    # ball scanning
    if "balls" in command and "scan" in command:
        await asyncio.sleep(0.5)
        await message.channel.send("Yes sir, commencing ball scan...")
        async with message.channel.typing():
            if message.reference is not None:  # if replying to message
                scan_id = str(message.reference.resolved.author.id)
            elif len(message.mentions) > 0:  # if mentions person
                scan_id = str(message.mentions[0].id)
            elif "my" in command:  # if self scan
                scan_id = str(message.author.id)
            else:  # if no one is scanned
                await asyncio.sleep(2)
                await message.channel.send("Their balls wack, sir.")
                await log_print(f"{message.author.id} used generic ball scan.")
                return

            if not any(scan_id in key for key in ball_values):  # if there is not a value present
                update_value(scan_id, random.randint(-50, 50))

            await asyncio.sleep(2)
            await message.channel.send(ball_values[scan_id][1])
            await log_print(f"{message.author.id} scanned {scan_id}'s balls.")
    elif "modsuit" in command:  # modsuit command
        await asyncio.sleep(0.5)
        await message.channel.send("Sir, in 2021.")


class Jarvis(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.offset_values.start()

    @tasks.loop(minutes=SILLY_CHANGE_TIME)
    async def offset_values(self):
        for key, data in ball_values.items():
            value: int = data[0]
            if value < -100:
                top_offset = SILLY_MULTIPLIER
                bottom_offset = SILLY_DAMPENER
            elif value > 100:
                bottom_offset = SILLY_MULTIPLIER
                top_offset = SILLY_DAMPENER
            else:
                bottom_offset = 1
                top_offset = 1
            offset = random.randint(-SILLY_INCREASE_MARGIN * bottom_offset, SILLY_INCREASE_MARGIN * top_offset)
            if random.random() <= INFLATION_CHANCE:
                print("INFLATED!")
                offset = offset * INFLATION_MULTIPLIER
            update_value(key, value + offset)

    @offset_values.before_loop
    async def before_offset_loop(self):
        await self.client.wait_until_ready()

    @commands.command(name="value_update")
    async def value_update(self, context, user_id, value):
        if context.author.id == 244517712032825344:
            global ball_values
            update_value(user_id, int(value))
            await log_print(f"Manually updated {user_id} to value {value}.")

    @commands.command(name="dev_scan")
    async def dev_scan(self, context, user_id):
        if context.author.id == 244517712032825344:
            message = context.message
            await asyncio.sleep(0.5)
            await message.channel.send("Yes sir, commencing ball scan...")
            async with message.channel.typing():
                if not any(user_id in key for key in ball_values):  # if there is not a value present
                    update_value(user_id, random.randint(-50, 50))

                await asyncio.sleep(0.5)
                await message.channel.send(ball_values[user_id][1])
