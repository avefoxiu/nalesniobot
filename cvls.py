import discord
from discord import app_commands
from dbhelpers import get_user_data, get_top_voice_users
import json
import datetime

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()

async def voice_xp_command(interaction: discord.Interaction, user: discord.Member = None, guild_ids=None):
    user = user or interaction.user
    data = get_user_data(user.id)

    embed = discord.Embed(
        title=config['voice_xp_title'],
        color=int(config['voice_message_color'].lstrip('#'), 16)
    )
    embed.add_field(name=config['voice_xp_level_label'], value=data['vlevel'], inline=False)
    embed.add_field(name=config['voice_xp_overall_xp_label'], value=data['ovxpv'], inline=False)
    embed.add_field(name=config['voice_xp_current_xp_label'], value=data['xpv'], inline=False)

    embed.set_footer(text=f"Invoked by {interaction.user.name} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    await interaction.response.send_message(embed=embed)

async def top_voice_command(interaction: discord.Interaction, offset: int = 0, guild_ids=None):
    users = get_top_voice_users(offset)
    embed = discord.Embed(
        title=config['top_voice_title'],
        color=int(config['voice_message_color'].lstrip('#'), 16)
    )

    for i, user_data in enumerate(users):
        try:
            user = await interaction.client.fetch_user(user_data['discord_id'])
            if user:
                required_xp = eval(config['required_voice_xp_formula'].replace('level', str(user_data['vlevel'])))
                embed.add_field(
                    name=f"{i + 1 + offset}. {user.name}",
                    value=f"{config['voice_xp_level_label']}: {user_data['vlevel']}, {user_data['xpv']}/{required_xp} - {user_data['ovxpv']}",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"{i + 1 + offset}. User not found",
                    value=f"{config['voice_xp_level_label']}: {user_data['vlevel']}, {user_data['xpv']}/(required_xp) - {user_data['ovxpv']}",
                    inline=False
                )
        except discord.NotFound:
            embed.add_field(
                name=f"{i + 1 + offset}. User not found",
                value=f"{config['voice_xp_level_label']}: {user_data['vlevel']}, {user_data['xpv']}/(required_xp) - {user_data['ovxpv']}",
                inline=False
            )

    view = TopVoiceView(offset)

    embed.set_footer(text=f"Invoked by {interaction.user.name} | {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    await interaction.response.send_message(embed=embed, view=view)

class TopVoiceView(discord.ui.View):
    def __init__(self, offset):
        super().__init__()
        self.offset = offset

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.offset > 0:
            self.offset -= 10
            await top_voice_command(interaction, self.offset)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.offset += 10
        await top_voice_command(interaction, self.offset)
