import discord
from discord.ext import commands

class Fight(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def fight(self, ctx, target: discord.User):
        request = await ctx.send(f"{target.mention}, you have been challenged to a fight! Do you accept?")
        request.add_reaction('🇾')

    @fight.error
    async def fight_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Couldn't find that user...")

def setup(bot):
    bot.add_cog(Fight(bot))