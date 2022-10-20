# run_coolant.py
import json
import discord
# local modules
from coolant import CoolantBot
from jarvis_processor import JarvisProcessor
from cogs.admin import Admin
from cogs.misc import Miscellaneous
from cogs.jarvis import Jarvis
from cogs.voice_channels import VoiceChannels

if __name__ == "__main__":
    with open("data/bot_data.json", "r") as bot_data_file:
        bot_data: dict = json.loads(bot_data_file.read())
        TOKEN: str = bot_data["token"]
        CREATE_CHANNEL_ID: int = bot_data["voice_chat_id"]
        JOIN_CHANNEL_ID: int = bot_data["join_channel_id"]
        MEMBER_ROLE_ID: int = bot_data["member_role_id"]
        ADMIN_LIST: list[int] = bot_data["admin_access_list"]
        DEBUG_MODE: bool = bot_data["debug_mode"]

    intents = discord.Intents.all()
    PREFIX = '.'
    debug_guilds = []
    if DEBUG_MODE: debug_guilds = [bot_data['bot_test_guild_id']]

    jarvis = JarvisProcessor()

    bot = CoolantBot(jarvis, intents=intents, debug_guilds=debug_guilds, command_prefix=PREFIX)

    bot.add_cog(Admin(bot))
    bot.add_cog(Miscellaneous(bot))
    bot.add_cog(Jarvis(bot, jarvis))
    bot.add_cog(VoiceChannels(bot))
    bot.run(TOKEN)
