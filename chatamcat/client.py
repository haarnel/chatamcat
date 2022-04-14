import asyncio
import json
import sys
import typing as t
from asyncio import StreamReader, StreamWriter

import aioconsole

from chatamcat.types import ClientMessage


class Client(object):
    def __init__(self, username: str, host: str, port: int) -> None:
        self.username = username
        self.host = host
        self.port = port
        self._reader: t.Optional[StreamReader] = None
        self._writer: t.Optional[StreamWriter] = None
        self._messages: t.List[ClientMessage] = []

    async def connect(self):
        self._reader, self._writer = await asyncio.open_connection(self.host, self.port)
        payload = {"command": "connect", "username": self.username}
        payload = json.dumps(payload) + "\n"
        self._writer.write(payload.encode())
        await self._writer.drain()
        response = await self._reader.readline()
        response = json.loads(response)
        status = response["status"]
        if status == "success":
            print(response["msg"])
            asyncio.create_task(self._listen_messages())

        elif status == "error":
            print(response["reason"])
            self._writer.close()
            await self._writer.wait_closed()
            sys.exit(0)

    async def chat_menu(self):
        menu = {
            1: "Show Messages",
            2: "Send Message",
            3: "Quit",
        }
        print()
        for n, item in menu.items():
            print(f"{n}. {item}")
        print()
        user_choice = await aioconsole.ainput("Choice: ")
        user_choice = int(user_choice)
        if user_choice == 1:
            await self.show_messages()
        elif user_choice == 2:
            print()
            recipient = await aioconsole.ainput("Recipient: ")
            text = await aioconsole.ainput("Text: ")
            print()
            await self.send_message(recipient, text)
        elif user_choice == 3:
            await self.disconnect()

    async def _listen_messages(self):
        while True:
            data = await self._reader.readline()
            if data == b"":
                break

            data: dict = json.loads(data)
            mtype = data.get("type")
            if mtype == "message":
                message = ClientMessage(**data.get("data"))
                self._messages.append(message)
            elif mtype == "info":
                print(data["text"])

    async def show_messages(self):
        table = {}
        print()
        for idx, message in enumerate(self._messages, 1):
            table[idx] = message
            print(f"{idx}. {message}")
        print()
        user_choice = await aioconsole.ainput("Replay (y/n/r): ")
        if user_choice == "y":
            user_choice = await aioconsole.ainput("replay to (number): ")
            message = table[int(user_choice)]
            text = await aioconsole.ainput("Text: ")
            await self.send_message(message.sender, text)
        elif user_choice == "n":
            await self.chat_menu()
        elif user_choice == "r":
            await self.show_messages()

    async def send_message(self, recipient: str, text: str):
        payload = {
            "command": "send_message",
            "data": {"sender": self.username, "recipient": recipient, "text": text},
        }
        payload = json.dumps(payload)
        self._writer.write(payload.encode() + b"\n")
        await asyncio.sleep(0.2)
        await self.chat_menu()

    async def disconnect(self):
        payload = {"command": "quit"}
        payload = json.dumps(payload) + "\n"
        self._writer.write(payload.encode())
        await self._writer.drain()
        print(f"Goodbye, {self.username}!")
        sys.exit(0)
