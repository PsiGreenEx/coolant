# game.py
import asyncio
import json
import discord
from datetime import date
import copy
import random
from discord.ext import commands
# local modules
import coolant


class Games(commands.Cog):
    def __init__(self, client: coolant.CoolantBot):
        self.client = client

        with open("./data/bot_data.json", "r") as f:
            bot_data = json.loads(f.read())
            self.ADMIN_LIST: list[int] = bot_data["admin_access_list"]

        # Game Information (such as item data)
        with open("./data/game_info.json", "r") as f:
            self.GAME_INFO_DICT: dict = json.loads(f.read())

        self.ITEM_INFO_DICT: dict = self.GAME_INFO_DICT['items']

        # Game Data (such as players' inventories)
        with open("./store/game_data.json", "r") as f:
            self.game_data_dict: dict = json.loads(f.read())

    # Save Game Data to JSON
    def save_data(self):
        with open('./store/game_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.game_data_dict, f, ensure_ascii=False, indent=2)

    # Get User Data and initialize if needed
    def get_user_data(self, user_id: int, reset=False) -> dict:
        if str(user_id) not in self.game_data_dict or reset:
            self.game_data_dict[str(user_id)] = copy.deepcopy(self.GAME_INFO_DICT["default_user"])
            self.save_data()
        return self.game_data_dict[str(user_id)]

    # Update a User's Data and save
    def update_user_data(self, user_id: int, user_game_data: dict):
        self.game_data_dict[str(user_id)] = user_game_data
        self.save_data()

    # Add item to user's inventory
    def add_item_to_inventory(self, user_id: int, new_item_data: dict):
        user_data: dict = self.get_user_data(user_id)
        user_inventory: list[list] = user_data["inventory"]
        new_item_info: dict = self.ITEM_INFO_DICT[new_item_data["id"]]
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

        self.save_data()

    # remove item from user's inventory
    def remove_item_from_inventory(self, user_id: int, item_id: str, count=-1):
        user_data: dict = self.get_user_data(user_id)
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
                        item_removed = True
                        break

            if item_removed: break

        self.save_data()

    # Convert Item Information into Discord Embed Field
    def item_dict_to_embed_field(self, item: dict, embed: discord.Embed):
        current_item_data = self.ITEM_INFO_DICT[item['id']]

        if current_item_data["max_count"] == 1:
            formatted_name = current_item_data['name']
        else:
            formatted_name = f"{current_item_data['name']} x{item['count']}"

        embed.add_field(
            name=formatted_name,
            value=current_item_data['description'],
            inline=False
        )

    # Create Embed of User's Inventory
    def generate_inventory_embed(self, member: discord.Member, page: int = 1) -> discord.Embed:
        member_game_data = self.get_user_data(member.id)
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
                  f"{member.nick}'s Inventory:",
            description=f"**:coin: AlloyTokens:** {member_game_data['tokens']:,}\n"
                        f"**✨ Shinies:** {member_game_data['shinies']:,}",
            color=0x006AF5
        )

        if member_inventory[page-1]:
            for item in member_inventory[page-1]:
                self.item_dict_to_embed_field(item, inventory_embed)

        return inventory_embed

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
            )
        ]
    )
    async def inventory(self, context: discord.ApplicationContext, page):
        author = context.author

        inventory_embed = self.generate_inventory_embed(author, page)

        await context.respond(embed=inventory_embed)
        await coolant.log_print(f"{author} checked their inventory.")

    # Daily Claim
    @commands.slash_command(
        name="claim",
        description="Claim your daily tokens!"
    )
    async def daily(self, context: discord.ApplicationContext):
        member_game_data = self.get_user_data(context.author.id)
        if date.fromisoformat(member_game_data['daily']['when_last_claimed']) < date.today():
            member_game_data['tokens'] += member_game_data['daily']['tokens_per_claim']
            message = f"You claimed {member_game_data['daily']['tokens_per_claim']:,} AlloyTokens. Your total is {member_game_data['tokens']:, :coin:}."

            if random.random() <= member_game_data['daily']['shiny_chance']:
                member_game_data['shinies'] += member_game_data['daily']['shinies_per_claim']
                message += f"\nWow! You found {member_game_data['daily']['shinies_per_claim']:,} ✨Shin{'y' if member_game_data['daily']['shinies_per_claim'] == 1 else 'ies'}✨! " \
                           f"Your total is {member_game_data['shinies']:, ✨}."

            member_game_data['daily']['when_last_claimed'] = date.today().isoformat()
            self.update_user_data(context.author.id, member_game_data)
            await context.respond(message)
            await coolant.log_print(f"{context.author} claimed their dailies.")
        else:
            response = await context.respond("You've already claimed your AlloyTokens for today!")
            await response.delete_original_response(delay=3)

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
        payer_game_data: dict = self.get_user_data(context.author.id)
        payee_game_data: dict = self.get_user_data(user.id)

        if currency == "tokens":
            if payer_game_data["tokens"] < amount:
                response = await context.respond("Insufficient tokens.")
                await response.delete_original_response(delay=3)
                return
            else:
                payer_game_data["tokens"] -= amount
                payee_game_data["tokens"] += amount
                await context.respond(f"Paid {user.display_name} {amount} :coin:.")
        elif currency == "shinies":
            if payer_game_data["shinies"] < amount:
                response = await context.respond("Insufficient shinies.")
                await response.delete_original_response(delay=3)
                return
            else:
                payer_game_data["shinies"] -= amount
                payee_game_data["shinies"] += amount
                await context.respond(f"Paid {user.nick} {amount} ✨.")

        self.save_data()

    # Spin the Slots
    @commands.slash_command(
        name="slots",
        description="Try your luck with the slot machine!",
        options=[
            discord.Option(
                int,
                name="bet",
                description="Number of tokens to bet. Min bet is 10. Max bet is 2,000.",
                min_value=10,
                max_value=2000
            )
        ]
    )
    async def spin_slots(self, context: discord.ApplicationContext, bet: int):
        slot_symbols: dict = {
            "grapes": "🍇",
            "cherry": "🍒",
            "orange": "🍊",
            "watermelon": "🍉",
            "bell": "🔔",
            "diamond": "💎",
            "jackpot": "<:23:1029169299526529024>"
        }

        member_game_data = self.get_user_data(context.author.id)

        if bet > member_game_data["tokens"]:
            await context.respond("Insufficient tokens!")
            return

        member_game_data["tokens"] -= bet

        payout = 0
        jackpot = False

        symbol_one = random.choice(list(slot_symbols.keys()))
        symbol_two = random.choice(list(slot_symbols.keys()))
        symbol_three = random.choice(list(slot_symbols.keys()))

        await context.respond(f"**Bet is:** {bet}\n"
                              f"** <a:loading:1029896164981604423> Spinning:** \n"
                              f"❔ ❔ ❔")
        async with context.channel.typing():
            await asyncio.sleep(1)
            await context.edit(content=f"**Bet is:** {bet}\n"
                                       f"** <a:loading:1029896164981604423> Spinning:** \n"
                                       f"{slot_symbols[symbol_one]} ❔ ❔")
            await asyncio.sleep(1)
            await context.edit(content=f"**Bet is:** {bet}\n"
                                       f"** <a:loading:1029896164981604423> Spinning:** \n"
                                       f"{slot_symbols[symbol_one]} {slot_symbols[symbol_two]} ❔")
            await asyncio.sleep(1)
            await context.edit(content=f"**Bet is:** {bet}\n"
                                       f"**Finished!** \n"
                                       f"{slot_symbols[symbol_one]} {slot_symbols[symbol_two]} {slot_symbols[symbol_three]}")
            message = f"**Bet is:** {bet}\n" \
                      f"**Finished!** \n" \
                      f"{slot_symbols[symbol_one]} {slot_symbols[symbol_two]} {slot_symbols[symbol_three]}\n"

            # Calculate Payout
            if symbol_one == symbol_two == symbol_three:  # if a match 3
                if symbol_one in ("grapes", "cherry", "orange", "watermelon"):
                    payout = bet * 2
                    message += f"**Triple {slot_symbols[symbol_one]}!**\n" \
                               f"**Payout:** {payout} :coin: ({bet}×2)"
                elif symbol_one == "bell":
                    payout = bet * 3
                    message += f"**Triple {slot_symbols[symbol_one]}!**\n" \
                               f"**Payout:** {payout} :coin: ({bet}×3)"
                elif symbol_one == "diamond":
                    payout = bet * 4
                    message += f"**Triple {slot_symbols[symbol_one]}!**\n" \
                               f"**Payout:** {payout} :coin: ({bet}×4)"
                elif symbol_one == "jackpot":
                    payout = bet * 23
                    message += f"**JACKPOT!!!**\n" \
                               f"**Payout:** {payout} :coin: ({bet}×23) and a ✨Shiny✨!"
                    jackpot = True
            elif all(i in ("grapes", "cherry", "orange", "watermelon") for i in (symbol_one, symbol_two, symbol_three)):  # if a fruit match
                payout = bet
                message += f"**Triple Fruit!**\n" \
                           f"**Payout:** {payout} :coin: ({bet}×1)"
            else:
                message += "Better luck next time!"

            member_game_data["tokens"] += payout
            if jackpot: member_game_data["shinies"] += 1
            self.save_data()
            await asyncio.sleep(1)
            await context.send_followup(message)

    # TODO: Sell items

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
            await context.respond("Improper perms!")
            return

        user_id = user.id

        self.add_item_to_inventory(user_id, {"id": item_id, "count": count})
        response: discord.Interaction = await context.respond("Gave item(s).")
        await coolant.log_print(f"{context.author} gave item {item_id} to {user_id}.")
        await response.delete_original_response(delay=3)

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
            await context.respond("Improper perms!")
            return

        user_id = user.id

        self.remove_item_from_inventory(user_id, item_id, count)
        response: discord.Interaction = await context.respond("Removed item(s).")
        await coolant.log_print(f"{context.author} took {count} {item_id} from {user_id}.")
        await response.delete_original_response(delay=3)
