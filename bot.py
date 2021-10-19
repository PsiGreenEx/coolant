# bot.py
import os
import discord
import random
import time
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands
from discord.utils import get
prefix = '.'
client = commands.Bot(command_prefix=prefix)
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
    "a pornography starring your mother.",
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
    "yormit make shit brownies",
    "seha make great brownies",
    "seha make pizza",
    "for the pizza",
    "for omori gifs; death on sight",
    "for mittence; do the funny voice",
    "the alloy discord server",
    "odin make Burnout",
    "vlad make AlloyDungeon"
]

# Uses a .env to access it's discord token to prevent token stealing.
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PHRASE_CHANCE = 0.01

# Put a user ID as any of these variables to target it.
admin = 688115255301242919
ACCESS_list = [admin, 244517712032825344]

# Balls message dictionary
scan_messages = {
    "688115255301242919": ["Leafesque's balls are massive. They read as `percent` wack, sir.",2], # Leafesque
    "517122589718741022": ["23rd President's balls are `23%` wack, sir.",0], # 23
    "221756292862050314": ["Afanguy's balls are `0%` wack, sir.",0], # Afanguy
    "546400083311067137": ["Seha's balls are enormous, sir. Readings say `percent` wack.",12], # Seha
    "593223812980670493": ["Bug's balls are seemingly irrelevant to the context, sir.",0], # Buggy
    "436985877806317586": ["Callisuni's balls are from space, referred to as spaceballs. Readings say `percent` wack.",30], # Calli
    "346393655432445954": ["Redditor balls, sir. Readings show `percent` wack.",3], # chickenblitz
    "347198887309869078": ["His balls wack, sir. Readings say `percent` wack.",57], # winna
    "703732414119411792": ["Turkish balls, sir. Readings show `percent` wack.",0], # coffee
    "868744451244302346": ["My database contains all possible balls in the universe, making them the most wack balls, sir.",0], # coolant
    "318151890405687296": ["Furry balls, sir. `percent` wack, readings show.",103], # dopa
    "242220086713122816": ["His balls are deep, sir. Readings show `percent` wack.",37], # grey
    "645668447967117332": ["His balls wack, sir. They seem to like men. Readings show `percent` wack.",24], # kazooby
    "665882081343307794": ["Apologies sir, his balls are too tiny to scan.",0], # pan
    "306966483911704586": ["Loli in username, sir.",0], # onigiri
    "454735636956577803": ["Balls slightly wack, sir. Readings show `percent` wack.",17], # Lucas
    "538479146679140362": ["Greek balls, sir. `percent` wack.",67], # Lucent
    "441052235967889430": ["Funny balls, sir. Very wack.",0], # Mittence
    "402026123086528518": ["His balls are holy, sir. `77%` wack.",0], # Neo
    "244517712032825344": ["Readings show `percent` wack, sir. The reading spikes past 8PM.",27], # Psi
    "453227223693131777": ["Racist balls, sir. Readings show `percent` wack.",37], # psp
    "288481819173584898": ["Inconsistent balls, sir. Readings say very wack.",0], # shroedinger
    "624738893543243786": ["Worldbuilder balls, sir. `39%` wack.",0], # smoothie
    "538182631074955294": ["Rubber balls, sir. `percent` wack.",13], # odin
    "169564270277820417": ["His balls have Thaumcraft taint, sir. Readings say `percent` wack.",47], # vlad
    "607408346668204032": ["Their ball hair seems to be attributed to someone named 'Gabe', sir.",0], # xenza
    "328118566299631616": ["Emerald balls, sir. `percent` wack, sir.",26], # yormit
    "328697009068310531": ["Lawyer balls, sir. `percent` wack.",12], # pina"
    "670854196584513559": ["I must warn you that this is the infamous Charles Cavet, known sex trafficker. He uses an alias so he's never been caught. He uses Planet Minecraft and \"minecraft but\" datapacks in his operations regularly. Readings say `percent` wack, sir.",83], # ccavet
    "721758349313441864": ["No balls detected, sir.",0], # beans
    "877303149461930034": ["Readings show close relation to worldbuiling. `percent` wack, sir.",26], # crete greece
    "562800486189760514": ["Some real [[pipis]] balls. `percent` wack, sir.",36], # tanjo
    "792893341217718283": ["Very cool balls. `percent` wack, sir.",8], # omega
    "381193469034496012": ["Hints of cannabis in his balls. `percent` wack, sir.",79] # stoner sudowoodo
}

# Phrase response dictionary
phrase_dict = {
    "zamn": "She's 12?"
}

