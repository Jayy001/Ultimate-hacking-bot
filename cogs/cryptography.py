import requests
import json
import os

import logging

import discord

from discord.ext import commands
from discord.ui import Button, View, Select, Modal
from discord import app_commands

from search_that_hash import api as sth_api
from name_that_hash.runner import api_return_hashes_as_json as nth_api

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)


class Handler:
    def __init__(self, config):
        self.config = config

        try:
            pass
        except Exception as error:
            logger.exception(error)

    def ciphey(self, ctext):
        responses = {
            '{"message": "Internal server error"}': "Took too long to decrypt",
            '"Failed to crack"': "Could not decrypt the text",
        }
        response = requests.get(self.config["apis"]["ciphey"] + ctext).text.strip('"')

        if response in responses:
            return False, responses[response]

        return True, response

    @staticmethod
    def search_that_hash(ctext):
        response = sth_api.return_as_fast_json([ctext])[0][
            ctext
        ]  # Returns a list, so we want the first result

        if response == "Could not crack hash":
            return False, response

        if type(response) == list:
            return (
                False,
                "I could not find any cracking services matching this hash type",
            )

        return True, response["plaintext"], response["types"], response["verified"]

    @staticmethod
    def identify(ctext):
        matches = ""

        hashes = json.loads(nth_api([ctext]))
        htype: str
        for htype in hashes[ctext]:
            matches += htype + "\n"

        identifiers = json.loads(os.popen("lemmeknow.exe --json " + ctext).read())
        wtype: dict
        for wtype in identifiers:
            matches += wtype["data"]["Name"] + "\n"

        if matches:
            return True, matches
        return False, "Could not identify this text"


class Cryptography(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.handler = Handler(self.bot.config)

    @app_commands.command(name="ciphey")
    async def ciphey(self, interaction: discord.Interaction, ctext: str) -> None:
        await interaction.response.send_message(
            self.handler.ciphey(ctext),
            ephemeral=self.bot.config["bot"]["hidden_replies"],
        )

    @app_commands.command(name="crack")
    async def crack(self, interaction: discord.Interaction, ctext: str) -> None:
        await interaction.response.send_message(
            self.handler.search_that_hash(ctext),
            ephemeral=self.bot.config["bot"]["hidden_replies"],
        )

    @app_commands.command(name="identify")
    async def identify(self, interaction: discord.Interaction, ctext: str) -> None:
        await interaction.response.send_message(
            self.handler.identify(ctext),
            ephemeral=self.bot.config["bot"]["hidden_replies"],
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Cryptography(bot))
