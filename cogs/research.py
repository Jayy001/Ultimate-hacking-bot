# https://raw.githubusercontent.com/GTFOBins/GTFOBins.github.io/master/_gtfobins/alpine.md

import requests
import json
import os

import logging

import discord

from discord.ext import commands
from discord.ui import Button, View, Select, Modal
from discord import app_commands

from tldr import get_page
from data.revshells import shells
from difflib import get_close_matches as search

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)


class Handler:
    def __init__(self, config):
        self.config = config
        self.shell_names = [shell["name"] for shell in shells]

        try:
            pass
        except Exception as error:
            logger.exception(error)

    @staticmethod
    def binaries(ctext):
        ctext = ctext.lower()

        unix = requests.get(
            f"https://raw.githubusercontent.com/GTFOBins/GTFOBins.github.io/master/_gtfobins/{ctext}.md")
        if unix:
            return True, unix.text

        windows = requests.get(
            f"https://raw.githubusercontent.com/LOLBAS-Project/LOLBAS/master/yml/OSBinaries/{ctext}.yml")
        if windows:
            return True, windows.text

        return False, "Not a valid binary name"

    @staticmethod
    def tldr(ctext):
        result = get_page(ctext, "https://raw.githubusercontent.com/tldr-pages/tldr/master/pages", None, None)

        if result:
            return True, result
        return False, "Could not find any documentation for this command"

    def revshells(self, ctext):
        results = search(ctext, self.shell_names)
        matches = ""

        if results:
            for shell_name in results:
                for shell_dict in shells:
                    if shell_dict["name"] == shell_name:
                        matches += f"{shell_name}: {shell_dict['command']}"
            return True, matches
        return False, "Could not find any documentation for this command"


class Research(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.handler = Handler(self.bot.config)

    @app_commands.command(name="binaries")
    async def binaries(self, interaction: discord.Interaction, ctext: str) -> None:
        await interaction.response.send_message(
            self.handler.binaries(ctext),
            ephemeral=self.bot.config["bot"]["hidden_replies"],
        )

    @app_commands.command(name="tldr")
    async def tldr(self, interaction: discord.Interaction, ctext: str) -> None:
        await interaction.response.send_message(
            self.handler.tldr(ctext),
            ephemeral=self.bot.config["bot"]["hidden_replies"],
        )

    @app_commands.command(name="revshells")
    async def revshells(self, interaction: discord.Interaction, ctext: str) -> None:
        await interaction.response.send_message(
            self.handler.revshells(ctext),
            ephemeral=self.bot.config["bot"]["hidden_replies"],
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Research(bot))
