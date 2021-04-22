from discord.ext import commands
from random import choices
from config import emotes, users, dialogue

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description="Basic, simple bot commands."

    @commands.command(help="Health check function.")
    async def hello(self, ctx):
        await ctx.send('henlo')

    @commands.command(help='Choose between any number of options, separated by /.')
    async def choose(self, ctx, *args):
        split_args = ' '.join(args).split('/')
        await ctx.send(choices(split_args)[0])
    
    @commands.command(help='Pings Kaina')
    async def ping(self, ctx):
        await ctx.send(f"{users['kaina']} {emotes['kree']}")

    @commands.command(help='Pings spoof')
    async def pong(self, ctx):
        await ctx.send(f"{users['fy']} {emotes['kree']}")

    @commands.command(help='Get a Melt voice line.')
    async def talk(self, ctx):
        await ctx.send(choices(dialogue)[0])

    @commands.command(aliases=['commandlist', 'h'], help='View list of available commands.')
    async def commands(self, ctx, *args):
        await ctx.send_help(*args)

def setup(bot):
    bot.add_cog(Basic(bot))