# processors/permion.py
import logging
import discord


class PermionProcessor:
    def __init__(self):
        self.logger = logging.getLogger('discord')
        self.PERMION_DICT: dict = {  # dictionary contains references to a function to call upon activation.
            # keyword activated
            "active": {},
            # discord perms only
            "passive": {},
            # unique activation method
            "unique": {}
        }

    async def activate_permion(self, user_role_data: dict, message: discord.Message = None):
        user_permion: str = user_role_data['permion']

        # activate proper permion
        if message and user_permion in self.PERMION_DICT['active'].keys():
            await self.PERMION_DICT['active'][user_permion](user_role_data, message)
