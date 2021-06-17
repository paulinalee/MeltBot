from discord.ext import commands
from random import choices
from config import emotes, users, dialogue
import re
from replit import db
from sqlitedict import SqliteDict

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description="Basic, simple bot commands."
        self.db = SqliteDict('./prefix.sqlite', autocommit=True)

    @commands.command(help="Health check function.")
    async def hello(self, ctx):
        await ctx.send('henlo')
    
    @commands.command(help=':kek')
    async def ping(self, ctx):
        if not self.in_server(ctx, users['kaina']):
            return await ctx.send("Sorry! This command is only available in specific servers.")
        await ctx.send(f"{users['kaina']} {emotes['kree']}")

    @commands.command(help='you:')
    async def pong(self, ctx):
        if not self.in_server(ctx, users['fy']):
            return await ctx.send("Sorry! This command is only available in specific servers.")
        await ctx.send(f"{users['fy']} {emotes['kree']}")
    
    @commands.command(help=':paissayay:', aliases=['hbd'])
    async def cake(self, ctx):
        if not self.in_server(ctx, users['dog']):
            return await ctx.send("Sorry! This command is only available in specific servers.")
        await ctx.send(f"{users['dog']} HAPPY BIRTHDAY {emotes['paissayay']}")

    @commands.command(help=':paissadab:')
    async def dab(self, ctx):
        await ctx.send(emotes['paissadab'])

    def in_server(self, ctx, ping_str):
        id = int(re.search(r'\d+', ping_str).group())
        return ctx.guild.get_member(id) != None

    @commands.command(help='Bootleg FGO My Room experience.')
    async def talk(self, ctx):
        await ctx.send(choices(dialogue)[0])

    @commands.command(aliases=['cmds', 'h'], help='View list of available commands.')
    async def commandlist(self, ctx, *args):
        await ctx.send_help(*args)

    @commands.command(help='Change the bot prefix for this server.')
    async def prefix(self, ctx, new_prefix: str):
        server = str(ctx.guild.id)
        db['prefix'][server] = new_prefix
        await ctx.send(f"Prefix changed to `{new_prefix}`!")

def setup(bot):
    bot.add_cog(Basic(bot))