# roles.py
import json
import random

from discord.ext import commands
import discord
# local modules
import coolant


class Roles(commands.Cog):
    def __init__(self, bot_client: coolant.CoolantBot):
        self.bot = bot_client

        with open("./data/bot_data.json", "r") as f:
            self.BOT_ROLE_ID: int = json.loads(f.read())['bot_role_id']

        with open("./store/roles.json", "r") as f:
            self.roles: dict = json.loads(f.read())

        with open("./data/colors.json", "r") as f:
            self.COLORS: dict = json.loads(f.read())

    # roles subcommand group
    roles_group = discord.SlashCommandGroup("role", "Modify your coolant role.")

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                await self.update_role(member, save=False)

        self.save_role_data()

    def save_role_data(self):
        with open("./store/roles.json", "w") as f:
            json.dump(self.roles, f, ensure_ascii=False, indent=2)

    async def update_role(self, user: discord.Member, name: str or None = None, color: int or None = None, save: bool = True):
        if user.bot:
            return

        if str(user.id) not in self.roles.keys():
            user_role = await user.guild.create_role(
                name=name if name is not None else user.name
            )

            bot_role_position = user.guild.get_member(self.bot.user.id).get_role(self.BOT_ROLE_ID).position

            await user_role.edit(position=bot_role_position-1)
            if color is not None: await user_role.edit(color=color)

            self.roles[str(user.id)] = {
                "role_id": user_role.id,
                "permion": None
            }

            await self.bot.log_print(f"New role {user_role.name} created!")
            await user.add_roles(user_role)
        else:
            user_role = user.get_role(self.roles[str(user.id)]['role_id'])
            if name:
                await user_role.edit(name=name)
            if color:
                await user_role.edit(color=color)

        if save: self.save_role_data()

    def int_into_color_hex(self, color: int) -> str:
        hex_color = hex(color).lstrip('0x')
        hex_color = hex_color.zfill(len(hex_color)-6)
        return hex_color

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
        async def shuffle_callback(self, button: discord.Button, interaction: discord.Interaction):
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
        async def accept_callback(self, button: discord.Button, interaction: discord.Interaction):
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
                name="hex",
                description="The hex code of the color. Default is random.",
                default=None,
                min_length=6,
                max_length=6
            ),
            discord.Option(
                str or None,
                name="colorname",
                description="The name of the color. If the name is not a color name, it will be random.",
                default=None
            )
        ]
    )
    async def change_role_color(self, context: discord.ApplicationContext, hex_string: str or None, color_name: str or None):
        if color_name and color_name.title() in self.COLORS.keys():
            hex_color = int(self.COLORS[color_name.title()], 16)
        elif hex_string is None:
            hex_color = random.randint(0, 0xFFFFFF)
        else:
            hex_color = int(hex_string.strip('#'), 16)

        if 0 <= hex_color >= 0xFFFFFF:
            await context.response.send_message(content="Invalid hex code!", ephemeral=True)

        formatted_hex = hex(hex_color).lstrip('0x').upper().zfill(6)

        color_embed = discord.Embed(
            title="Color:",
            description=f"**#{formatted_hex}**",
            color=hex_color
        )

        color_embed.set_thumbnail(url=f"https://via.placeholder.com/50/{formatted_hex}/{formatted_hex}.png")

        await context.response.send_message(embed=color_embed, ephemeral=True, view=self.RoleColorView(self, hex_color, context.author.get_role(self.roles[str(context.author.id)]['role_id']), color_embed))
