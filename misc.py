# misc.py

import discord
import random
import asyncio
import json
from discord.ext import commands, tasks
# local modules
from library import *
from admin import status_movies

with open("data/join_messages.json", "r") as message_file:
    JOIN_MESSAGES = json.loads(message_file.read())


class Miscellaneous(commands.Cog):
    def __init__(self, client, join_channel_id: int, member_role_id: int):
        self.client = client
        self.join_channel_id = join_channel_id
        self.member_role_id = member_role_id
        self.auto_change_status.start()
        self.dud_messages = [0]

    # Join message and role add.
    @commands.Cog.listener("on_member_join")
    async def join_greet(self, member: discord.Member):
        join_channel = self.client.get_channel(self.join_channel_id)
        member_role = member.guild.get_role(self.member_role_id)
        await join_channel.send(random.choice(JOIN_MESSAGES["join"]).format(member.mention))
        await member.add_roles(member_role)

    # Leave message
    @commands.Cog.listener("on_member_remove")
    async def leave_message(self, member: discord.Member):
        join_channel = self.client.get_channel(self.join_channel_id)
        await join_channel.send(random.choice(JOIN_MESSAGES["leave"]).format(member))

    # Auto Status Change
    @tasks.loop(hours=12)
    async def auto_change_status(self):
        await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(status_movies)))
        await log_print("Automatically changed status.")

    @auto_change_status.before_loop
    async def before_status_loop(self):
        await self.client.wait_until_ready()

    @commands.command(name='help')
    async def help(self, context, category=""):
        # TODO Separate help fields into other modules.
        help_embed = discord.Embed(
            title="Help",
            description="Go yell at Psi to add more features!",
            color=0x006AF5
        )
        if category.lower() in ("ball scans", "ball scan", ""):
            help_embed.add_field(
                name="Ball Scans",
                value="Type \"jarvis, scan the balls of \" then mention the user you wish to scan.\n\n"
                      "Alternatively, you can type \"jarvis, scan this guys balls\" when replying to a message.\n\n"
                      "You can scan your own balls with \"jarvis, scan my balls\".\n\n"
                      "(The content of the message doesn't really matter as long as it contains 'balls' and 'scan'.)",
            )

        if category.lower() in ("misc", "other", ""):
            help_embed.add_field(
                name="Misc",
                value="`.fuse <name or user> <name or user> [use nickname?]`: Generates Dragon Ball Fusion name by combining two names together.\n\n"
                      "`.quote`: Coming soon! (probably)"
            )

        if category.lower() in ("voice", "voice channel", "vc", ""):
            help_embed.add_field(
                name="Voice",
                value="Join <#853038740863451186> to create a temporary VC. You have full perms for this vc.\n\n"
                      "`.vcpref [user_limit [channel name]]`: Shows you your set preferences if blank. Allows you to modify some of your default VC settings."
            )

        if category.lower() in ("games", "game", "gambling", ""):
            help_embed.add_field(
                name="Games",
                value="`.inv`: Show your inventory.\n\n"
                      "`.claim`: Claim your daily AlloyTokens."
            )

        await context.send(embed=help_embed)

    @commands.command(name='fuse')
    async def fuse(self, context, name1: str, name2: str, use_nickname="no"):
        title1 = None
        title2 = None
        new_title = ""

        await log_print(f"{str(context.author)} used fuse.")

        # Pull users if mentioned
        if name1.startswith('<@') and name1.endswith('>'):
            user1 = await context.guild.fetch_member(name1.strip('<@!>'))
            if use_nickname in ("yes", "true"):
                name1 = user1.display_name
            else:
                name1 = user1.name

        if name2.startswith('<@') and name2.endswith('>'):
            user2 = await context.guild.fetch_member(name2.strip('<@!>'))
            if use_nickname in ("yes", "true"):
                name2 = user2.display_name
            else:
                name2 = user2.name

        # Strip first text from names with titles (usually nicknames)
        if "|" in name1:
            title1 = name1.split("|", 1)[1].lstrip()
            name1 = name1.split("|", 1)[0].rstrip()
        elif "," in name1:
            title1 = name1.split(",", 1)[1].lstrip()
            name1 = name1.split(",", 1)[0].rstrip()

        if "|" in name2:
            title2 = name2.split("|", 1)[1].lstrip()
            name2 = name2.split("|", 1)[0].rstrip()
        elif "," in name2:
            title2 = name2.split(",", 1)[1].lstrip()
            name2 = name2.split(",", 1)[0].rstrip()

        # fuse names
        new_name = name1[:len(name1) // 2] + name2[len(name2) // 2:]

        # fuse titles unless there is only one
        if title1 is not None and title2 is not None:
            new_title = " | " + title1[:len(title1) // 2] + title2[len(title2) // 2:]

        await asyncio.sleep(0.25)
        await context.reply(new_name + new_title)

    @commands.command(name="quote")
    async def quote(self, context: discord.ext.commands.Context, *args):
        pass

    @commands.slash_command()
    @commands.guild_only()
    async def flurgus(self, context: discord.ApplicationContext):
        await context.respond("No Way.")
