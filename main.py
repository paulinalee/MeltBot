import os
import config
import discord
from discord.ext.commands import Bot
from pretty_help import PrettyHelp
from replit import db
import urllib3
from sqlitedict import SqliteDict

class MeltBot(Bot):
    DEFAULT_PREFIX = '!'
    
    def __init__(self):
        urllib3.disable_warnings()
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix=self.determine_prefix, description="Your favorite Alter Ego, now as a bot. [under development]",
                help_command=PrettyHelp(), intents=intents, case_insensitive=True)

        if 'reminders' not in db:
            db['reminders'] = {}
        self.prefix_db = SqliteDict('./prefix.sqlite', autocommit=True)
   
    def determine_prefix(self, bot, message):
        server = str(message.guild.id)
        return self.prefix_helper(server)
    
    def ctx_prefix(self, ctx):
        # basically the same as above but using ctx instead of message to grab the server id
        server = str(ctx.guild.id)
        return self.prefix_helper(server)

    def prefix_helper(self, server):
        if server in self.prefix_db:
            return self.prefix_db[server]
        else:
            return self.DEFAULT_PREFIX

    async def on_ready(self):
        print('Logged in as {0.user}'.format(self))
        for cog in config.cogs:
            self.load_extension(cog)

bot = MeltBot()

bot.run(os.environ['TOKEN']);