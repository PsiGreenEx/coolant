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
                description="Number of tokens to bet. Min bet is 10. Max bet is 3,000.",
                min_value=10,
                max_value=3000
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

        fruits: list[str] = ["🍇", "🍒", "🍊", "🍉", "🍋", "🫐", "🍑"]

        outcome_chances: dict = {
            "any fruit": 0.3,
            "triple fruit": 0.13,
            "bell": 0.06,
            "diamond": 0.01,
            "jackpot": 0.001
        }

        scaled_outcome_chances: dict = {
            "jackpot": (0, outcome_chances['jackpot']),
            "diamond": (outcome_chances['jackpot'], outcome_chances['jackpot']+outcome_chances['diamond']),
            "bell":  (outcome_chances['jackpot']+outcome_chances['diamond'], outcome_chances['jackpot']+outcome_chances['diamond']+outcome_chances['bell']),
            "triple fruit": (outcome_chances['jackpot']+outcome_chances['diamond']+outcome_chances['bell'],
                             outcome_chances['jackpot']+outcome_chances['diamond']+outcome_chances['bell']+outcome_chances['triple fruit']),
            "any fruit": (outcome_chances['jackpot']+outcome_chances['diamond']+outcome_chances['bell']+outcome_chances['triple fruit'],
                          outcome_chances['jackpot']+outcome_chances['diamond']+outcome_chances['bell']+outcome_chances['triple fruit']+outcome_chances['any fruit'])
        }

        outcome_random_value = random.random()
        outcome = "none"

        for outcome_string, chance_range in scaled_outcome_chances.items():
            if chance_range[0] < outcome_random_value <= chance_range[1]:
                outcome = outcome_string

        member_game_data = self.bot.get_user_data(context.author.id)

        if bet > member_game_data["tokens"]:
            await context.interaction.response.send_message(content="Insufficient tokens!", ephemeral=True)
            return

        member_game_data["tokens"] -= bet
        payout = 0
        jackpot = False

        slots: list[str] = ["", "", ""]

        if outcome == "any fruit":
            while True:
                slots[0] = random.choice(fruits)
                slots[1] = random.choice(fruits)
                slots[2] = random.choice(fruits)
                if not (slots[0] == slots[1] == slots[2]): break

            payout = round(bet * 1.3)

            payout_message = f"**Triple Fruit!**\n" \
                             f"**Payout:** {payout} {Emojis.TOKEN} ({bet}×1.3)"
        elif outcome == "triple fruit":
            tripled_fruit = random.choice(fruits)
            slots[0] = tripled_fruit
            slots[1] = tripled_fruit
            slots[2] = tripled_fruit

            payout = bet * 2

            payout_message = f"**Triple {slots[0]}!**\n" \
                             f"**Payout:** {payout} {Emojis.TOKEN} ({bet}×2)"
        elif outcome == "none":
            while True:
                if random.random() >= 0.33:
                    teaser_symbol = random.choice(list(slot_symbols.values()))  # i am pure evil
                    slots[0] = teaser_symbol
                    slots[1] = teaser_symbol
                else:
                    slots[0] = random.choice(list(slot_symbols.values()))
                    slots[1] = random.choice(list(slot_symbols.values()))

                slots[2] = random.choice(list(slot_symbols.values()))
                if not (slots[0] == slots[1] == slots[2]) and not all(i in fruits for i in slots): break

            payout_message = "Better luck next time!"
        else:
            slots[0] = slot_symbols[outcome]
            slots[1] = slot_symbols[outcome]
            slots[2] = slot_symbols[outcome]

            if outcome == "bell":
                payout = bet * 4

                payout_message = f"**Triple {slots[0]}!**\n" \
                                 f"**Payout:** {payout} {Emojis.TOKEN} ({bet}×4)"
            elif outcome == "diamond":
                payout = bet * 8

                payout_message = f"**Triple {slots[0]}!**\n" \
                                 f"**Payout:** {payout} {Emojis.TOKEN} ({bet}×8)"
            elif outcome == "jackpot":
                payout = bet * 23
                jackpot = True

                payout_message = f"**Jackpot!**\n" \
                                 f"**Payout:** {payout} {Emojis.TOKEN} ({bet}×23) and 5 {Emojis.SHINY}Shinies{Emojis.SHINY}!"
            else:
                payout_message = "<:realer:883844085805350932> (tell psi about this something is BROKE)"

        # Spinning
        await context.respond(f"**Bet is:** {bet} {Emojis.TOKEN}\n"
                              f"** <a:loading:1029896164981604423> Spinning:** \n"
                              f"❔ ❔ ❔")
        await asyncio.sleep(1)
        await context.edit(content=f"**Bet is:** {bet} {Emojis.TOKEN}\n"
                                   f"** <a:loading:1029896164981604423> Spinning:** \n"
                                   f"{slots[0]} ❔ ❔")
        await asyncio.sleep(1)
        await context.edit(content=f"**Bet is:** {bet} {Emojis.TOKEN}\n"
                                   f"** <a:loading:1029896164981604423> Spinning:** \n"
                                   f"{slots[0]} {slots[1]} ❔")
        await asyncio.sleep(1)
        message = f"**Bet is:** {bet} {Emojis.TOKEN}\n" \
                  f"**Finished!** \n" \
                  f"{slots[0]} {slots[1]} {slots[2]}\n\n"
        await context.edit(content=message)

        message += payout_message

        member_game_data["tokens"] += payout
        if jackpot: member_game_data["shinies"] += 5

        self.bot.save_data()
        await asyncio.sleep(1)
        await context.edit(content=message)
