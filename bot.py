# bot.py
import os
import discord
import random
import time
import asyncio
import youtube_dl
from youtubesearchpython.__future__ import VideosSearch
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import commands, tasks
from discord.utils import get
prefix = '.'
client = commands.Bot(command_prefix=prefix)

client.remove_command("help")

# Uses a .env to access it's discord token to prevent token stealing.
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

PHRASE_CHANCE = 0.01
INFLATION_CHANCE = 0.02

# music bot stuff
song_queue = []
tasker = None

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

# Put a user ID as any of these variables to target it.
admin = 688115255301242919
access_list = [admin, 244517712032825344]

# Balls message dictionary
scan_messages = {
    "688115255301242919": ["Leafesque's balls are massive. They read as `percent` wack, sir.",2], # Leafesque
    "517122589718741022": ["23rd President's balls are `23%` wack, sir.",0], # 23
    "221756292862050314": ["Afanguy's balls are `0%` wack, sir.",0], # Afanguy
    "546400083311067137": ["Seha's balls are enormous, sir. Readings say `percent` wack.",12], # Seha
    "593223812980670493": ["Bug's balls are filled with Monster Energy Drink. `percent` wack, sir.",63], # Buggy
    "436985877806317586": ["Callisuni's balls are from space, referred to as spaceballs. Readings say `percent` wack.",30], # Calli
    "346393655432445954": ["Redditor balls, sir. Readings show `percent` wack.",3], # chickenblitz
    "703732414119411792": ["Turkish balls, sir. Readings show `percent` wack.",0], # coffee
    "868744451244302346": ["My database contains all possible balls in the universe, making them the most wack balls, sir.",0], # coolant
    "318151890405687296": ["Furry balls, sir. `percent` wack, readings show.",103], # dopa
    "242220086713122816": ["His balls are deep, sir. Readings show `percent` wack.",37], # grey
    "645668447967117332": ["His balls wack, sir. They seem to like men. Readings show `percent` wack.",24], # kazooby
    "665882081343307794": ["Apologies sir, his balls are too tiny to scan.",0], # pan
    "306966483911704586": ["Loli in username, sir.",0], # onigiri
    "454735636956577803": ["Balls slightly wack, sir. Readings show `percent` wack.",17], # Lucas
    "538479146679140362": ["Greek balls, sir. `percent` wack.",67], # Lucent
    "441052235967889430": ["I cannot get a full scan, as the scanning radius is seemingly moon-sized. My estimations are `percent` wack, sir.",17], # Mittence
    "402026123086528518": ["His balls are holy, sir. `77%` wack.",0], # Neo
    "244517712032825344": ["Readings show `percent` wack, sir. The reading spikes past 8PM.",27], # Psi
    "453227223693131777": ["Racist balls, sir. Readings show `percent` wack.",37], # psp
    "288481819173584898": ["Inconsistent balls, sir. Readings say `percent` wack.",85], # shroedinger
    "624738893543243786": ["Worldbuilder balls, sir. `39%` wack.",0], # smoothie
    "538182631074955294": ["Rubber balls, sir. `percent` wack.",13], # odin
    "169564270277820417": ["His balls have Thaumcraft taint, sir. Readings say `percent` wack.",47], # vlad
    "607408346668204032": ["Their ball hair seems to be attributed to someone named 'Gabe', sir.",0], # xenza
    "328118566299631616": ["Emerald balls, sir. `percent` wack, sir.",26], # yormit
    "328697009068310531": ["Lawyer balls, sir. `percent` wack.",12], # pina"
    "670854196584513559": ["I must warn you that this is the infamous Charles Cavet, known sex trafficker. He uses an alias so he's never been caught. He uses Planet Minecraft and \"minecraft but\" datapacks in his operations regularly. Readings say `percent` wack, sir.",83], # ccavet
    "721758349313441864": ["Only detecting balls in spirit. `percent` wack, sir.",28], # beans
    "877303149461930034": ["Readings show close relation to worldbuiling. `percent` wack, sir.",26], # crete greece
    "562800486189760514": ["Some real [[pipis]] balls. `percent` wack, sir.",36], # tanjo
    "792893341217718283": ["Very cool balls. `percent` wack, sir.",8], # omega
    "381193469034496012": ["Hints of cannabis in his balls. `percent` wack, sir.",79], # stoner sudowoodo
    "594323388705538069": ["Balls of all colors, sir.",0], # Lexa
    "155149108183695360": ["The balls of our robot overlord, sir.",0], # Dyno
    "159985870458322944": ["Stupid fucking balls, sir.",0], # MEE6
    "783772765962240022": ["These balls seem to only work half the time, sir",0], # Tempy
    "534589798267224065": ["https://cdn.discordapp.com/attachments/699684376715460628/905262129530175558/dragon-ball-super-goku-shocked-1240697.png",0], # Rank
    "235088799074484224": ["These balls have been crushed, sir. There is trace amounts of Youtube TOS left on the remnants.",0] # Rhythm
}

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
    "yormit make shit brownies",
    "seha make great brownies",
    "seha make pizza",
    "for the pizza",
    "for omori gifs; death on sight",
    "for mittence; do the funny voice",
    "the alloy discord server",
    "smoothie art stream",
    "odin make Burnout",
    "vlad make AlloyDungeon",
    "alloy direct",
    "alloy direct unofficial pre-show",
    "psi make AlloyAdventures"
]

