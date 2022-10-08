# game.py
import asyncio
import json
import discord
from datetime import date
import copy
import random
from discord.ext import commands
# local modules
from log_print import log_print


class Games(commands.Cog):
    def __init__(self, client):
        self.client = client

        # Game Information (such as item data)
        with open("data/game_info.json", "r") as f:
            self.game_info_dict: dict = json.loads(f.read())

        self.item_info: dict = self.game_info_dict['items']

        # Game Data (such as players' inventories)
        with open("store/game_data.json", "r") as f:
            self.game_data_dict: dict = json.loads(f.read())

    # Save Game Data to JSON
    def save_data(self):
        with open('store/game_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.game_data_dict, f, ensure_ascii=False, indent=2)

    # Get User Data and initialize if needed
    def get_user_data(self, user_id: int, reset=False) -> dict:
        if str(user_id) not in self.game_data_dict or reset:
            self.game_data_dict[str(user_id)] = copy.deepcopy(self.game_data_dict["default"])
            self.save_data()
        return self.game_data_dict[str(user_id)]

    # Update a User's Data and save
    def update_user_data(self, user_id: int, user_game_data: dict):
        self.game_data_dict[str(user_id)] = user_game_data
        self.save_data()

    # Convert Item Information into Discord Embed Field
    def item_dict_to_embed_field(self, item: dict, embed: discord.Embed):
        current_item_data = self.item_info[item['id']]

        if current_item_data["max_count"] == 1:
            formatted_name = current_item_data['name']
        else:
            formatted_name = f"{current_item_data['name']} x{item['count']}"

        embed.add_field(
            name=formatted_name,
            value=current_item_data['description'],
            inline=False
        )

    def generate_inventory_embed(self, member: discord.Member, page: int = 1) -> discord.Embed:
        member_game_data = self.get_user_data(member.id)
        member_inventory: list = member_game_data["inventory"]

        page = max(1, min(10, page))

        inventory_embed = discord.Embed(
            title=f"Page {page} of 10\n"
                  f"{member.nick}'s Inventory:",
            description=f"**🪙 AlloyTokens:** {member_game_data['tokens']}\n"
                        f"**✨ Shinies:** {member_game_data['shinies']}",
            color=0x006AF5
        )

        if member_inventory[page-1]:
            for item in member_inventory[page-1]:
                self.item_dict_to_embed_field(item, inventory_embed)

        return inventory_embed

    @commands.command(name="inventory", aliases=["inv"])
    async def inventory(self, context: discord.ext.commands.Context, page: int = 1):
        author = context.author

        inventory_embed = self.generate_inventory_embed(author, page)

        reply = await context.reply(embed=inventory_embed)
        await log_print(f"{author} checked their inventory.")

    @commands.command(name="daily", aliases=["day", "claim"])
    async def daily(self, context: discord.ext.commands.Context):
        member_game_data = self.get_user_data(context.author.id)
        if date.fromisoformat(member_game_data['daily']['when_last_claimed']) < date.today():
            member_game_data['tokens'] += member_game_data['daily']['tokens_per_claim']
            message = f"You claimed {member_game_data['daily']['tokens_per_claim']} AlloyTokens. Your total is {member_game_data['tokens']}."

            if random.random() <= member_game_data['daily']['shiny_chance']:
                member_game_data['shinies'] += member_game_data['daily']['shinies_per_claim']
                message += f"\nWow! You found {member_game_data['daily']['shinies_per_claim']} Shin{'y' if member_game_data['daily']['shinies_per_claim'] == 1 else 'ies'}! " \
                           f"Your total is {member_game_data['shinies']}."

            member_game_data['daily']['when_last_claimed'] = date.today().isoformat()
            self.update_user_data(context.author.id, member_game_data)
            await log_print(f"{context.author} claimed their dailies.")
        else:
            message = "You've already claimed your AlloyTokens for today!"

        await context.reply(message)
