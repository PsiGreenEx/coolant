# music.py

from youtubesearchpython.__future__ import VideosSearch
import discord
import asyncio
import youtube_dl
import time
from discord.ext import commands

from log_print import log_print

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
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


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
        data = await loop.run_in_executor(None,
                                          lambda: ytdl.extract_info(f"ytsearch:{url}", download=not stream or play))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Leave when empty
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        global song_queue
        global tasker
        voice_client = member.guild.voice_client
        if voice_client is None:
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
        if voice_client is not None and voice_client.is_connected():
            if ctx.message.author.voice is not None and ctx.message.author.voice.channel == voice_client.channel:
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
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        try:
            if voice is None:
                if not ctx.message.author.voice:
                    await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
                else:
                    channel = ctx.message.author.voice.channel
                    await channel.connect()
        except Exception as e:
            await ctx.send(f"Error occured: {e}")

    @commands.command(name='play', aliases=['p', 'play_song'], help='To play song')
    async def play(self, ctx, *, url: str):
        global song_queue
        voice = discord.utils.get(self.client.voice_clients, guild=ctx.guild)
        try:
            if voice is None:
                if not ctx.message.author.voice:
                    await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
                else:
                    channel = ctx.message.author.voice.channel
                    await channel.connect()

            async with ctx.typing():
                voice_client = ctx.message.guild.voice_client
                if not voice_client.is_playing():
                    song_queue.clear()
                player = await YTDLSource.from_url(url, loop=self.client.loop, stream=True)
            if len(song_queue) == 0:
                await self.start_playing(ctx, player)
            else:
                song_queue.append(player)
                await ctx.send(f"**Queued at position {len(song_queue) - 1}:** {player.title} - {self.convert_duration(player.duration)}")
        except Exception as e:
            await ctx.send(f"Error occured: {e}")

    @commands.command(name='search', aliases=['sr'])
    async def search(self, ctx, *, term: str):
        videos_search = VideosSearch(term, limit=5)
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
            return user == ctx.message.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=20, check=check)
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
        if song_queue[0] is None:
            return
        i = 0
        while i < len(song_queue):
            try:
                ctx.voice_client.play(song_queue[0], after=lambda e: print('Player error: %s' % e) if e else None)
                await ctx.send(f"**Now playing:** {song_queue[0].title} - {self.convert_duration(song_queue[0].duration)}")
            except Exception as e:
                await ctx.send(f"Something went wrong: {e}")
            # await asyncio.sleep(song_queue[0].duration)
            tasker = asyncio.create_task(self.coro(ctx, song_queue[0].duration))
            try:
                await tasker
            except asyncio.CancelledError:
                await log_print("Task cancelled")
            if len(song_queue) > 0:
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
                a = a + "**" + str(i) + ".** " + song.title + " - " + self.convert_duration(song.duration) + "\n "
            i += 1
        await ctx.send(f"**Now Playing:** {song_queue[0].title} - {self.convert_duration(song_queue[0].duration)}\n- - -\n**Queue:** \n {a}")

    @commands.command(name='pause', help='This command pauses the song')
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if voice_client is not None and voice_client.is_playing():
            if ctx.message.author.voice is not None and ctx.message.author.voice.channel == voice_client.channel:
                await ctx.send("Paused playing.")
                await voice_client.pause()
            else:
                await ctx.send("You are not in the same channel as coolant.")
        else:
            await ctx.send("Coolant is not playing anything at the moment.")

    @commands.command(name='resume', help='Resumes the song')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client is not None and voice_client.is_paused():
            if ctx.message.author.voice is not None and ctx.message.author.voice.channel == voice_client.channel:
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
        if voice_client is not None and voice_client.is_playing():
            if ctx.message.author.voice is not None and ctx.message.author.voice.channel == voice_client.channel:
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
        if voice_client is not None and voice_client.is_playing():
            if ctx.message.author.voice is not None and ctx.message.author.voice.channel == voice_client.channel:
                voice_client.stop()
                tasker.cancel()
                await ctx.send("Skipped song.")
            else:
                await ctx.send("You are not in the same channel as coolant.")
        else:
            await ctx.send("Coolant is not playing anything at the moment.")

    @commands.command(name='loop', help='Toggles song looping')
    async def loop(self, ctx):
        await ctx.send(":(")

    def convert_duration(self, seconds:int):
        video_time = time.gmtime(seconds)
        if seconds >= 3600:
            return time.strftime("%H:%M:%S", video_time)
        else:
            return time.strftime("%M:%S", video_time)
