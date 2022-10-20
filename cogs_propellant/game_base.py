# game_base.py
import asyncio
import json
import discord
from datetime import date
import copy
import random
from discord.ext import commands
# local modules
import propellant


class GameBase(commands.Cog):
    def __init__(self, bot_client: propellant.PropellantBot):
        self.bot = bot_client

        with open("./data/bot_data.json", "r") as f:
            bot_data = json.loads(f.read())
            self.ADMIN_LIST: list[int] = bot_data["admin_access_list"]

    # Functions
    # Add item to user's inventory
    def add_item_to_inventory(self, user_id: int, new_item_data: dict):
        user_data: dict = self.bot.get_user_data(user_id)
        user_inventory: list[list] = user_data["inventory"]
        new_item_info: dict = self.bot.ITEM_INFO_DICT[new_item_data["id"]]
        item_added = False

        for inventory_page in user_inventory:
            for item_data in inventory_page:
                if new_item_data["id"] == item_data["id"]:
                    if new_item_info["max_count"] > -1:
                        item_data["count"] = min(new_item_info["max_count"], item_data["count"] + new_item_data["count"])
                    else:
                        item_data["count"] += new_item_data["count"]
                    item_added = True
                    break

            if item_added: break

            if len(inventory_page) < 10:
                inventory_page.append(new_item_data)
                item_added = True
                break

        if not item_added:
            user_inventory.append([new_item_data])

        self.bot.save_data()

    # remove item from user's inventory
    def remove_item_from_inventory(self, user_id: int, item_id: str, count=-1):
        user_data: dict = self.bot.get_user_data(user_id)
        user_inventory: list[list] = user_data["inventory"]

        item_removed = False

        for inventory_page in user_inventory:
            for item_data in inventory_page:
                if item_id == item_data["id"]:
                    if count == -1:
                        inventory_page.remove(item_data)
                        if not inventory_page: user_inventory.remove(inventory_page)
                        item_removed = True
                        break
                    else:
                        item_data["count"] -= count
                        if item_data['count'] <= 0:
                            inventory_page.remove(item_data)
                            if not inventory_page: user_inventory.remove(inventory_page)
                        item_removed = True
                        break

            if item_removed: break

        self.bot.save_data()

    # Convert Item Information into Discord Embed Field
    def item_dict_to_embed_field(self, item: dict, embed: discord.Embed, inventory_slot: int):
        current_item_data = self.bot.ITEM_INFO_DICT[item['id']]

        if current_item_data["max_count"] == 1:
            formatted_name = f"{inventory_slot}. {current_item_data['emoji']} {current_item_data['name']}"
        else:
            formatted_name = f"{inventory_slot}. {current_item_data['emoji']} {current_item_data['name']} ×{item['count']}"

        embed.add_field(
            name=formatted_name,
            value=current_item_data['description'],
            inline=False
        )

    # Create Embed of User's Inventory
    def generate_inventory_embed(self, member: discord.Member, page: int = 1) -> discord.Embed:
        member_game_data = self.bot.get_user_data(member.id)
        member_inventory: list[list] = member_game_data["inventory"]

        max_page = 0
        for inventory_page in member_inventory:
            if inventory_page:
                max_page += 1
            else:
                if max_page == 0: max_page = 1
                break

        page = max(1, min(max_page, page))

        inventory_embed = discord.Embed(
            title=f"Page {page} of {max_page}\n"
                  f"{member.display_name}'s Inventory:",
            description=f"**:coin: AlloyTokens:** {member_game_data['tokens']:,}\n"
                        f"**✨ Shinies:** {member_game_data['shinies']:,}",
            color=0x006AF5
        )

        if member_inventory[page-1]:
            i = (page * 10) - 10
            for item in member_inventory[page-1]:
                i += 1
                self.item_dict_to_embed_field(item, inventory_embed, i)

        return inventory_embed

    # Sell Item (assuming the item is sellable and the player has those items)
    def sell_item(self, user_id: int, inventory_slot: int, count: int):
        user_game_data = self.bot.get_user_data(user_id)

        item_data: dict = user_game_data['inventory'][inventory_slot // 10][inventory_slot-1]
        item_info: dict = self.bot.ITEM_INFO_DICT[item_data['id']]

        user_game_data['tokens'] += item_info['value'] * count
        self.remove_item_from_inventory(user_id, item_data['id'], count)

    # Views and Other Classes
    # Inventory Page Buttons
    class InventoryView(discord.ui.View):
        def __init__(self, game_base, user: discord.Member, page: int,  *items: discord.ui.Item):
            super().__init__(*items)
            self.game_base: GameBase = game_base
            self.user = user
            self.page = page

        # Left Page Button
        @discord.ui.button(label="◀")
        async def left_callback(self, button: discord.Button, interaction: discord.Interaction):
            if interaction.message.interaction.user != interaction.user:
                await interaction.response.send_message(content="Hey! Don't touch that!", ephemeral=True)
                return
            if self.page <= 1:
                await interaction.response.send_message(content="Can't move before page 1.", ephemeral=True)
                return

            self.page -= 1

            inventory_embed = self.game_base.generate_inventory_embed(self.user, self.page)
            await interaction.response.edit_message(embed=inventory_embed, view=self)

        # Right Page Button
        @discord.ui.button(label="▶")
        async def right_callback(self, button: discord.Button, interaction: discord.Interaction):
            if interaction.message.interaction.user != interaction.user:
                await interaction.response.send_message(content="Hey! Don't touch that!", ephemeral=True)
                return

            member_game_data = self.game_base.bot.get_user_data(self.user.id)
            member_inventory = member_game_data['inventory']
            max_page = 0

            for inventory_page in member_inventory:
                if inventory_page:
                    max_page += 1
                else:
                    if max_page == 0: max_page = 1
                    break

            if self.page == max_page:
                await interaction.response.send_message(content=f"Can't move past page {max_page}.", ephemeral=True)
                return

            self.page += 1

            inventory_embed = self.game_base.generate_inventory_embed(self.user, self.page)
            await interaction.response.edit_message(embed=inventory_embed, view=self)

    # Commands
    # Inventory
    @commands.slash_command(
        name="inventory",
        description="Shows your inventory.",
        options=[
            discord.Option(
                int,
                name="page",
                description="The page number of your inventory.",
                min_value=1,
                default=1
            ),
            discord.Option(
                discord.Member or None,
                name="user",
                description="The user whose inventory you want to check.",
                default=None
            )
        ]
    )
    async def inventory(self, context: discord.ApplicationContext, page: int, user: discord.Member or None):
        if user is None:
            user = context.author

        inventory_embed = self.generate_inventory_embed(user, page)

        await context.respond(embed=inventory_embed, view=self.InventoryView(self, user, page))

    # Daily Claim
    @commands.slash_command(
        name="claim",
        description="Claim your daily tokens!"
    )
    async def daily(self, context: discord.ApplicationContext):
        member_game_data = self.bot.get_user_data(context.author.id)
        if date.fromisoformat(member_game_data['daily']['when_last_claimed']) < date.today():
            member_game_data['tokens'] += member_game_data['daily']['tokens_per_claim']
            message = f"You claimed {member_game_data['daily']['tokens_per_claim']:,} AlloyTokens. Your total is {member_game_data['tokens']:,} :coin:."

            if random.random() <= member_game_data['daily']['shiny_chance']:
                member_game_data['shinies'] += member_game_data['daily']['shinies_per_claim']
                message += f"\nWow! You found {member_game_data['daily']['shinies_per_claim']:,} ✨Shin{'y' if member_game_data['daily']['shinies_per_claim'] == 1 else 'ies'}✨! " \
                           f"Your total is {member_game_data['shinies']:,} ✨."

            member_game_data['daily']['when_last_claimed'] = date.today().isoformat()

            await context.respond(message)
            await self.bot.log_print(f"{context.author} claimed their dailies.")
        else:
            await context.interaction.response.send_message(content="You already claimed your tokens for today.", ephemeral=True)

    # Clam Tomfoolery
    @commands.slash_command(
        name="clam",
        description="Clam your daily tokens!"
    )
    async def clam(self, context: discord.ApplicationContext):
        await context.respond("https://cdn.discordapp.com/attachments/596391083311759412/1029178643580203089/CLAMd.png")

    # Pay
    @commands.slash_command(
        name="pay",
        description="Pay another user some tokens or shinies.",
        options=[
            discord.Option(
                discord.Member,
                name="user",
                description="The user you will pay."
            ),
            discord.Option(
                int,
                name="amount",
                description="Amount of currency to pay."
            ),
            discord.Option(
                str,
                name="currency",
                description="Type of currency to pay. Tokens by default.",
                default="tokens",
                choices=[
                    discord.OptionChoice(
                        name="Tokens",
                        value="tokens"
                    ),
                    discord.OptionChoice(
                        name="Shinies",
                        value="shinies"
                    )
                ]
            )
        ]
    )
    async def pay(self, context: discord.ApplicationContext, user: discord.Member, amount: int, currency: int):
        payer_game_data: dict = self.bot.get_user_data(context.author.id)
        payee_game_data: dict = self.bot.get_user_data(user.id)

        if amount <= 0:
            await context.interaction.response.send_message("Amount needs to be above 0.", ephemeral=True)
            return

        if currency == "tokens":
            if payer_game_data["tokens"] < amount:
                response = await context.respond("Insufficient tokens.")
                await response.delete_original_response(delay=3)
                return
            else:
                payer_game_data["tokens"] -= amount
                payee_game_data["tokens"] += amount
                await context.respond(f"Paid {user.mention} {amount} :coin:.")
        elif currency == "shinies":
            if payer_game_data["shinies"] < amount:
                response = await context.respond("Insufficient shinies.")
                await response.delete_original_response(delay=3)
                return
            else:
                payer_game_data["shinies"] -= amount
                payee_game_data["shinies"] += amount
                await context.respond(f"Paid {user.mention} {amount} ✨.")

        self.bot.save_data()

    # Class for the Valuate Command View
    class ValuateView(discord.ui.View):
        def __init__(self, game, member_game_data: dict, selected_item: dict, selected_item_info: dict, inventory_slot: int, count: int, *items: discord.ui.Item):
            super().__init__(*items, timeout=60)
            self.game: GameBase = game
            self.count = count
            self.inventory_slot = inventory_slot
            self.member_game_data = member_game_data
            self.selected_item = selected_item
            self.selected_item_info = selected_item_info

        async def on_timeout(self):
            for child in self.children:
                child.disabled = True
            await self.message.edit(view=self)

        @discord.ui.button(
            label="Sell",
            style=discord.ButtonStyle.blurple
        )
        async def sell_button_callback(self, button: discord.Button, interaction: discord.Interaction):
            if interaction.user != interaction.message.interaction.user:
                await interaction.response.send_message(content="You can't touch that!", ephemeral=True)
                return
            button.disabled = True
            button.label = "Sold"

            self.game.sell_item(interaction.user.id, self.inventory_slot, self.count)

            message = f"Sold **{self.selected_item_info['name']} ×{self.count}** for {self.selected_item_info['value'] * self.count} :coin:.\n" \
                      f"Your total is now {self.member_game_data['tokens']:,} :coin:."

            await interaction.response.edit_message(content=message, view=self)

    # Valuate items worth.
    @commands.slash_command(
        name="valuate",
        description="Determine an item's value and allows you to sell it.",
        options=[
            discord.Option(
                int,
                name="inventoryslot",
                description="Slot number of the item you want to valuate.",
                min_value=1
            ),
            discord.Option(
                int,
                name="amount",
                description="Amount of item you wish to sell. Default is all.",
                min_value=0,
                default=0
            ),
            discord.Option(
                bool,
                name="quicksell",
                description="Sell the item without the prompt, if possible.",
                default=False
            )
        ]
    )
    async def valuate(self, context: discord.ApplicationContext, inventory_slot: int, amount: int, quick_sell: bool):
        member_game_data = self.bot.get_user_data(context.author.id)

        inventory_page = inventory_slot // 10

        try:
            selected_item: dict = member_game_data["inventory"][inventory_page][inventory_slot-1]
        except IndexError:
            await context.interaction.response.send_message(content="That inventory slot is empty.", ephemeral=True)
            return

        selected_item_info = self.bot.ITEM_INFO_DICT[selected_item["id"]]

        if not selected_item_info["sellable"]:  # if item is unsellable
            await context.interaction.response.send_message(content="This item is unsellable.", ephemeral=True)
            return

        if amount > selected_item['count']:
            await context.interaction.response.send_message(content="You do not have enough of this item.", ephemeral=True)
            return

        if amount == 0:
            amount = selected_item['count']

        total_sale_value = selected_item_info['value'] * amount

        message = f"**{selected_item_info['name']} ×{amount:,}:** {total_sale_value:,} :coin:\n" \
                  f"({selected_item_info['value']:,} :coin: per item)"

        if not quick_sell:
            await context.respond(message, view=self.ValuateView(self, member_game_data, selected_item, selected_item_info, inventory_slot, amount))
        else:
            self.sell_item(context.author.id, inventory_slot, amount)

            message = f"Sold **{selected_item_info['name']} ×{amount}** for {selected_item_info['value'] * amount} :coin:.\n" \
                      f"Your total is now {member_game_data['tokens']:,} :coin:."
            await context.respond(message)

    # TODO: Trade items.

    # TODO: Secret secret. I've got a secret.

    # Admin Commands
    # Give Item
    @commands.slash_command(
        name="give",
        description="Coolant Admin: Give user an item.",
        options=[
            discord.Option(
                discord.User,
                name="user",
                description="User to give the item to."
            ),
            discord.Option(
                str,
                name="item_id",
                description="The id of the item."
            ),
            discord.Option(
                int,
                name="count",
                description="Number of the item. Default is 1.",
                default=1
            )
        ]
    )
    async def give_item(self, context: discord.ApplicationContext, user: discord.User, item_id: str, count: int):
        if context.author.id not in self.ADMIN_LIST:
            await context.interaction.response.send_message("Improper perms!", ephemeral=True)
            return

        self.add_item_to_inventory(user.id, {"id": item_id, "count": count})
        await context.interaction.response.send_message("Gave item(s).", ephemeral=True)
        await self.bot.log_print(f"{context.author} gave item {item_id} to {user.id}.")

    # Take Item
    @commands.slash_command(
        name="take",
        description="Coolant Admin: Take an item from a user.",
        options=[
            discord.Option(
                discord.User,
                name="user",
                description="The user to take the item from."
            ),
            discord.Option(
                str,
                name="item_id",
                description="The id of the item."
            ),
            discord.Option(
                int,
                name="count",
                description="Number of the item to remove. Default is all.",
                default=-1
            )
        ]
    )
    async def take_item(self, context: discord.ApplicationContext, user: discord.User, item_id: str, count=-1):
        if context.author.id not in self.ADMIN_LIST:
            await context.interaction.response.send_message("Improper perms!", ephemeral=True)
            return

        self.remove_item_from_inventory(user.id, item_id, count)
        await context.interaction.response.send_message("Removed item(s).", ephemeral=True)
        await self.bot.log_print(f"{context.author} took {count} {item_id} from {user.id}.")

    # Money
    @commands.slash_command(
        name="money",
        description="Coolant Admin: Add or subtract tokens/shinies from a user.",
        options=[
            discord.Option(
                discord.Member,
                name="user",
                description="User you are giving to/taking from."
            ),
            discord.Option(
                int,
                name="amount",
                description="Amount of currency. Use negative to subtract."
            ),
            discord.Option(
                str,
                name="currency",
                description="Type of currency to modify.",
                default="tokens",
                choices=[
                    discord.OptionChoice("Tokens", "tokens"),
                    discord.OptionChoice("Shinies", "shinies")
                ]
            )
        ]
    )
    async def money(self, context: discord.ApplicationContext, user: discord.Member, amount: int, currency: str):
        if context.author.id not in self.ADMIN_LIST:
            await context.interaction.response.send_message("Improper perms!", ephemeral=True)
            return

        member_game_data: dict = self.bot.get_user_data(user.id)
        if currency == "tokens":
            member_game_data["tokens"] = max(0, member_game_data["tokens"] + amount)
            await context.interaction.response.send_message(f"Gave {user.display_name} {amount} :coin:.", ephemeral=True)
        elif currency == "shinies":
            member_game_data["shinies"] = max(0, member_game_data["shinies"] + amount)
            await context.interaction.response.send_message(f"Gave {user.display_name} {amount} :sparkles:.", ephemeral=True)
