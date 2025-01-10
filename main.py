import tls_client
import random
import string
import time
import re
import threading
import json
import colorama
import ctypes
import platform
import sys
import os
import shutil
from datetime import datetime
from websocket import WebSocket
from typing import Optional
import requests
import base64


# Utility Functions
class Utils:
    @staticmethod
    def random_username(length: int = 8) -> str:
        """Generate a random username with letters only."""
        return ''.join(random.choices(string.ascii_letters, k=length))

    @staticmethod
    def fetch_buildnum() -> int:
        try:
            asset_files = re.findall(r'<script\s+src="([^"]+\.js)"\s+defer>\s*</script>', requests.get("https://discord.com/login").text)
            for js_endpoint in asset_files:
                resp = requests.get(f"https://discord.com/{js_endpoint}")
                try:
                    return int(resp.text.split('"buildNumber",(_="')[1].split('"')[0])
                except (IndexError, ValueError):
                    continue
        except Exception as e:
            Log.warn(f"Failed to fetch build number: {e}")
        return 295805

    @staticmethod
    def build_x_context_properties(location: str) -> str:
        try:
            data = {"location": location}
            return base64.b64encode(json.dumps(data).encode()).decode()
        except Exception as e:
            Log.warn(f"Error building x-context-properties: {e}")
            return ""

    @staticmethod
    def nonce() -> str:
        try:
            return str((int(time.mktime(datetime.now().timetuple())) * 1000 - 1420070400000) * 4194304)
        except Exception as e:
            Log.warn(f"Error generating nonce: {e}")
            return "0"

    @staticmethod
    def build_xsup(user_agent: str, ua_version: str, build_num: int) -> str:
        try:
            data = {
                "os": "Windows",
                "browser": "Chrome",
                "device": "",
                "system_locale": "en-US",
                "browser_user_agent": user_agent,
                "browser_version": f"{ua_version}.0.0.0",
                "os_version": "10",
                "referrer": "",
                "referring_domain": "",
                "referrer_current": "https://discord.com/",
                "referring_domain_current": "discord.com",
                "release_channel": "stable",
                "client_build_number": build_num,
                "client_event_source": None,
                "design_id": 0
            }
            return base64.b64encode(json.dumps(data, separators=(",", ":")).encode()).decode()
        except Exception as e:
            Log.warn(f"Error building x-super-properties: {e}")
            return ""


# Logging Utility
class Log:
    colorama.init(autoreset=True)

    @staticmethod
    def amazing(msg: str, symbol="U"):
        Log._log(msg, symbol, colorama.Fore.BLUE)

    @staticmethod
    def good(msg: str, symbol="+"):
        Log._log(msg, symbol, colorama.Fore.LIGHTBLUE_EX)

    @staticmethod
    def info(msg: str, symbol="="):
        Log._log(msg, symbol, colorama.Fore.LIGHTCYAN_EX)

    @staticmethod
    def bad(msg: str, symbol="X"):
        Log._log(msg, symbol, colorama.Fore.RED)

    @staticmethod
    def warn(msg: str, symbol="!"):
        Log._log(msg, symbol, colorama.Fore.YELLOW)

    @staticmethod
    def _log(msg: str, symbol: str, color: str):
        print(f"[{colorama.Fore.LIGHTBLACK_EX}{datetime.now().strftime('%H:%M:%S')}{colorama.Fore.RESET}] "
              f"({color}{symbol}{colorama.Fore.RESET}) - {msg}")


# UI Utility
class UI:
    @staticmethod
    def clear(title: Optional[str] = None):
        if platform.system() == 'Windows':
            os.system(f'cls {title if title else ""}')
        elif platform.system() == 'Linux':
            os.system('clear')
        elif platform.system() == 'Darwin':
            os.system("clear && printf '\e[3J'")

    @staticmethod
    def show():
        colorama.init(autoreset=True)
        logo_text = """
        ██████╗ ██████╗  ██████╗ ████████╗ ██████╗ ███╗   ██╗     ██████╗ ███████╗███╗   ██╗
        ██╔══██╗██╔══██╗██╔═████╗╚══██╔══╝██╔═████╗████╗  ██║    ██╔════╝ ██╔════╝████╗  ██║
        ██████╔╝██████╔╝██║██╔██║   ██║   ██║██╔██║██╔██╗ ██║    ██║  ███╗█████╗  ██╔██╗ ██║
        ██╔═══╝ ██╔══██╗████╔╝██║   ██║   ████╔╝██║██║╚██╗██║    ██║   ██║██╔══╝  ██║╚██╗██║
        ██║     ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚████║    ╚██████╔╝███████╗██║ ╚████║
        ╚═╝     ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝  ╚═══╝     ╚═════╝ ╚══════╝╚═╝  ╚═══╝
        """
        console_width = shutil.get_terminal_size().columns
        colors = [colorama.Fore.RED, colorama.Fore.LIGHTMAGENTA_EX, colorama.Fore.CYAN, colorama.Fore.LIGHTCYAN_EX]

        for line in logo_text.splitlines():
            print(random.choice(colors) + line.center(console_width))

    @staticmethod
    def get_api_key() -> str:
        return input(f"\n{colorama.Fore.BLUE}[>] Enter your RazorCap API Key: {colorama.Fore.RESET}")


