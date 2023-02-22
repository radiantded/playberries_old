import json
import os

from colorama import Fore
from dotenv import load_dotenv


load_dotenv()

PROXY_SITE = os.environ.get('PROXY_SITE')
BOT_TOKEN = os.environ.get('TEST_TOKEN')
AUTH_USERS = json.loads(os.environ.get('AUTH_USERS'))
PAGE_RETRIES = 21
OPTIONS_RETRIES = 11

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 OPR/70.0.3728.95',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36 Edg/86.0.622.51',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11.0.0; SM-G960F Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/80.0.3987.95 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 9; HUAWEI OS) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Mobile Safari/537.36'
]

CONSOLE_COLORS = [
    Fore.RED, Fore.GREEN, Fore.BLUE, 
    Fore.YELLOW, Fore.WHITE, Fore.MAGENTA, Fore.CYAN
]
