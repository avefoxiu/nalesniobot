import discord
from discord import app_commands
from dbhelpers import get_user_data, get_top_text_users
import json

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()

guild_ids = config.get('guild_ids', [])

@app_commands.command(name="xpt", description="Displays text XP stats", guild_ids=guild_ids)
async def text_xp_command(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    data = get_user_data(user.id)

    embed = discord.Embed(
        title=config['text_xp_title'],
        color=int(config['text_message_color'].lstrip('#'), 16)
    )
    embed.add_field(name=config['text_xp_level_label'], value=data['tlevel'], inline=False)
    embed.add_field(name=config['text_xp_overall_xp_label'], value=data['ovxpt'], inline=False)
    embed.add_field(name=config['text_xp_current_xp_label'], value=data['xpt'], inline=False)

    await interaction.response.send_message(embed=embed)

@app_commands.command(name="toptext", description="Displays top text users", guild_ids=guild_ids)
async def top_text_command(interaction: discord.Interaction, offset: int = 0):
    users = get_top_text_users(offset)
    embed = discord.Embed(
        title=config['top_text_title'],
        color=int(config['text_message_color'].lstrip('#'), 16)
    )
    for i, user_data in enumerate(users):
        user = interaction.guild.get_member(user_data['discord_id'])
        if user:
            embed.add_field(name=f"{i + 1 + offset}. {user.display_name}", value=f"{config['text_xp_level_label']}: {user_data['tlevel']}, {config['text_xp_overall_xp_label']}: {user_data['ovxpt']}", inline=False)

    view = TopTextView(offset)
    await interaction.response.send_message(embed=embed, view=view)

class TopTextView(discord.ui.View):
    def __init__(self, offset):
        super().__init__()
        self.offset = offset

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.offset > 0:
            self.offset -= 10
            await top_text_command(interaction, self.offset)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.offset += 10
        await top_text_command(interaction, self.offset)