# RazorCap Captcha Solver
class Captcha:
    @staticmethod
    def solve(api_key: str, sitekey: str, siteurl: str, proxy: str, rqdata: Optional[str] = None) -> Optional[str]:
        try:
            payload = {
                'key': api_key,
                'type': 'hcaptcha_basic',
                'data': {
                    'sitekey': sitekey,
                    'siteurl': siteurl,
                    'proxy': proxy
                }
            }
            if rqdata:
                payload['data']['rqdata'] = rqdata

            Log.info(f"Sending captcha solving request to RazorCap...")
            response = requests.post("https://api.razorcap.xyz/create_task", json=payload)
            response_data = response.json()

            if response_data.get('status') == 'success':
                return response_data.get('solution')
            else:
                Log.bad(f"Captcha solving failed: {response_data}")
                return None
        except Exception as e:
            Log.bad(f"Error solving captcha with RazorCap: {e}")
            return None


# Main Discord Class
class Discord:
    def __init__(self, config, proxies):
        try:
            self.config = config
            self.proxies = proxies
            self.proxy = random.choice(proxies)
            self.username = Utils.random_username(random.randint(6, 12))
            self.email = f"{self.username}@gmail.com"
            self.password = config.get('password', 'default_password')
            self.token = None
            Log.good(f"Initialized Discord object with proxy: {self.proxy}, username: {self.username}")
        except Exception as e:
            Log.bad(f"Error during initialization: {e}")

    def begin(self):
        try:
            Log.good("Starting Discord operations...")
            self.create_account()
        except Exception as e:
            Log.bad(f"Error in Discord.begin: {e}")

    def create_account(self):
        try:
            Log.info("Creating account...")
            captcha_solution = Captcha.solve(
                api_key=self.config['captcha_api_key'],
                sitekey="4c672d35-0701-42b2-88c3-78380b0db560",
                siteurl="https://discord.com",
                proxy=self.proxy
            )
            if captcha_solution:
                Log.amazing(f"Captcha solved: {captcha_solution[:10]}...")
                # Construct the payload to send for account creation
                payload = {
                    "email": self.email,
                    "username": self.username,
                    "password": self.password,
                    "captcha_key": captcha_solution,  # The solved captcha key
                    "invite": None,  # If you have a specific invite code, include it here
                    "consent": True,  # Consent checkbox
                    "date_of_birth": "2000-01-01",  # Provide a valid birthdate in the proper format
                }

                # Send request to Discord's account creation endpoint
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": self.config.get('user_agent', 'Mozilla/5.0'),
                    "X-Super-Properties": Utils.build_xsup(self.config.get('user_agent', 'Mozilla/5.0'), '99', 295805)
                }

                create_account_url = "https://discord.com/api/v9/auth/register"
                response = requests.post(create_account_url, json=payload, headers=headers, proxies={"http": self.proxy, "https": self.proxy})

                if response.status_code == 201:
                    # Successfully created the account, extract token from the response
                    self.token = response.json().get("token")
                    if self.token:
                        Log.amazing(f"Account created successfully with token: {self.token[:10]}...")
                    else:
                        Log.bad("Account created, but no token received.")
                else:
                    Log.bad(f"Account creation failed: {response.status_code} - {response.text}")
            else:
                Log.warn("Failed to solve captcha. Retrying...")
        except Exception as e:
            Log.bad(f"Error in Discord.create_account: {e}")


# Main Execution
if __name__ == "__main__":
    try:
        UI.show()
        api_key = UI.get_api_key()
        config = {
            "captcha_api_key": api_key,
            "password": "dummy_password12345tg",
        }
        proxies = ["http://prismboosts:SantaProxy_Streaming-1@geo.iproyal.com:12321"]

        discord = Discord(config, proxies)
        discord.begin()
    except Exception as e:
        Log.bad(f"Unhandled exception in main: {e}")
