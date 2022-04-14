import asyncio
from functools import wraps

import click

from chatamcat.client import Client
from chatamcat.server import Server


def coro_wrap(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        asyncio.run(func(*args, **kwargs))

    return wrapper


@click.group()
def cli():
    pass


@click.command()
@click.option("-h", "--host", required=True, type=str, help="Server host")
@click.option("-p", "--port", required=True, type=int, help="Server port")
@coro_wrap
async def server(host, port):
    server = Server(host, port)

    await server.start()


@click.command()
@click.option("-u", "--username", required=True, type=str, help="Username")
@click.option("-h", "--host", required=True, type=str, help="Server host")
@click.option("-p", "--port", required=True, type=int, help="Server port")
@coro_wrap
async def client(username, host, port):
    client = Client(username, host, port)
    await client.connect()

    await client.chat_menu()


cli.add_command(server)
cli.add_command(client)

if __name__ == "__main__":
    cli()
