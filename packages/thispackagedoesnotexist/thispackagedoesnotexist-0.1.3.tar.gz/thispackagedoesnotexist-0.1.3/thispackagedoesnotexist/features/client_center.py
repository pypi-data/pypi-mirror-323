from ..plugins.client import ClientControl

def ClientCenter(data, client, converter):
    try:
        command = data["client"]

        if command not in ["restart", "shutdown", "update", "uninstall"]:
            client.send_message(converter.encode({"client_logger": f"From Client: {command} not recognized"}))
            return
        
        client.send_message(converter.encode({"client": f"From Client: {command} executed"}))

        if command == "restart":
            ClientControl.restart_self()
        elif command == "shutdown":
            ClientControl.shutdown_self()
        elif command == "update":
            ClientControl.update_self()
        elif command == "uninstall":
            ClientControl.uninstall_self()

    except Exception as e:
        client.send_message(converter.encode({"client_logger": str(e)}))
