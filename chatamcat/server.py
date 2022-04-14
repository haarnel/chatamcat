import asyncio
import json
import typing as t
from asyncio import StreamReader, StreamWriter

from chatamcat.logger import getLogger
from chatamcat.types import ChatClient, ClientMessage


class Server(object):
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

        self._online = 0
        self._clients: t.Dict[str, ChatClient] = {}
        self._lock = asyncio.Lock()
        self._logger = getLogger()
        self._mq = asyncio.Queue()

    async def start(self):

        server = await asyncio.start_server(self.connect_client, self.host, self.port)

        async with server:
            asyncio.create_task(self._message_sender())
            await server.serve_forever()

    async def connect_client(self, reader: StreamReader, writer: StreamWriter):
        data = await reader.readline()
        request: dict = json.loads(data)
        if request.get("command") == "connect":
            username = request["username"]
            added = await self.add_client(username, reader, writer)
            if added:
                self._logger.info(msg=f"[CONNECTED] {self._clients[username]}")
                message = f"Welcome, {username}! Server online: {self._online}"
                response = {"status": "success", "msg": message}

            else:
                response = {
                    "status": "error",
                    "reason": f"User ({username}) already exists. Please choose another one!",
                }

            response = json.dumps(response)
            writer.write(response.encode() + b"\n")
            await writer.drain()
            if not added:
                writer.close()
                await writer.wait_closed()
            else:
                asyncio.create_task(self._listen_client(username))

    async def add_client(
        self,
        username: str,
        reader: StreamReader,
        writer: StreamWriter,
    ) -> bool:
        user = self._clients.get(username)
        if user is not None:
            return False
        else:
            async with self._lock:
                client = ChatClient(username, reader, writer)
                self._clients[username] = client
                self._online += 1
                return True

    async def _listen_client(self, username: str):
        while True:
            client = self._clients[username]
            if client is None:
                break

            client_data = await client.reader.readline()
            if client_data == b"":
                await self._disconnect_client(username)
                break

            request: dict = json.loads(client_data)
            command = request.get("command")
            if command == "send_message":
                message = ClientMessage(**request["data"])
                await self._mq.put(message)
            elif command == "quit":
                client.writer.close()
                await client.writer.wait_closed()

    async def _disconnect_client(self, username: str):
        user = self._clients.get(username)
        if user is not None:
            user.writer.close()
            await user.writer.wait_closed()

            async with self._lock:
                del self._clients[username]
                self._online -= 1

            self._logger.info(msg=f"[DISCONNECTED] {user}")

    async def _message_sender(self, timeout: float = 0.1):
        while True:
            message: ClientMessage = await self._mq.get()
            if message is not None:
                sender = self._clients.get(message.sender)
                recipient = self._clients.get(message.recipient)
                delivered = False
                if sender and recipient:
                    response = {
                        "type": "message",
                        "data": {
                            "sender": message.sender,
                            "recipient": message.recipient,
                            "text": message.text,
                        },
                    }
                    response = json.dumps(response) + "\n"
                    recipient.writer.write(response.encode())
                    await recipient.writer.drain()
                    delivered = True
                else:
                    response = {
                        "type": "info",
                        f"text": f"[INFO]: Message wasn't delivered to {message.recipient}",
                    }
                    delivered = False

                if delivered:
                    log_msg = f"[OK][MESSAGE]: [FROM: {message.sender}] -> [TO: {message.recipient}] [TEXT: {message.text}]"
                    confirm_resp = {
                        "type": "info",
                        f"text": f"[STATUS]: Message was successfully delivered to {message.recipient}",
                    }
                else:
                    confirm_resp = {
                        "type": "info",
                        f"text": f"[STATUS]: Message wasn't delivered to {message.recipient}",
                    }
                    log_msg = f"[FAIL][MESSAGE]: [FROM: {message.sender}] -> [TO: {message.recipient}] [TEXT: {message.text}]"

                confirm_resp = json.dumps(confirm_resp) + "\n"
                sender.writer.write(confirm_resp.encode())
                await sender.writer.drain()
                self._logger.info(log_msg)

            await asyncio.sleep(timeout)
