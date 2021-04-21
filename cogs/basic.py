from discord.ext import commands
from random import choices
from config import emotes, users, dialogue

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description='ree')
    async def hello(self, ctx):
        await ctx.send('henlo')

    @commands.command(description='Choose between any number of options, separated by /. Usage: !choose [choice 1]/[choice 2]/[choice 3]')
    async def choose(self, ctx, *args):
        split_args = ' '.join(args).split('/')
        await ctx.send(choices(split_args)[0])
    
    @commands.command(description='kek')
    async def ping(self, ctx):
        await ctx.send(f"{users['kaina']} {emotes['kree']}")

    @commands.command(description='kek')
    async def pong(self, ctx):
        await ctx.send(f"{users['fy']} {emotes['kree']}")

    @commands.command()
    async def melt(self, ctx):
        await ctx.send(choices(dialogue)[0])

def setup(bot):
    bot.add_cog(Basic(bot))