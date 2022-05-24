# misc.py

import discord
import random
import asyncio
import json
from discord.ext import commands, tasks
# local modules
from log_print import log_print
from admin import status_movies

with open("join_messages.json", "r") as message_file:
    JOIN_MESSAGES = json.loads(message_file.read())


class Miscellaneous(commands.Cog):
    def __init__(self, client, join_channel_id: int, member_role_id: int):
        self.client = client
        self.join_channel_id = join_channel_id
        self.member_role_id = member_role_id
        self.auto_change_status.start()

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
                value="Type \"jarvis, scan the balls of \" then mention the user you wish to scan."
                      "\nAlternatively, you can type \"jarvis, scan this guys balls\" when replying to a message.",
            )

        if category.lower() in ("misc", "other", ""):
            help_embed.add_field(
                name="Misc",
                value="`.fuse <name or user> <name or user> [use nickname?]`: Generates Dragon Ball Fusion name by combining two names together."
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
