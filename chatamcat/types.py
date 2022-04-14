from asyncio import StreamReader, StreamWriter


class ChatClient(object):
    def __init__(
        self,
        username: str,
        reader: StreamReader,
        writer: StreamWriter,
    ):
        self.username = username
        self.reader = reader
        self.writer = writer
        self.adress = ":".join(str(v) for v in writer.get_extra_info("peername"))

    def __str__(self) -> str:
        return f"[User: {self.username} :: {self.adress}]"


class ClientMessage(object):
    def __init__(self, sender: str, recipient: str, text: str) -> None:
        self.sender = sender
        self.recipient = recipient
        self.text = text

    def __str__(self) -> str:
        return f"[FROM: {self.sender}]: {self.text}"
