import discord
from config import poll_reacts, poll_options, emotes
from discord.ext import commands

class Interactive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(description="Create a poll with up to 10 options. Usage: !vote [title] [choice 1]/[choice2]/[choice 3]")
    async def vote(self, ctx, title, *args):
        split_args = ' '.join(args).split('/')
        if (len(split_args) > 10):
            return await ctx.send('Sorry, polls only support up to 10 options! Please try again.')
        poll_content = ''
        max_iters = min(len(split_args), 10)
        for i in range(max_iters):
            poll_content += f"{poll_options[i]} {split_args[i]}"
            if (i != max_iters - 1):
                poll_content += '\n'
        embed = discord.Embed(title=title, description=poll_content)
        message = await ctx.send(embed=embed)
        for i in range(max_iters):
            await message.add_reaction(emoji=poll_reacts[i])
    
    @vote.error
    async def vote_error(self, ctx, error):
        await ctx.send(f"Stop breaking the bot ree {emotes['kree']}")

def setup(bot):
    bot.add_cog(Interactive(bot))