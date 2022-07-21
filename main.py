import discord
import aiohttp
import toml

from discord.ext import commands

import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

with open("config.toml", "r", encoding="UTF-8") as cfile:
    config = toml.load(cfile)


class UltimateHackingBot(commands.Bot):
    def __init__(self, config, description, intents):
        super().__init__(
            command_prefix=config["bot"]["prefix"], description=description, intents=intents
        )

        self.config = config
        self.synced = False
        self.initial_extensions = ["cogs.cryptography", "cogs.research"]

        logger.info("Bot object initialised")

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        for ext in self.initial_extensions:
            try:
                await self.load_extension(ext)
                logger.info(f"Loaded cog: {ext}")
            except Exception as error:
                logger.error(f"Could not load cog: {ext} | {error}")

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_ready(self):
        await self.wait_until_ready()

        if not bot.synced:
            await bot.tree.sync()
        bot.synced = True

        logger.info(f"Running as {bot.user} (ID: {bot.user.id})")


description = config["bot"]["description"]

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = UltimateHackingBot(
    config=config, intents=intents, description=description
)


@bot.command()
async def sync(ctx):
    if not bot.synced:
        await bot.tree.sync()
        bot.synced = True
    await ctx.send("We are up to date!")


if __name__ == "__main__":
    with open(".env", "r") as file:
        token = file.read()

    logger.info("Attempting to start")
    bot.run(token)
