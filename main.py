import discord
from discord.ext import commands
import json
import tls
import vls
import datetime

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=config['prefix'], intents=intents)

def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

@bot.event
async def on_ready():
    print(f'{get_current_time()} [INFO] Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await tls.process_text_message(message)
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    await vls.process_voice_activity(member, before, after)

bot.run(config['token'])