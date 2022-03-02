# bot.py

import os
import discord
import random
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands
# local modules
from log_print import log_print
from admin import Admin
from misc import Miscellaneous
from jarvis import Jarvis, jarvis_command
from voice_channels import VoiceChannels

prefix = '.'
client = commands.Bot(command_prefix=prefix)

client.remove_command("help")

# Uses a .env to access its discord token to prevent token stealing.
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CREATE_CHANNEL_ID = int(os.getenv('VOICE_CHAT_ID'))

PHRASE_CHANCE = 0.01
REPEATS_NEEDED = 2

# Phrase response dictionary
PHRASE_DICT = {
    "zamn": "SHE'S 12?",
    "minecraft - snapshot": "holy shit, a snapshot!"
}

# Phrase reaction dictionary
REACT_DICT = {
    "joker": 856994037424586752,
    "kitten": 827223066241007674,
    "watching you": 875142471808602112,
    "bingqining": 888508047100633161,
    "whaaa": 779359149791903784,
    "artifact": 749095975112671312,
    "hypothetically": 851547872889405470,
    "keeradance": 708317460578959360,
    "coolant sucks": 809916658214895666
}

repeat_message = ""
repeat_message_author = ""
repeat_message_count = 0

# Ready
@client.event
async def on_ready():
    await log_print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    message_content: str = message.content.lower()

    if message.author == client.user:
        return
    
    if message.channel.type == discord.ChannelType.private:
        await message.channel.send("Shut the fuck up, you stupid bitch!")
        return

    author_name = message.author

    # Message Repetition
    global repeat_message
    global repeat_message_author
    global repeat_message_count

    if message.content == repeat_message and author_name != repeat_message_author:
        repeat_message_count = repeat_message_count + 1
    else:
        repeat_message_count = 0

    if repeat_message_count == REPEATS_NEEDED:
        async with message.channel.typing():
            await asyncio.sleep(1)
            await message.channel.send(repeat_message)

    repeat_message = message.content
    repeat_message_author = author_name

    # Jarvis
    if message_content.startswith("jarvis,"): await jarvis_command(message, message_content.split(" ", 1)[1])
    # Gif Reply
    elif message_content == 'https://tenor.com/view/jarvis-gif-21248397':
        await asyncio.sleep(1)
        await message.reply("https://tenor.com/view/jarvis-gif-21248407")
    
    # Responses
    if random.random() <= PHRASE_CHANCE:
        for key in PHRASE_DICT:
            if key in message.content.lower():
                await message.reply(PHRASE_DICT[key])
                await log_print(f"Auto replied to {key} with {PHRASE_DICT[key]}")
                break

    # Reactions
    for key in REACT_DICT:
        if key in message.content.lower():
            await message.add_reaction(client.get_emoji(REACT_DICT[key]))
            await log_print(f"Auto reacted to {key} with emoji {REACT_DICT[key]}.")
    
    await client.process_commands(message)


# Run the client
client.add_cog(Admin(client))
client.add_cog(Miscellaneous(client))
client.add_cog(Jarvis(client))
client.add_cog(VoiceChannels(client, CREATE_CHANNEL_ID))
client.run(TOKEN)
