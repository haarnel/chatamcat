# Chatamcat

**Study/Pet Project**. Simple asynchronous chat using asyncio.

## Main Features

- Supports multiple clients
- Delivery notification system
- Simple cli mode

## Requirements

- click
- aioconsole

## Installation

```sh
git clone https://github.com/wujiocean/chatamcat
cd chatamcat
python -m venv .env && source .env/bin/activate
pip install .
```

## Usage

1. Run server

```sh
chatamcat server -h "127.0.0.1" -p 32000
```

2. Connecting clients to the server

```sh
chatamcat client -u "anna" -h "127.0.0.1" -p 32000
chatamcat client -u "jonny" -h "127.0.0.1" -p 32000
chatamcat client -u "andrew" -h "127.0.0.1" -p 32000
....
```

3. Chatting

## TODO

- [ ] Better error handling.
- [ ] Tests.
- [ ] TUI support.