# Phrase response dictionary
phrase_dict = {
    "zamn": "SHE'S 12?",
    "minecraft - snapshot": "holy shit, a snapshot!"
}

# Phrase reaction dictionary
react_dict = {
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

# YTDL
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.duration = data.get('duration')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, play=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{url}", download=not stream or play))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# Log Print
async def log_print(text):
    print('[' + datetime.now().strftime("%x %X") + '] ' + text)
    with open('log.txt', 'a') as log_file:
        log_file.write('[' + datetime.now().strftime("%x %X") + '] ' + text + "\n")

# Ready
@client.event
async def on_ready():
    await log_print(f'{client.user} has connected to Discord!')
    
    #await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(status_movies)))

@client.event
async def on_message(message):
    scrubbed_message = message.content.lower().replace(' ', '')

    if message.author == client.user:
        return
    
    if message.channel.type == discord.ChannelType.private:
        await message.channel.send("Shut the fuck up you stupid bitch!")
        return

    author_name = message.author

    # Jarvis
    if scrubbed_message == 'jarvis,scanthisguysballs' and message.reference is None:
        await log_print(f"{author_name} used generic scan.")
        await asyncio.sleep(0.5)
        await message.channel.send("Yes sir, commencing ball scan...")
        async with message.channel.typing():
            await asyncio.sleep(2)
            await message.channel.send("Their balls wack, sir.")
    elif (('jarvis,scantheballsof' in scrubbed_message and len(message.mentions) == 1 and message.reference is None)) or (scrubbed_message == 'jarvis,scanthisguysballs' and message.reference is not None) or (scrubbed_message == 'jarvis,scanmyballs' and message.reference is None):
        await log_print(f"{author_name} used specific scan...")
        await asyncio.sleep(0.5)
        await message.channel.send("Yes sir, commencing ball scan...")
        async with message.channel.typing():
            await asyncio.sleep(2)

            if len(message.mentions) == 1:
                mention_id = str(message.mentions[0].id)
                await log_print(f"{author_name} scanned {message.mentions[0]}")
            elif message.reference is not None:
                mention_id = str(message.reference.resolved.author.id)
                await log_print(f"{author_name} scanned {message.reference.resolved.author}")
            elif message.reference is None:
                mention_id = str(message.author.id)
                await log_print(f"{author_name} scanned themself.")
            else:
                response = "Scan failed, sir. Please tell Psi about this."
                await log_print(f"{author_name}'s scan failed!")
        
            if any(mention_id in key for key in scan_messages):
                random_percentage = max(scan_messages[mention_id][1] + random.randint(-15, 15), 0)
                if random.random() <= INFLATION_CHANCE: random_percentage + random.randint(500, 50000)
                if mention_id == "244517712032825344" and (datetime.now().hour >= 20 or datetime.now().hour <= 6): random_percentage *= 3
                response = scan_messages[mention_id][0].replace("`percent`", f"`{str(random_percentage)}%`")
            else:
                response = f"Their balls wack, sir. Readings show `{str(random.randint(0, 100))}%` wack."
            await message.channel.send(response)
    elif scrubbed_message == 'https://tenor.com/view/jarvis-gif-21248397':
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

    # Leaf secret
    if message.author.id == admin and "i need a good laugh" in message.content.lower():
        await log_print(f"{author_name} needed a good laugh.")
        await message.reply("https://cdn.discordapp.com/attachments/739998700767674459/898750730477928518/video0-27.mp4")
    
    await client.process_commands(message)

# Cogs
class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="s")
    async def say(self, context):
        if (context.author.id in access_list):
            text = context.message.content.replace(".s", "")
            await context.send(text)
            await delete_message(context.message)
            await log_print('[' + datetime.now().strftime("%x %X") + ']' + ' Said \"' + text + '\"!')

    @commands.command(name="cst")
    async def change_status(self, context, choice=-1):
        if (context.author.id in access_list):
            if choice == -1:
                await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(status_movies)))
            else:
                await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=status_movies[choice]))
            await delete_message(context.message)
            await log_print('[' + datetime.now().strftime("%x %X") + ']' + ' Switched status message!')

    @commands.command(name='op')
    async def op(self, context, text):
        if (context.author.id == admin):
            mention_id = context.mentions[0].id
            access_list.append(mention_id)
            await delete_message(context.message)
            await log_print('[' + datetime.now().strftime("%x %X") + ']' + ' Gave \"' + str(mention_id) + '\" permissions!')

    @commands.command(name='deop')
    async def deop(self, context, text):
        if (context.author.id == admin):
            mention_id = context.mentions[0].id
            access_list.remove(mention_id)
            await delete_message(context.message)
            await log_print('[' + datetime.now().strftime("%x %X") + ']' + ' Took away \"' + str(mention_id) + '\"\'s permissions!')

