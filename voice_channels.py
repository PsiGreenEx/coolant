# voice_channels.py
import discord
import asyncio
from discord.ext import commands
# local modules
from log_print import log_print


class VoiceChannels(commands.Cog):
    def __init__(self, client, create_channel_id: int):
        self.client = client
        self.create_channel_id: int = create_channel_id
        self.channel_list = []

    # Creates temporary voice channel on join of "creation channel"
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is not None:
            if after.channel.id == self.create_channel_id:
                channel = after.channel
                guild = channel.guild
                channel_name = member.name + "'s Channel"
                overwrites = {
                    member: discord.PermissionOverwrite(manage_channels=True),
                    guild.me: discord.PermissionOverwrite(manage_channels=True)
                }
                new_channel = await guild.create_voice_channel(channel_name, overwrites=overwrites, category=channel.category)
                self.channel_list.append(new_channel)
                await log_print(f"Created voice channel \"{channel_name}\".")
                await member.move_to(new_channel)
        if before.channel in self.channel_list:
            if len(before.channel.members) == 0:
                await log_print(f"Deleted voice channel \"{channel_name}\".")
                await before.channel.delete()
