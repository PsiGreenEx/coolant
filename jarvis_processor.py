# jarvis_processor.py

import discord
import random
import asyncio
import json
# local modules
import coolant


class JarvisProcessor:
    def __init__(self):
        self.VALUE_CATEGORY = {
            "SUPERWACK": 0,
            "WACK": 1,
            "ZERO": 2,
            "SILLY": 3,
            "SUPERSILLY": 4
        }

        self.INFLATION_CHANCE = 0.001
        self.INFLATION_MULTIPLIER = 15
        self.SILLY_INCREASE_MARGIN = 10
        self.SILLY_DAMPENER = 0.5
        self.SILLY_MULTIPLIER = 2.0

        self.SCAN_READING = (" `{}%` wack.", " `{}%` silly.")

        self.VALUE_EXCLUSION = (
            "868744451244302346",
            "594323388705538069",
            "155149108183695360",
            "159985870458322944",
            "783772765962240022",
            "534589798267224065",
            "235088799074484224",
            "856326057400598590"
        )

        self.SPECIAL_VALUES = {
            "624738893543243786": (-3939, -39, 0, 39, 3939),  # smoothie
            "402026123086528518": (777, 77, 0, 77, 777),  # neo
            "517122589718741022": (3232, 32, 0, 23, 2323)   # 23prez
        }

        with open("data/messages.json", "r") as message_file:
            self.SCAN_MESSAGES = json.loads(message_file.read())

        with open("store/ball_values.json", "r") as values_file:
            self.ball_values = json.loads(values_file.read())

    def update_value(self, user_id, value):
        self.ball_values[user_id] = []
        self.ball_values[user_id].append(value)
        is_excluded = user_id in self.VALUE_EXCLUSION
        has_messages = any(user_id in key for key in self.SCAN_MESSAGES)
        shown_value = value

        # determine value category
        if value <= -100:
            category_value = self.VALUE_CATEGORY["SUPERWACK"]
        elif -100 < value < 0:
            category_value = self.VALUE_CATEGORY["WACK"]
        elif value == 0:
            category_value = self.VALUE_CATEGORY["ZERO"]
        elif 0 < value < 100:
            category_value = self.VALUE_CATEGORY["SILLY"]
        else:
            category_value = self.VALUE_CATEGORY["SUPERSILLY"]

        # determine static values
        if any(user_id in key for key in self.SPECIAL_VALUES):
            shown_value = self.SPECIAL_VALUES[user_id][category_value]

        # apply value and message
        if category_value == self.VALUE_CATEGORY["SUPERWACK"]:
            if has_messages and len(self.SCAN_MESSAGES[user_id][0]) != 0: message = random.choice(self.SCAN_MESSAGES[user_id][0])
            else: message = self.SCAN_MESSAGES["0"][0][0]
            if not is_excluded: message = message + self.SCAN_READING[0].format(abs(shown_value))
        elif category_value == self.VALUE_CATEGORY["WACK"]:
            if has_messages and len(self.SCAN_MESSAGES[user_id][1]) != 0: message = random.choice(self.SCAN_MESSAGES[user_id][1])
            else: message = self.SCAN_MESSAGES["0"][1][0]
            if not is_excluded: message = message + self.SCAN_READING[0].format(abs(shown_value))
        elif category_value == self.VALUE_CATEGORY["ZERO"]:
            if has_messages and len(self.SCAN_MESSAGES[user_id][2]) != 0: message = random.choice(self.SCAN_MESSAGES[user_id][2])
            else: message = self.SCAN_MESSAGES["0"][2][0]
        elif category_value == self.VALUE_CATEGORY["SILLY"]:
            if has_messages and len(self.SCAN_MESSAGES[user_id][3]) != 0: message = random.choice(self.SCAN_MESSAGES[user_id][3])
            else: message = self.SCAN_MESSAGES["0"][3][0]
            if not is_excluded: message = message + self.SCAN_READING[1].format(shown_value)
        else:
            if has_messages and len(self.SCAN_MESSAGES[user_id][4]) != 0: message = random.choice(self.SCAN_MESSAGES[user_id][4])
            else: message = self.SCAN_MESSAGES["0"][4][0]
            if not is_excluded: message = message + self.SCAN_READING[1].format(shown_value)

        self.ball_values[user_id].append(message)
        with open('store/ball_values.json', 'w', encoding='utf-8') as f:
            json.dump(self.ball_values, f, ensure_ascii=False, indent=2)

    async def jarvis_command(self, message: discord.Message, command: str):
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
                    await coolant.log_print(f"{message.author.id} used generic ball scan.")
                    return

                if not any(scan_id in key for key in self.ball_values):  # if there is not a value present
                    self.update_value(scan_id, random.randint(-50, 50))

                await asyncio.sleep(2)
                await message.channel.send(self.ball_values[scan_id][1])
                await coolant.log_print(f"{message.author.id} scanned {scan_id}'s balls.")
        elif "modsuit" in command:  # modsuit command
            await asyncio.sleep(0.5)
            await message.channel.send("Sir, in 2021.")
        elif "create new vc" in command:  # create new vc
            await asyncio.sleep(0.5)
            await message.channel.send("The \"create new vc\" channel is ready for you, sir.")
