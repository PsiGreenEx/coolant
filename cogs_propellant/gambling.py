# gambling.py
import random
import discord
import asyncio
from discord.ext import commands
# local modules
from propellant import PropellantBot, Emojis


class Gambling(commands.Cog):
    def __init__(self, bot_client: PropellantBot):
        self.bot = bot_client

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
            "lemon": "🍋",
            "blueberries": "🫐",
            "peach": "🍑",
            "bell": "🔔",
            "diamond": "💎",
            "jackpot": "<:23:1029169299526529024>"
        }

        member_game_data = self.bot.get_user_data(context.author.id)

        if bet > member_game_data["tokens"]:
            await context.interaction.response.send_message(content="Insufficient tokens!", ephemeral=True)
            return

        member_game_data["tokens"] -= bet
        payout = 0
        jackpot = False

        symbol_one = random.choice(list(slot_symbols.keys()))
        symbol_two = random.choice(list(slot_symbols.keys()))
        symbol_three = random.choice(list(slot_symbols.keys()))

        await context.respond(f"**Bet is:** {bet} {Emojis.TOKEN}\n"
                              f"** <a:loading:1029896164981604423> Spinning:** \n"
                              f"❔ ❔ ❔")
        await asyncio.sleep(1)
        await context.edit(content=f"**Bet is:** {bet} {Emojis.TOKEN}\n"
                                   f"** <a:loading:1029896164981604423> Spinning:** \n"
                                   f"{slot_symbols[symbol_one]} ❔ ❔")
        await asyncio.sleep(1)
        await context.edit(content=f"**Bet is:** {bet} {Emojis.TOKEN}\n"
                                   f"** <a:loading:1029896164981604423> Spinning:** \n"
                                   f"{slot_symbols[symbol_one]} {slot_symbols[symbol_two]} ❔")
        await asyncio.sleep(1)
        await context.edit(content=f"**Bet is:** {bet} {Emojis.TOKEN}\n"
                                   f"**Finished!** \n"
                                   f"{slot_symbols[symbol_one]} {slot_symbols[symbol_two]} {slot_symbols[symbol_three]}")
        message = f"**Bet is:** {bet} {Emojis.TOKEN}\n" \
                  f"**Finished!** \n" \
                  f"{slot_symbols[symbol_one]} {slot_symbols[symbol_two]} {slot_symbols[symbol_three]}\n\n"

        # Calculate Payout
        if symbol_one == symbol_two == symbol_three:  # if a match 3
            if symbol_one in ("grapes", "cherry", "orange", "watermelon", "lemon", "blueberries", "peach"):  # fruit payout
                payout = bet * 4
                message += f"**Triple {slot_symbols[symbol_one]}!**\n" \
                           f"**Payout:** {payout} {Emojis.TOKEN} ({bet}×4)"
            elif symbol_one == "bell":  # bell payout
                payout = bet * 5
                message += f"**Triple {slot_symbols[symbol_one]}!**\n" \
                           f"**Payout:** {payout} {Emojis.TOKEN} ({bet}×5)"
            elif symbol_one == "diamond":  # diamond payout
                payout = bet * 6
                message += f"**Triple {slot_symbols[symbol_one]}!**\n" \
                           f"**Payout:** {payout} {Emojis.TOKEN} ({bet}×6)"
            elif symbol_one == "jackpot":  # jackpot payout
                payout = bet * 23
                message += f"**JACKPOT!!!**\n" \
                           f"**Payout:** {payout} {Emojis.TOKEN} ({bet}×23) and a {Emojis.SHINY}Shiny{Emojis.SHINY}!"
                jackpot = True
        elif all(i in ("grapes", "cherry", "orange", "watermelon", "lemon", "blueberries", "peach") for i in
                 (symbol_one, symbol_two, symbol_three)):  # if a fruit match
            payout = round(bet * 1.5)
            message += f"**Triple Fruit!**\n" \
                       f"**Payout:** {payout} {Emojis.TOKEN} ({bet}×1.5)"
        else:
            message += "Better luck next time!"

        member_game_data["tokens"] += payout
        if jackpot: member_game_data["shinies"] += 1

        self.bot.save_data()
        await asyncio.sleep(1)
        await context.edit(content=message)
