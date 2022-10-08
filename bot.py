# bot.py
import json

import discord
import random
import asyncio
from discord.ext import commands
# local modules
from log_print import log_print
from admin import Admin
from misc import Miscellaneous
from jarvis import Jarvis, jarvis_command
from voice_channels import VoiceChannels
from game import Games

intents = discord.Intents.all()

with open("data/bot_data.json", "r") as bot_data_file:
    bot_data: dict = json.loads(bot_data_file.read())
    TOKEN = bot_data["token"]
    CREATE_CHANNEL_ID = bot_data["voice_chat_id"]
    JOIN_CHANNEL_ID = bot_data["join_channel_id"]
    MEMBER_ROLE_ID = bot_data["member_role_id"]

prefix = '.'
client = commands.Bot(command_prefix=prefix, intents=intents, debug_guilds=[bot_data['alloy_guild_id'], bot_data['bot_test_guild_id']])

client.remove_command("help")

PHRASE_CHANCE = 0.02
REPEATS_NEEDED = 2

with open("data/reactions.json", 'r') as reactions_file:
    reactions_dict = json.loads(reactions_file.read())
    PHRASE_DICT = reactions_dict["phrases"]
    REACT_DICT = reactions_dict["reactions"]

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

    if repeat_message_count == REPEATS_NEEDED and message.content != "":
        async with message.channel.typing():
            await asyncio.sleep(1)
            await message.channel.send(message.content)

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


if __name__ == "__main__":
    # Run the client
    client.add_cog(Admin(client))
    client.add_cog(Miscellaneous(client, JOIN_CHANNEL_ID, MEMBER_ROLE_ID))
    client.add_cog(Jarvis(client))
    client.add_cog(VoiceChannels(client, CREATE_CHANNEL_ID, MEMBER_ROLE_ID))
    client.add_cog(Games(client))
    client.run(TOKEN)
