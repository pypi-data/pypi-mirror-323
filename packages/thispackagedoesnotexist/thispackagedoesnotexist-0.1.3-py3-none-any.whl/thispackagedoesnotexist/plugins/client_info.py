import platform
import requests
from wmi import WMI
import winreg
import ctypes

class ClientInfo:
    def __init__(self):
        self.ip = None
        self.country = None
        self.pc_name = platform.node()
        self.pc_id = WMI().Win32_ComputerSystemProduct()[0].UUID
        self.os = self.get_win_ver()
        self.account_type = self.check_account_type()
        self.fetch_client_info()

    def get_win_ver(self):
        system_info = platform.system()
        architecture = platform.architecture()[0]
        if system_info == "Windows":
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                    edition = winreg.QueryValueEx(key, "ProductName")[0]
                    version = winreg.QueryValueEx(key, "ReleaseId")[0]
                return f"{edition} {version} {architecture}"
            except Exception:
                return "Error retrieving Windows edition"
        return "Not a Windows system"

    def check_account_type(self):
        try:
            if ctypes.windll.shell32.IsUserAnAdmin() != 0:
                return "Admin"
            else:
                return "User"
        except Exception:
            return "None"

    def fetch_client_info(self):
        try:
            url = "https://api.my-ip.io/v2/ip.json"
            response = requests.get(url)
            print(response.text)
            if response.status_code == 200:
                data = response.json()
                self.ip = data.get("ip")
                self.country = data.get("country", {}).get("name")
        except:
            self.ip = None
            self.country = None

    def get_details(self):
        return {
            "IP": self.ip,
            "PC Name": self.pc_name,
            "PC ID": self.pc_id,
            "OS": self.os,
            "Account Type": self.account_type,
            "Country": self.country,
        }