class Miscellaneous(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.auto_change_status.start()
    
    # Auto Status Change
    @tasks.loop(hours=12)
    async def auto_change_status(self):
        #await client.get_channel(852326964298514452).send("woa")
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(status_movies)))

    @auto_change_status.before_loop
    async def before_status_loop(self):
        await self.client.wait_until_ready()
    
    @commands.command(name='help')
    async def help(self, context, category=""):
        help_embed = discord.Embed(
            title="Help",
            description="Go yell at Psi to add more features!",
            color=0x006AF5
        )
        if category.lower() in ("ball scans", "ball scan", ""):
            help_embed.add_field(
                name="Ball Scans",
                value="Type \"jarvis, scan the balls of \" then mention the user you wish to scan.\nAlternatively, you can type \"jarvis, scan this guys balls\" when replying to a message.",
            )

        if category.lower() in ("misc", "other", ""):
            help_embed.add_field(
                name="Misc",
                value="`.fuse <name or user> <name or user> [use nickname?]`: Generates Dragon Ball Fusion name by combining two names together."
            )

        if category.lower() in ("music", "player", ""):
            help_embed.add_field(
                name="Music",
                value="`.join`: Joins the channel you are in.\n`.play or .p <youtube-link>`: Joins the channel you are in and plays the song. If a song is already playing, it will add it to the queue.\n`.search or .sr <search-text>`: Allows you to select the top 5 results from youtube to play.\n`.leave`: Leaves current channel and clear the queue.\n`.queue or .q`: Views the song queue.\n`.pause`: Pauses the current song.\n`.resume`: Resumes the song if paused.\n`.stop`: Stops playing and clears the queue.\n`.skip`: Skips the current song.",
                inline=False
            )
        
        await context.send(embed=help_embed)

    @commands.command(name='fuse')
    async def fuse(self, context, name1:str, name2:str, use_nickname="no"):
        title1 = []
        title2 = []
        new_title = ""

        # Pull users if mentioned
        if name1.startswith('<@') and name1.endswith('>'):
            user1 = context.message.mentions[0]
            if use_nickname in ("yes", "true") and user1.nick is not None:
                name1 = user1.nick
            else:
                name1 = user1.name

        if name2.startswith('<@') and name2.endswith('>'):
            user2 = context.message.mentions[1]
            if use_nickname in ("yes", "true") and user2.nick is not None:
                name2 = user2.nick
            else:
                name2 = user2.name
        
        # Strip first text from names with titles (usually nicknames)
        if "|" in name1:
            title1 = name1.split("|", 1)[1].split()
            name1 = name1.split("|", 1)[0].rstrip()
        elif "," in name1:
            title1 = name1.split(",", 1)[1].split()
            name1 = name1.split(",", 1)[0].rstrip()
        
        if "|" in name2:
            title2 = name2.split("|", 1)[1].split()
            name2 = name2.split("|", 1)[0].rstrip()
        elif "," in name2:
            title2 = name2.split(",", 1)[1].split()
            name2 = name2.split(",", 1)[0].rstrip()

        new_name = name1[:len(name1)//2] + name2[len(name2)//2:]

        # hacky way to prevent strings becomming lists
        if len(title1) == 2 and len(title2) > 0: title1 = [[title1[0]], [title1[1]]]
        if len(title2) == 2 and len(title1) > 0: title2 = [[title2[0]], [title2[1]]]

        if len(title1) > 0 and len(title2) == 0:
            new_title = " | " + " ".join(title1)
        elif len(title1) == 0 and len(title2) > 0:
            new_title = " | " + " ".join(title2)
        elif len(title1) > 0 and len(title2) > 0:
            new_title = " | " + " ".join([*title1[:len(title1)//2], *title2[len(title2)//2]])
        else:
            new_title = ""

        await asyncio.sleep(0.25)
        await context.reply(new_name + new_title)


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Leave when empty
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        global song_queue
        global tasker
        voice_client = member.guild.voice_client
        if voice_client == None:
            return
        
        if before.channel == voice_client.channel:
            if len(voice_client.channel.members) == 1:
                song_queue.clear()
                voice_client.stop()
                if tasker: tasker.cancel()
                await voice_client.disconnect()

    @commands.command(name='leave', aliases=['l', 'exit'], help='To make the bot leave the voice channel')
    async def leave(self, ctx):
        global song_queue
        global tasker
        voice_client = ctx.message.guild.voice_client
        if voice_client != None and voice_client.is_connected():
            if ctx.message.author.voice != None and ctx.message.author.voice.channel == voice_client.channel:
                song_queue.clear()
                voice_client.stop()
                if tasker: tasker.cancel()
                await voice_client.disconnect()
            else:
                await ctx.send("You are not in the same channel as coolant.")
        else:
            await ctx.send("Coolant is not connected to a voice channel.")
    
    @commands.command(name='join')
    async def join(self, ctx):
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        try:
            if(voice == None):
                if not ctx.message.author.voice:
                    await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
                else:
                    channel = ctx.message.author.voice.channel
                    await channel.connect()
        except Exception as e:
            await ctx.send(f"Error occured: {e}")

    @commands.command(name='play', aliases=['p', 'play_song'], help='To play song')
    async def play(self, ctx, *, url:str):
        global song_queue
        voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
        try:
            if(voice == None):
                if not ctx.message.author.voice:
                    await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
                else:
                    channel = ctx.message.author.voice.channel
                    await channel.connect()
            
            async with ctx.typing():
                voice_client = ctx.message.guild.voice_client
                if not voice_client.is_playing():
                    song_queue.clear()
                player = await YTDLSource.from_url(url, loop=client.loop, stream=True)
            if len(song_queue) == 0:
                await self.start_playing(ctx, player)
            else:
                song_queue.append(player)
                await ctx.send(f"**Queued at position {len(song_queue)-1}:** {player.title}")
        except Exception as e:
            await ctx.send(f"Error occured: {e}")
    
    @commands.command(name='search', aliases=['sr'])
    async def search(self, ctx, *, term:str):
        videos_search = VideosSearch(term, limit = 5)
        videos_result = await videos_search.next()
        a = "**Pick a video:**"
        i = 0
        for result in videos_result['result']:
            i += 1
            a = a + f"\n**{i}.** {result['title']} - {result['duration']}"
        pick_message = await ctx.send(a)
        await pick_message.add_reaction('1️⃣')
        await pick_message.add_reaction('2️⃣')
        await pick_message.add_reaction('3️⃣')
        await pick_message.add_reaction('4️⃣')
        await pick_message.add_reaction('5️⃣')

        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['1️⃣','2️⃣','3️⃣','4️⃣','5️⃣']

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=5, check=check)
            reaction_numbers = {
                '1️⃣': 1,
                '2️⃣': 2,
                '3️⃣': 3,
                '4️⃣': 4,
                '5️⃣': 5
            }
            chosen_result_url = videos_result['result'][reaction_numbers[reaction.emoji] - 1]['link']
            await pick_message.delete()
            await self.play(ctx, url=chosen_result_url)
        except asyncio.TimeoutError:
            await pick_message.delete()
            await ctx.send("Timed out.")

    async def start_playing(self, ctx, player):
        global song_queue
        song_queue.append(player)
        global tasker
        if(song_queue[0] == None):
            return
        i = 0
        while i < len(song_queue):
            try:
                ctx.voice_client.play(song_queue[0], after=lambda e: print('Player error: %s' % e) if e else None)
                await ctx.send(f"**Now playing:** {song_queue[0].title}")
            except Exception as e:
                await ctx.send(f"Something went wrong: {e}")
            #await asyncio.sleep(song_queue[0].duration)
            tasker = asyncio.create_task(self.coro(ctx,song_queue[0].duration))
            try:
                await tasker
            except asyncio.CancelledError:
                await log_print("Task cancelled")
            if(len(song_queue) > 0):
                song_queue.pop(0)

    async def coro(self, ctx, duration):
        await asyncio.sleep(duration)

    @commands.command(name='queued', aliases=['q', 'queue', 'list'], help='This command displays the queue')
    async def queued(self, ctx):
        global song_queue
        if len(song_queue) == 0:
            await ctx.send("No songs remaining in queue! <:watcher:875142471808602112>")
            return
        a = ""
        i = 0
        for song in song_queue:
            if i > 0:
                a = a + "**" + str(i) +".** " + song.title + "\n "
            i += 1
        await ctx.send(f"**Now Playing:** {song_queue[0].title}\n- - -\n**Queue:** \n {a}")

    @commands.command(name='pause', help='This command pauses the song')
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client
        
        if voice_client != None and voice_client.is_playing():
            if ctx.message.author.voice != None and ctx.message.author.voice.channel == voice_client.channel:
                await ctx.send("Paused playing.")
                await voice_client.pause()
            else:
                await ctx.send("You are not in the same channel as coolant.")
        else:
            await ctx.send("Coolant is not playing anything at the moment.")
        
        
    
    @commands.command(name='resume', help='Resumes the song')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client != None and voice_client.is_paused():
            if ctx.message.author.voice != None and ctx.message.author.voice.channel == voice_client.channel:
                await ctx.send("Resumed playing.")
                await voice_client.resume()
            else:
                await ctx.send("You are not in the same channel as coolant.")
        else:
            await ctx.send("Coolant was not playing anything before this. Use `.play` instead.")
    
    @commands.command(name='stop', help='Stops the song')
    async def stop(self, ctx):
        global tasker
        global song_queue
        voice_client = ctx.message.guild.voice_client
        if voice_client != None and voice_client.is_playing():
            if ctx.message.author.voice != None and ctx.message.author.voice.channel == voice_client.channel:
                song_queue.clear()
                voice_client.stop()
                tasker.cancel()
                await ctx.send("The queue is cleared.")
            else:
                await ctx.send("You are not in the same channel as coolant.")
        else:
            await ctx.send("Coolant is not playing anything at the moment.")

    @commands.command(name='skip', help='Skip the song')
    async def skip(self, ctx):
        global tasker
        voice_client = ctx.message.guild.voice_client
        if voice_client != None and voice_client.is_playing():
            if ctx.message.author.voice != None and ctx.message.author.voice.channel == voice_client.channel:
                voice_client.stop()
                tasker.cancel()
                await ctx.send("Skipped song.")
            else:
                await ctx.send("You are not in the same channel as coolant.")
        else:
            await ctx.send("Coolant is not playing anything at the moment.")

# Delete message unless in DM
async def delete_message(message):
    if message.channel.type != discord.ChannelType.private: await message.delete()

# Run the client
client.add_cog(Admin(client))
client.add_cog(Miscellaneous(client))
client.add_cog(Music(client))
client.run(TOKEN)
