import os

def power(data, client, converter):
    try:
        command = data["power"]

        if command not in ["restart", "shutdown", "lock"]:
            client.send_message(converter.encode({"power_logger": f"From Client: {command} not recognized"}))
            return
        
        client.send_message(converter.encode({"power": f"From Client: {command} executed"}))

        if command == "restart":
            os.system("shutdown /r /t 0")
        elif command == "shutdown":
            os.system("shutdown /s /t 0")
        elif command == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")

    except Exception as e:
        client.send_message(converter.encode({"power_logger": str(e)}))
