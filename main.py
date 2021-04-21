import discord
import os
import config
from discord.ext.commands import Bot

class MeltBot(Bot):
  def __init__(self):
      super().__init__(command_prefix='!', description='henlo this is a bot')


  async def on_ready(self):
      print('We have logged in as {0.user}'.format(self))
      for cog in config.cogs:
        self.load_extension(cog)

bot = MeltBot()

bot.run(os.environ['TOKEN']);