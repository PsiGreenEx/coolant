# misc.py

import discord
import random
import json
from discord.ext import commands, tasks
# local modules
import coolant


class Miscellaneous(commands.Cog):
    def __init__(self, bot_client: coolant.CoolantBot):
        self.bot = bot_client
        self.auto_change_status.start()
        self.dud_messages = [0]

        with open("./data/bot_data.json", "r") as f:
            bot_data = json.loads(f.read())
            self.join_channel_id: int = bot_data["join_channel_id"]
            self.member_role_id: int = bot_data["member_role_id"]

        with open("./data/status_movies.json", 'r') as status_movies_file:
            self.status_movies: list = json.loads(status_movies_file.read())

        with open("./data/join_messages.json", "r") as message_file:
            self.JOIN_MESSAGES = json.loads(message_file.read())

    # Join message and role add.
    @commands.Cog.listener("on_member_join")
    async def join_greet(self, member: discord.Member):
        join_channel = self.bot.get_channel(self.join_channel_id)
        member_role = member.guild.get_role(self.member_role_id)
        await join_channel.send(random.choice(self.JOIN_MESSAGES["join"]).format(member.mention))
        await member.add_roles(member_role)

    # Leave message
    @commands.Cog.listener("on_member_remove")
    async def leave_message(self, member: discord.Member):
        join_channel = self.bot.get_channel(self.join_channel_id)
        await join_channel.send(random.choice(self.JOIN_MESSAGES["leave"]).format(member))

    # Auto Status Change
    @tasks.loop(hours=12)
    async def auto_change_status(self):
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=random.choice(self.status_movies)))
        await coolant.log_print("Automatically changed status.")

    @auto_change_status.before_loop
    async def before_status_loop(self):
        await self.bot.wait_until_ready()

    @commands.slash_command(name='help', description="Displays the help menu")
    async def help(self, context, category=""):
        # TODO: Separate help fields into other modules.
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

        await context.respond(embed=help_embed)

    @commands.slash_command(name='fuse', description="Generates Dragon Ball Fusion name by combining two names together.")
    async def fuse(self, context: discord.ApplicationContext, user1: discord.User, user2: discord.User, use_nickname: bool = False):
        title1 = None
        title2 = None
        new_title = ""

        await coolant.log_print(f"{str(context.author)} used fuse.")

        # Pull users if mentioned
        if use_nickname:
            name1 = user1.display_name
        else:
            name1 = user1.name

        if use_nickname:
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

        await context.respond(new_name + new_title)

    @commands.command(name="clam")
    async def clam(self, context: commands.Context):
        await context.reply("https://cdn.discordapp.com/attachments/596391083311759412/1029178643580203089/CLAMd.png")

    @commands.slash_command(description="No Way.")
    @commands.guild_only()
    async def flurgus(self, context: discord.ApplicationContext):
        await context.respond("No Way.")
