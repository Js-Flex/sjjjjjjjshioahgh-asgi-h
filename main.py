import requests
import random
import string
import time
import json
import platform
import os
import colorama
import shutil
from datetime import datetime
from queue import Queue
from typing import Optional
import base64


# Utility Functions
class Utils:
    @staticmethod
    def random_username(length: int = 8) -> str:
        """Generate a random username with letters only."""
        return ''.join(random.choices(string.ascii_letters, k=length))

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
                task_id = response_data.get('task_id')
                Log.amazing(f"Captcha task created successfully. Task ID: {task_id}")

                # Wait 10 seconds before checking the captcha solving result
                Log.info(f"Waiting 10 seconds for captcha solution...")
                time.sleep(10)

                # Now check the status of the captcha solving task
                status_response = requests.get(f"https://api.razorcap.xyz/get_task?task_id={task_id}")
                status_data = status_response.json()

                if status_data.get('status') == 'solved':
                    captcha_solution = status_data.get('solution')
                    Log.amazing(f"Captcha solved: {captcha_solution[:10]}...")
                    return captcha_solution
                elif status_data.get('status') == 'failed':
                    Log.bad(f"Captcha solving failed: {status_data}")
                    return None
            else:
                Log.bad(f"Captcha solving task creation failed: {response_data}")
                return None
        except Exception as e:
            Log.bad(f"Error solving captcha with RazorCap: {e}")
            return None


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


# Discord Account Creation
class Discord:
    def __init__(self, config, proxies):
        try:
            self.config = config
            self.proxies = proxies
            self.proxy_queue = Queue()
            for proxy in proxies:
                self.proxy_queue.put(proxy)
            self.username = Utils.random_username(random.randint(6, 12))
            self.email = f"{self.username}@gmail.com"
            self.password = config.get('password', 'default_password')
            self.token = None
            Log.good(f"Initialized Discord object with proxy: {self.proxy_queue.queue[0]}, username: {self.username}")
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
            captcha_solution = None
            retries = 0

            while True:  # Infinite retry loop
                proxy = self.proxy_queue.get()
                captcha_solution = Captcha.solve(
                    api_key=self.config['captcha_api_key'],
                    sitekey="4c672d35-0701-42b2-88c3-78380b0db560",  # Discord's sitekey
                    siteurl="https://discord.com",
                    proxy=proxy
                )

                if captcha_solution:
                    Log.amazing(f"Captcha solved: {captcha_solution[:10]}...")
                    account_data = {
                        "email": self.email,
                        "username": self.username,
                        "password": self.password,
                        "captcha_key": captcha_solution,  # The captcha solution from RazorCap
                        "invite": None,
                        "gift_code_sku_id": None,
                        "date_of_birth": "2000-01-01",  # Make sure to set a valid birthdate
                        "consent": True,
                        "platform": "web"
                    }

                    # Register account
                    registration_url = "https://discord.com/api/v9/auth/register"
                    headers = {
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    }
                    response = requests.post(registration_url, json=account_data, headers=headers, proxies={"http": proxy, "https": proxy})

                    if response.status_code == 201:  # Success
                        self.token = response.json().get('token')
                        Log.amazing(f"Account created successfully with token: {self.token[:10]}...")
                        break  # Break out of the loop if account creation is successful
                    else:
                        retries += 1
                        self.proxy_queue.put(proxy)  # Re-add proxy to the queue for the next try
                        Log.warn(f"Failed to create account. Retrying... {retries}")
                        time.sleep(3)  # Add a delay between retries

            # If captcha solution failed, retry the process
            else:
                Log.bad(f"Failed to get valid captcha solution. Retrying...")
                time.sleep(3)  # Retry after a short delay

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
