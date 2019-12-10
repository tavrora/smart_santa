from dotenv import load_dotenv
load_dotenv()

import os

token = os.getenv("token")
socks5 = os.getenv("socks5")
bot_username = os.getenv("bot_username")