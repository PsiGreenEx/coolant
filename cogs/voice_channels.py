# voice_channels.py
import copy
import json
import logging
import discord
from discord.ext import commands
# local modules
import coolant


class VoiceChannels(commands.Cog):
    def __init__(self, bot_client: coolant.CoolantBot):
        self.bot = bot_client
        self.channel_list: list[discord.abc.GuildChannel] = []
        self.logger = logging.getLogger('discord')

        with open("./data/bot_data.json", 'r') as f:
            bot_data = json.loads(f.read())
            self.create_channel_id: int = bot_data["voice_chat_id"]
            self.member_role_id: int = bot_data["member_role_id"]

        with open("./store/vc_preferences.json", "r") as f:
            self.vc_preferences = json.loads(f.read())

        with open("./store/leftover_vcs.json", "r") as f:
            self.leftover_vcs: list = json.loads(f.read())

    @commands.Cog.listener()
    async def on_ready(self):
        leftover_vcs_iterator = copy.deepcopy(self.leftover_vcs)
        for vc_id in leftover_vcs_iterator:
            voice_channel = self.bot.get_channel(vc_id)
            if voice_channel is None:
                self.leftover_vcs.remove(vc_id)
                continue
            self.channel_list.append(voice_channel)
            self.leftover_vcs.remove(vc_id)
            if len(voice_channel.members) == 0:
                self.logger.info(f"Deleted leftover voice channel \"{voice_channel.name}\".")
                await voice_channel.delete()

        with open("./store/leftover_vcs.json", "w") as f:
            json.dump(list(map(lambda x: x.id, self.channel_list)), f, ensure_ascii=False, indent=2)

    @commands.slash_command(
        name="vcpref",
        description="Set your preferences for your personal voice chat.",
        options=[
            discord.Option(
                int,
                name="userlimit",
                description="Maximum number of users.",
                max_value=99,
                min_value=-1,
                default=-1
            ),
            discord.Option(
                str,
                name="channelname",
                description="Name of your channel.",
                default=""
            )
        ]
    )
    async def vcpref(self, context: discord.ApplicationContext, user_limit: int, channel_name: str):
        author_id = str(context.author.id)

        if not any(author_id in key for key in self.vc_preferences):
            self.vc_preferences[author_id] = [self.vc_preferences["default"][0], self.vc_preferences["default"][1]]

        if user_limit >= 0:
            self.vc_preferences[author_id][0] = min(user_limit, 99)

        if channel_name != "":
            self.vc_preferences[author_id][1] = channel_name

        with open("./store/vc_preferences.json", "w") as preference_file:
            json.dump(self.vc_preferences, preference_file)

        embed = discord.Embed(title="Your preferences are:", color=0x006AF5, fields=[
            discord.EmbedField("User Limit", str(self.vc_preferences[author_id][0]), True),
            discord.EmbedField("Channel Name", self.vc_preferences[author_id][1].format(context.author.name), True)
        ])

        self.logger.info(f"{context.author} updated their VC Prefs.")
        await context.interaction.response.send_message(embed=embed, ephemeral=True)

    # Creates temporary voice channel on join of "creation channel"
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if after.channel is not None:
            if after.channel.id == self.create_channel_id:
                channel: discord.VoiceChannel = after.channel
                guild = channel.guild
                member_role = channel.guild.get_role(self.member_role_id)
                member_id = str(member.id)

                if not any(member_id in key for key in self.vc_preferences):
                    user_limit = self.vc_preferences["default"][0]
                    channel_name = self.vc_preferences["default"][1].format(member.name)
                else:
                    user_limit = self.vc_preferences[member_id][0]
                    channel_name = self.vc_preferences[member_id][1].format(member.name)

                overwrites = {
                    member: discord.PermissionOverwrite(manage_channels=True, manage_messages=True, move_members=True),
                    member_role: discord.PermissionOverwrite(send_messages=False),
                    guild.me: discord.PermissionOverwrite(manage_channels=True)
                }

                new_channel = await guild.create_voice_channel(channel_name, overwrites=overwrites,
                                                               category=channel.category, user_limit=user_limit)
                self.channel_list.append(new_channel)

                with open("./store/leftover_vcs.json", "w") as f:
                    json.dump(list(map(lambda x: x.id, self.channel_list)), f, ensure_ascii=False, indent=2)

                self.logger.info(f"Created voice channel \"{channel_name}\".")
                await member.move_to(new_channel)

        if before.channel in self.channel_list:
            if len(before.channel.members) == 0:
                self.logger.info(f"Deleted voice channel \"{before.channel.name}\".")

                self.channel_list.remove(before.channel)

                with open("./store/leftover_vcs.json", "w") as f:
                    json.dump(list(map(lambda x: x.id, self.channel_list)), f, ensure_ascii=False, indent=2)

                await before.channel.delete()
