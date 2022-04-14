from setuptools import find_packages, setup

setup(
    name="chatamcat",
    version="0.0.1",
    description="chatamcat - Simple asynchronous chat using asyncio.",
    author="David Woo",
    author_email="wujiocean@protonmail.com",
    packages=find_packages(exclude=("tests",)),
    install_requires=[
        "aioconsole",
        "click",
    ],
    entry_points={
        "console_scripts": [
            "chatamcat = chatamcat.cli:cli",
        ]
    },
)
