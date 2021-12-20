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
from music import Music
from admin import Admin
from misc import Miscellaneous

prefix = '.'
client = commands.Bot(command_prefix=prefix)

client.remove_command("help")

# Uses a .env to access its discord token to prevent token stealing.
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

PHRASE_CHANCE = 0.01
INFLATION_CHANCE = 0.02

# Balls message dictionary
SCAN_MESSAGES = {
    "688115255301242919": ["Leafesque's balls are massive. They read as {} wack, sir.",2], # Leafesque
    "517122589718741022": ["23rd President's balls are `23%` wack, sir.",0], # 23
    "221756292862050314": ["Afanguy's balls are `0%` wack, sir.",0], # Afanguy
    "546400083311067137": ["Seha's balls are enormous, sir. Readings say {} wack.",12], # Seha
    "593223812980670493": ["Bug's balls are filled with Monster Energy Drink. {} wack, sir.",63], # Buggy
    "436985877806317586": ["Callisuni's balls are from space, referred to as spaceballs. Readings say {} wack.",30], # Calli
    "346393655432445954": ["Redditor balls, sir. Readings show {} wack.",3], # chickenblitz
    "703732414119411792": ["Turkish balls, sir. Readings show {} wack.",0], # coffee
    "318151890405687296": ["Furry balls, sir. {} wack, readings show.",103], # dopa
    "242220086713122816": ["His balls are deep, sir. Readings show {} wack.",37], # grey
    "645668447967117332": ["His balls wack, sir. They seem to like men. Readings show {} wack.",24], # kazooby
    "665882081343307794": ["Apologies sir, his balls are too tiny to scan.",0], # pan
    "306966483911704586": ["Loli in username, sir.",0], # onigiri
    "454735636956577803": ["Balls slightly wack, sir. Readings show {} wack.",17], # Lucas
    "538479146679140362": ["Greek balls, sir. {} wack.",67], # Lucent
    "441052235967889430": ["I cannot get a full scan, as the scanning radius is seemingly moon-sized. My estimations are {} wack, sir.",17], # Mittence
    "402026123086528518": ["His balls are holy, sir. `77%` wack.",0], # Neo
    "244517712032825344": ["Readings show {} wack, sir. The reading spikes past 8PM.",27], # Psi
    "453227223693131777": ["Racist balls, sir. Readings show {} wack.",37], # psp
    "288481819173584898": ["Inconsistent balls, sir. Readings say {} wack.",85], # shroedinger
    "624738893543243786": ["Worldbuilder balls, sir. `39%` wack.",0], # smoothie
    "538182631074955294": ["Rubber balls, sir. {} wack.",13], # odin
    "169564270277820417": ["His balls have Thaumcraft taint, sir. Readings say {} wack.",47], # vlad
    "607408346668204032": ["Their ball hair seems to be attributed to someone named 'Gabe', sir. Readings say {} wack.",50], # xenza
    "328118566299631616": ["Emerald balls, sir. {} wack, sir.",26], # yormit
    "328697009068310531": ["Lawyer balls, sir. {} wack.",12], # pina"
    "670854196584513559": ["I must warn you that this is the infamous Charles Cavet, known sex trafficker. He uses an alias so he's never been caught. He uses Planet Minecraft and \"minecraft but\" datapacks in his operations regularly. Readings say {} wack, sir.",83], # ccavet
    "721758349313441864": ["Only detecting balls in spirit. {} wack, sir.",28], # beans
    "877303149461930034": ["Readings show close relation to worldbuiling. {} wack, sir.",26], # crete greece
    "562800486189760514": ["Some real [[pipis]] balls. {} wack, sir.",36], # tanjo
    "792893341217718283": ["Very cool balls. {} wack, sir.",8], # omega
    "381193469034496012": ["Hints of cannabis in his balls. {} wack, sir.",79], # stoner sudowoodo
    "477069775944810496": ["Artist balls. {} wack, sir.",9], # onion
    "206464430047887362": ["A League of Legends player. Readings say {} wack, sir.",83], #paul
    "395977824768360458": ["Exquisite balls, sir. {} wack.",15], # godot
    "399652203133927427": ["Who? {} wack, I think...",50], # gonc
    "458872384221347849": ["Yummy. {} wack, sir.",40], # ham sandwich
    "856326057400598590": ["Subscribe to Stardust Fantasy.",0], # stardust fantasy

    # Bots
    "868744451244302346": ["My database contains all possible balls in the universe, making them the most wack balls, sir.", 0],  # coolant
    "594323388705538069": ["Balls of all colors, sir.",0], # Lexa
    "155149108183695360": ["The balls of our robot overlord, sir.",0], # Dyno
    "159985870458322944": ["Stupid fucking balls, sir.",0], # MEE6
    "783772765962240022": ["These balls seem to only work half the time, sir",0], # Tempy
    "534589798267224065": ["https://cdn.discordapp.com/attachments/699684376715460628/905262129530175558/dragon-ball-super-goku-shocked-1240697.png",0], # Rank
    "235088799074484224": ["These balls have been crushed, sir. There is trace amounts of Youtube TOS left on the remnants.",0] # Rhythm
}

