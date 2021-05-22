from discord.ext import commands
from owotext import OwO

class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description="Random other utilities"
    
    @commands.command(help="what's this")
    async def owo(self, ctx, *args):
        text = ' '.join(args)
        owo = OwO()
        await ctx.send(owo.whatsthis(text))

def setup(bot):
    bot.add_cog(Misc(bot))