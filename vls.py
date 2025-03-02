import json
import discord
from dbhelpers import get_user_data, update_user_data
import asyncio
import datetime
from colorama import Fore, Style, init

init(autoreset=True)

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}[ERROR] config.json not found. Please create it.{Style.RESET_ALL}")
        return None
    except json.JSONDecodeError:
        print(f"{Fore.RED}[ERROR] config.json is not valid JSON. Please correct it.{Style.RESET_ALL}")
        return None

config = load_config()

if config is None:
    exit()

voice_activity = {}

def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

async def process_voice_activity(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    user_id = member.id
    current_time = asyncio.get_event_loop().time()

    try:
        if before.channel is None and after.channel is not None:
            voice_activity[user_id] = current_time
            print(f"{get_current_time()} {Fore.CYAN}[VOICE JOIN]{Style.RESET_ALL} User {member.name} joined voice channel {after.channel.name}")
        elif before.channel is not None and after.channel is None and user_id in voice_activity:
            time_spent = current_time - voice_activity[user_id]
            del voice_activity[user_id]
            await add_voice_xp(member, time_spent)
            print(f"{get_current_time()} {Fore.CYAN}[VOICE LEAVE]{Style.RESET_ALL} User {member.name} left voice channel {before.channel.name}. Time spent: {time_spent} seconds.")
        elif before.channel != after.channel and before.channel is not None and after.channel is not None:
            print(f"{get_current_time()} {Fore.CYAN}[VOICE SWITCH]{Style.RESET_ALL} User {member.name} switched voice channel from {before.channel.name} to {after.channel.name}.")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {get_current_time()} Error processing voice activity: {e}{Style.RESET_ALL}")

async def add_voice_xp(member: discord.Member, time_spent: float):
    user_id = member.id
    data = get_user_data(user_id)

    try:
        xpv = data['xpv'] + int(time_spent)
        ovxpv = data['ovxpv'] + int(time_spent)
        vlevel = data['vlevel']
        required_xpv = eval(config['required_voice_xp_formula'].replace('level', str(vlevel)))

        print(f"{get_current_time()} {Fore.YELLOW}[VOICE XP]{Style.RESET_ALL} User {member.name} gained {int(time_spent)} voice XP. Current XP: {xpv}, Required XP: {required_xpv}")

        if xpv >= required_xpv:
            vlevel += 1
            xpv = 0
            channel = member.guild.get_channel(int(config['voice_levelup_channel']))
            if channel is None:
                print(f"{Fore.RED}[ERROR] {get_current_time()} Voice level up channel not found. Check 'voice_levelup_channel' in config.json.{Style.RESET_ALL}")
                return
            embed = discord.Embed(
                title=config['voice_levelup_title'],
                description=config['voice_levelup_message'].format(user=member.mention, level=vlevel),
                color=int(config['voice_message_color'].lstrip('#'), 16)
            )
            await channel.send(embed=embed)
            print(f"{get_current_time()} {Fore.GREEN}[VOICE LEVELUP]{Style.RESET_ALL} User {member.name} leveled up to {vlevel} (voice)")
        else:
            print(f"{get_current_time()} {Fore.RED}[VOICE XP]{Style.RESET_ALL} User {member.name} did not level up.")

        update_user_data(user_id, data['xpt'], data['ovxpt'], data['tlevel'], xpv, ovxpv, vlevel)
        print(f"{get_current_time()} {Fore.MAGENTA}[DATABASE]{Style.RESET_ALL} User {member.name} voice data updated.")
    except KeyError as e:
        print(f"{Fore.RED}[ERROR] {get_current_time()} Missing configuration key: {e}. Check config.json.{Style.RESET_ALL}")
    except ValueError as e:
        print(f"{Fore.RED}[ERROR] {get_current_time()} Invalid value in configuration: {e}. Check config.json.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR] {get_current_time()} An unexpected error occurred: {e}. If you believe it is not due to incompetent setup, please contact @avefoxiu on discord.{Style.RESET_ALL}")