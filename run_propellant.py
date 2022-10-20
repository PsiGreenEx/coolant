# run_propellant.py
import json
import discord
# local modules
from propellant import PropellantBot
from cogs_propellant.game_base import GameBase

if __name__ == "__main__":
    with open("./data/bot_data.json", "r") as bot_data_file:
        bot_data: dict = json.loads(bot_data_file.read())
        TOKEN: str = bot_data["propellant_token"]
        MEMBER_ROLE_ID: int = bot_data["member_role_id"]
        DEBUG_MODE: bool = bot_data["debug_mode"]

    intents = discord.Intents.all()
    PREFIX = '.'
    debug_guilds = []
    if DEBUG_MODE: debug_guilds = [bot_data['bot_test_guild_id']]

    bot = PropellantBot(intents=intents, debug_guilds=debug_guilds, command_prefix=PREFIX)

    bot.add_cog(GameBase(bot))
    bot.run(TOKEN)
