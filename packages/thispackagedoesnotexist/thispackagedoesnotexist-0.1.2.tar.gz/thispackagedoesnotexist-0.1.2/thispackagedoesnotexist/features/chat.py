import customtkinter as ctk
import tkinter as tk
from tkinter import END
import json
import os
import threading
import time

class ChatBotApp:
    def __init__(self, root, data, client, converter, shared):
        self.root = root
        self.root.title("Chat")
        self.root.geometry("500x600")
        self.root.attributes("-topmost", True) 
        self.client = client
        self.converter = converter
        self.data = data
        self.shared = shared

        self.chat_display = tk.Text(self.root, width=480, height=25, wrap="word", state="disabled", font=("Helvetica", 30))
        self.chat_display.pack(pady=10)

        self.user_input = ctk.CTkTextbox(self.root, width=400, height=90, wrap="word")
        self.user_input.pack(pady=5)

        self.send_button = ctk.CTkButton(self.root, text="Send", command=self.handle_message)
        self.send_button.pack(pady=5)

        self.conversation_log = []
        self.json_file = "conversation_log.json"
        self.load_existing_log()
        self.display_previous_convo()
        
        threading.Thread(target=self.receive_message, daemon=True).start()

    def load_existing_log(self):
        if os.path.exists(self.json_file):
            with open(self.json_file, "r", encoding="utf-8") as file:
                self.conversation_log = json.load(file)

    def display_previous_convo(self):
        for entry in self.conversation_log:
            for sender, message in entry.items():
                self.display_message(sender, message)

    def handle_message(self):
        user_message = self.user_input.get("1.0", END).strip()
        if not user_message:
            return

        self.display_message("User 2", user_message)
        self.update_convo("User 2", user_message)
        self.user_input.delete("1.0", END)

        self.client.send_message(self.converter.encode({"chat_messages": user_message}))

    def update_convo(self, sender, message):
        self.conversation_log.append({sender: message})
        with open(self.json_file, "w", encoding="utf-8") as file:
            json.dump(self.conversation_log, file, indent=4)

    def display_message(self, sender, message):
        self.chat_display.configure(state="normal")
        if sender == "User 1":
            self.chat_display.insert(END, f"{sender}: ", "user1")
        else:
            self.chat_display.insert(END, f"{sender}: ", "user2")

        self.chat_display.insert(END, f"{message}\n")
        self.chat_display.see(END)
        self.chat_display.configure(state="disabled")

        self.chat_display.tag_configure("user1", foreground="red")
        self.chat_display.tag_configure("user2", foreground="blue")

    def receive_message(self):
        chat_online = self.shared.get_data("chat_online")
        while chat_online:
            chat_messages = self.shared.get_data("chat_messages")
            if chat_messages:
                self.display_message("User 1", chat_messages)
                self.update_convo("User 1", chat_messages)
            chat_online = self.shared.get_data("chat_online")
            time.sleep(1)

def chat(data, client, converter, shared):
    root = ctk.CTk()
    app = ChatBotApp(root, data, client, converter, shared)
    root.mainloop()
