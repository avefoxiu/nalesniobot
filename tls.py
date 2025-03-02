import json
import discord
from dbhelpers import get_user_data, update_user_data
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

def get_current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

async def process_text_message(message: discord.Message):
    user_id = message.author.id
    try:
        data = get_user_data(user_id)

        print(f"{get_current_time()} {Fore.CYAN}[MESSAGE]{Style.RESET_ALL} User {message.author.name} sent a message in channel {message.channel.name}")

        xpt = data['xpt'] + 1
        ovxpt = data['ovxpt'] + 1
        tlevel = data['tlevel']
        required_xpt = eval(config['required_text_xp_formula'].replace('level', str(tlevel)))

        print(f"{get_current_time()} {Fore.YELLOW}[XP]{Style.RESET_ALL} User {message.author.name} now has {xpt} XPT (required: {required_xpt})")

        if xpt >= required_xpt:
            tlevel += 1
            xpt = 0
            channel = message.guild.get_channel(int(config['text_levelup_channel']))
            if channel is None:
                print(f"{Fore.RED}[ERROR] {get_current_time()} Text level up channel not found. Check 'text_levelup_channel' in config.json.{Style.RESET_ALL}")
                return
            embed = discord.Embed(
                title=config['text_levelup_title'],
                description=config['text_levelup_message'].format(user=message.author.mention, level=tlevel),
                color=int(config['text_message_color'].lstrip('#'), 16)
            )
            await channel.send(embed=embed)
            print(f"{get_current_time()} {Fore.GREEN}[LEVELUP]{Style.RESET_ALL} User {message.author.name} leveled up to {tlevel} (text)")
        else:
            print(f"{get_current_time()} {Fore.RED}[XP]{Style.RESET_ALL} User {message.author.name} did not level up")

        update_user_data(user_id, xpt, ovxpt, tlevel, data['xpv'], data['ovxpv'], data['vlevel'])
        print(f"{get_current_time()} {Fore.MAGENTA}[DATABASE]{Style.RESET_ALL} User {message.author.name} data updated")
    except KeyError as e:
        error_message = f"Brak klucza konfiguracyjnego: {e}. Sprawdź config.json."
        await send_error_embed(message, error_message)
        print(f"{Fore.RED}[ERROR] {get_current_time()} Missing configuration key: {e}. Check config.json.{Style.RESET_ALL}")
    except ValueError as e:
        error_message = f"Nieprawidłowa wartość w konfiguracji: {e}. Sprawdź config.json."
        await send_error_embed(message, error_message)
        print(f"{Fore.RED}[ERROR] {get_current_time()} Invalid value in configuration: {e}. Check config.json.{Style.RESET_ALL}")
    except Exception as e:
        error_message = f"Wystąpił nieoczekiwany błąd: {e}. Zgłoś to do administratora."
        await send_error_embed(message, error_message)
        print(f"{Fore.RED}[ERROR] {get_current_time()} An unexpected error occurred: {e}{Style.RESET_ALL}")

async def send_error_embed(message: discord.Message, error_message: str):
    embed = discord.Embed(
        title="Wystąpił błąd!",
        description=error_message + "\n\nZgłoś ten problem do administratora serwera.",
        color=discord.Color.red()
    )
    await message.channel.send(embed=embed)
