import os
import config
from discord.ext.commands import Bot
from pretty_help import PrettyHelp

class MeltBot(Bot):
  def __init__(self):
      super().__init__(command_prefix='!', description="Your favorite Alter Ego, now as a bot. [under development]", help_command=PrettyHelp())


  async def on_ready(self):
      print('Logged in as {0.user}'.format(self))
      for cog in config.cogs:
        self.load_extension(cog)

bot = MeltBot()

bot.run(os.environ['TOKEN']);