# Phrase reaction dictionary
react_dict = {
    "joker": 856994037424586752,
    "cat": 827223066241007674,
    "watching you": 875142471808602112,
    "bingqining": 888508047100633161,
    "whaaa": 779359149791903784,
    "artifact": 749095975112671312
}

# Log Print
async def log_print(text):
    print('[' + datetime.now().strftime("%x %X") + '] ' + text)
    with open('log.txt', 'a') as log_file:
        log_file.write('[' + datetime.now().strftime("%x %X") + '] ' + text + "\n")

# Ready
@client.event
async def on_ready():
    await log_print(f'{client.user} has connected to Discord!')
    
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(status_movies)))

@client.event
async def on_message(message):
    msg = message.content.lower().replace(' ', '')

    if message.author == client.user:
        return

    author_name = message.author

    # Jarvis
    if msg == 'jarvis,scanthisguysballs' and message.reference is None:
        await log_print(f"{author_name} used generic scan.")
        await asyncio.sleep(0.5)
        await message.channel.send("Yes sir, commencing ball scan...")
        await asyncio.sleep(2)
        await message.channel.send("Their balls wack, sir.")
    elif (('jarvis,scantheballsof' in msg and len(message.mentions) == 1 and message.reference is None)) or (msg == 'jarvis,scanthisguysballs' and message.reference is not None):
        await log_print(f"{author_name} used specific scan...")
        await asyncio.sleep(0.5)
        await message.channel.send("Yes sir, commencing ball scan...")
        await asyncio.sleep(2)

        if len(message.mentions) == 1:
            mention_id = str(message.mentions[0].id)
            await log_print(f"{author_name} scanned {message.mentions[0]}")
        elif message.reference is not None:
            mention_id = str(message.reference.resolved.author.id)
            await log_print(f"{author_name} scanned {message.reference.resolved.author}")
        else:
            response = "Scan failed, sir. Please tell Psi about this."
            await log_print(f"{author_name}'s scan failed!")
        
        if any(mention_id in key for key in scan_messages):
            random_percentage = max(scan_messages[mention_id][1] + random.randint(-15, 15), 0)
            if mention_id == "244517712032825344" and (datetime.now().hour >= 20 or datetime.now().hour <= 6): random_percentage *= 3
            response = scan_messages[mention_id][0].replace("`percent`", f"`{str(random_percentage)}%`")
        else:
            response = f"Their balls wack, sir. Readings show `{str(random.randint(0, 100))}%` wack."
        await message.channel.send(response)
    elif msg == 'https://tenor.com/view/jarvis-gif-21248397':
        await asyncio.sleep(1)
        await message.reply("https://tenor.com/view/jarvis-gif-21248407")
    
    # Responses
    if random.random() <= PHRASE_CHANCE:
        for key in phrase_dict:
            if key in message.content.lower():
                await message.reply(phrase_dict[key])
                await log_print(f"Auto replied to {key} with {phrase_dict[key]}")
                break

    # Reactions
    for key in react_dict:
        if key in message.content.lower():
            await message.add_reaction(client.get_emoji(react_dict[key]))
            await log_print(f"Auto reacted to {key} with emoji {react_dict[key]}.")

    if message.author.id == admin and "i need a good laugh" in message.content.lower():
        await log_print(f"{author_name} needed a good laugh.")
        await message.reply("https://cdn.discordapp.com/attachments/739998700767674459/898750730477928518/video0-27.mp4")
    
    await client.process_commands(message)

# Commands
@client.command(name="s")
async def say(message):
    if (message.author.id in ACCESS_list):
        text = message.message.content.replace(".s", "")
        await message.send(text)
        await message.message.delete()
        await log_print('[' + datetime.now().strftime("%x %X") + ']' + ' Said \"' + text + '\"!')

@client.command(name="cst")
async def change_status(message):
    if (message.author.id in ACCESS_list):
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(status_movies)))
        await message.message.delete()
        await log_print('[' + datetime.now().strftime("%x %X") + ']' + ' Switched status message!')

@client.command(name='op')
async def op(message, text):
    if (message.author.id == admin):
        mention_id = message.mentions[0].id
        ACCESS_list.append(mention_id)
        await message.message.delete()
        await log_print('[' + datetime.now().strftime("%x %X") + ']' + ' Gave \"' + str(mention_id) + '\" permissions!')

@client.command(name='deop')
async def deop(message, text):
    if (message.author.id == admin):
        mention_id = message.mentions[0].id
        ACCESS_list.remove(mention_id)
        await message.message.delete()
        await log_print('[' + datetime.now().strftime("%x %X") + ']' + ' Took away \"' + str(mention_id) + '\"\'s permissions!')

# Run the client
client.run(TOKEN)
