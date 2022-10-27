# roles.py
import json
import random

from discord.ext import commands
import discord
# local modules
from coolant import CoolantBot, load_role_data, save_role_data


class Roles(commands.Cog):
    def __init__(self, bot_client: CoolantBot):
        self.bot = bot_client

        with open("./data/bot_data.json", "r") as f:
            self.BOT_ROLE_ID: int = json.loads(f.read())['bot_role_id']

        with open("./data/colors.json", "r") as f:
            self.COLORS: dict = json.loads(f.read())

    # roles subcommand group
    roles_group = discord.SlashCommandGroup("role", "Modify your coolant role.")

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        roles = load_role_data()

        for guild in self.bot.guilds:
            for member in guild.members:
                await self.update_role(member, save=False, roles_data=roles)

        save_role_data(roles)

    @commands.Cog.listener("on_member_joined")
    async def on_member_joined(self, member: discord.Member):
        await self.update_role(member)

    async def update_role(self, user: discord.Member, name: str or None = None, color: int or None = None, save: bool = True, roles_data: dict or None = None):
        if user.bot:
            return

        if roles_data is None:
            roles_data = load_role_data()

        if str(user.id) not in roles_data.keys():
            user_role = await user.guild.create_role(
                name=name if name is not None else user.name
            )

            bot_role_position = user.guild.get_member(self.bot.user.id).get_role(self.BOT_ROLE_ID).position

            await user_role.edit(position=bot_role_position-1)
            if color is not None: await user_role.edit(color=color)

            roles_data[str(user.id)] = {
                "role_id": user_role.id,
                "permion": None,
                "keyword": None
            }

            await self.bot.log_print(f"New role {user_role.name} created!")
            await user.add_roles(user_role)
        elif user.get_role(roles_data[str(user.id)]['role_id']) is not None:
            await user.add_roles(user.guild.get_role(roles_data[str(user.id)]['role_id']))
        else:
            user_role = user.get_role(roles_data[str(user.id)]['role_id'])
            if name:
                await user_role.edit(name=name)
            if color:
                await user_role.edit(color=color)

        if save: save_role_data(roles_data)

    # Commands
    @roles_group.command(
        name="name",
        description="Change the name of your coolant role.",
        options=[
            discord.Option(
                str,
                name="name",
                description="The name you wish to change the role to."
            )
        ]
    )
    async def change_role_name(self, context: discord.ApplicationContext, name: str):
        await self.update_role(context.author, name=name)
        await context.response.send_message(content=f"Role name updated to {name}.", ephemeral=True)

    # Color Button View
    class RoleColorView(discord.ui.View):
        def __init__(self, roles_cog, color: int, role: discord.Role, embed: discord.Embed, *items: discord.ui.Item):
            super().__init__(timeout=60, *items)
            self.roles_cog: Roles = roles_cog
            self.color = color
            self.role = role
            self.embed = embed

        async def on_timeout(self):
            await self.message.delete()

        @discord.ui.button(
            label="Randomize"
        )
        async def shuffle_callback(self, _button: discord.Button, interaction: discord.Interaction):
            self.color = random.randint(0, 0xFFFFFF)

            self.embed = discord.Embed(
                title="Color:",
                description=f"**#{hex(self.color).lstrip('0x').upper()}**",
                color=self.color
            )

            formatted_hex = hex(self.color).lstrip('0x').upper().zfill(6)

            self.embed.set_thumbnail(url=f"https://via.placeholder.com/50/{formatted_hex}/{formatted_hex}.png")
            await interaction.response.edit_message(embed=self.embed)

        @discord.ui.button(
            label="Accept",
            style=discord.ButtonStyle.green
        )
        async def accept_callback(self, _button: discord.Button, interaction: discord.Interaction):
            await self.role.edit(color=self.color)
            self.embed.title = "Accepted"

            for child in self.children:
                child.disabled = True

            await interaction.response.edit_message(embed=self.embed, view=self)

    # Change Role Color
    @roles_group.command(
        name="color",
        description="Change the color of your coolant role.",
        options=[
            discord.Option(
                str or None,
                name="color",
                description="The hex code of the color OR the name of the color. Default is random.",
                default=None
            )
        ]
    )
    async def change_role_color(self, context: discord.ApplicationContext, color_input: str or None):
        role_data = load_role_data()

        if color_input and color_input.title() in self.COLORS.keys():
            hex_color = int(self.COLORS[color_input.title()], 16)
        elif color_input is None:
            hex_color = random.randint(0, 0xFFFFFF)
        else:
            hex_color = int(color_input.lstrip('#'), 16)

        if 0 <= hex_color >= 0xFFFFFF:
            await context.response.send_message(content="Invalid hex code!", ephemeral=True)

        formatted_hex = hex(hex_color).lstrip('0x').upper().zfill(6)

        color_embed = discord.Embed(
            title="Color:",
            description=f"**#{formatted_hex}**",
            color=hex_color
        )

        color_embed.set_thumbnail(url=f"https://via.placeholder.com/50/{formatted_hex}/{formatted_hex}.png")

        await context.response.send_message(embed=color_embed, ephemeral=True,
                                            view=self.RoleColorView(self, hex_color, context.author.get_role(role_data[str(context.author.id)]['role_id']), color_embed))