# Phrase response dictionary
PHRASE_DICT = {
    "zamn": "SHE'S 12?",
    "minecraft - snapshot": "holy shit, a snapshot!"
}

# Phrase reaction dictionary
REACT_DICT = {
    "joker": 856994037424586752,
    "cat": 827223066241007674,
    "watching you": 875142471808602112,
    "bingqining": 888508047100633161,
    "whaaa": 779359149791903784,
    "artifact": 749095975112671312,
    "hypothetically": 851547872889405470,
    "keeradance": 708317460578959360,
    "coolant sucks": 809916658214895666
}


# Ready
@client.event
async def on_ready():
    await log_print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    scrubbed_message = message.content.lower().replace(' ', '')

    if message.author == client.user:
        return
    
    if message.channel.type == discord.ChannelType.private:
        await message.channel.send("Shut the fuck up, you stupid bitch!")
        return

    author_name = message.author

    # Jarvis
    # Generic Scan
    if scrubbed_message == 'jarvis,scanthisguysballs' and message.reference is None:
        await log_print(f"{author_name} used generic scan.")
        await asyncio.sleep(0.5)
        await message.channel.send("Yes sir, commencing ball scan...")
        async with message.channel.typing():
            await asyncio.sleep(2)
            await message.channel.send("Their balls wack, sir.")
    # Specific Scan
    elif ('jarvis,scantheballsof' in scrubbed_message and len(message.mentions) == 1 and message.reference is None) or \
            (scrubbed_message == 'jarvis,scanthisguysballs' and message.reference is not None) or \
            (scrubbed_message == 'jarvis,scanmyballs' and message.reference is None):
        await log_print(f"{author_name} used specific scan...")
        await asyncio.sleep(0.5)
        await message.channel.send("Yes sir, commencing ball scan...")

        async with message.channel.typing():
            await asyncio.sleep(2)

            # If the message mentioned someone directly
            if len(message.mentions) == 1:
                mention_id = str(message.mentions[0].id)
                await log_print(f"{author_name} scanned {message.mentions[0]}")
            # If the message is replying to a message
            elif message.reference is not None:
                mention_id = str(message.reference.resolved.author.id)
                await log_print(f"{author_name} scanned {message.reference.resolved.author}")
            # If they scanned themselves
            elif message.reference is None:
                mention_id = str(message.author.id)
                await log_print(f"{author_name} scanned themself.")
            # If all else fails
            else:
                response = "Scan failed, sir. Please tell Psi about this."
                await log_print(f"{author_name}'s scan failed!")
        
            if any(mention_id in key for key in SCAN_MESSAGES):
                random_percentage = max(SCAN_MESSAGES[mention_id][1] + random.randint(-15, 15), 0)

                if random.random() <= INFLATION_CHANCE:
                    random_percentage + random.randint(500, 50000)

                if mention_id == "244517712032825344" and (datetime.now().hour >= 20 or datetime.now().hour <= 6):  # 8pm psi
                    random_percentage *= 3

                response = SCAN_MESSAGES[mention_id][0].format(f"`{str(random_percentage)}%`")
            # Send generic message if user isn't in the list
            else:
                response = f"Their balls wack, sir. Readings show `{str(random.randint(0, 100))}%` wack."

            await message.channel.send(response)
    # Gif Reply
    elif scrubbed_message == 'https://tenor.com/view/jarvis-gif-21248397':
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
client.add_cog(Music(client))
client.run(TOKEN)
