import discord
from discord import app_commands
import json
from tls import process_text_message
from vls import process_voice_activity
from ctls import text_xp_command, top_text_command, TopTextView
from cvls import voice_xp_command, top_voice_command, TopVoiceView
from dbhelpers import create_levels_table
import os

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("[ERROR] config.json not found. Please create it.")
        return None
    except json.JSONDecodeError:
        print("[ERROR] config.json is not valid JSON. Please correct it.")
        return None

config = load_config()

if config is None:
    exit()

guild_ids = config.get('guild_ids', [])
MY_GUILD = discord.Object(id=int(guild_ids[0])) if guild_ids else None

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        if MY_GUILD:
            self.tree.copy_global_to(guild=MY_GUILD)
            await self.tree.sync(guild=MY_GUILD)
        else:
            await self.tree.sync()

client = MyClient(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')
    create_levels_table()

@client.tree.command(name="textxp", description="Displays text XP stats")
async def textxp(interaction: discord.Interaction, user: discord.Member = None):
    await text_xp_command(interaction, user, guild_ids)

@client.tree.command(name="toptext", description="Displays top text users")
async def toptext(interaction: discord.Interaction, offset: int = 0):
    await top_text_command(interaction, offset, guild_ids)

@client.tree.command(name="voicexp", description="Displays voice XP stats")
async def voicexp(interaction: discord.Interaction, user: discord.Member = None):
    await voice_xp_command(interaction, user, guild_ids)

@client.tree.command(name="topvoice", description="Displays top voice users")
async def topvoice(interaction: discord.Interaction, offset: int = 0):
    await top_voice_command(interaction, offset, guild_ids)

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    await process_text_message(message)

@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    await process_voice_activity(member, before, after)

client.run(config['token'])
