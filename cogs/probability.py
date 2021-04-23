from discord.ext import commands
from random import choices
from config import emotes

class Probability(commands.Cog):
    ASK_RESPONSES = [
        'Most likely.',
        'Absolutely not!',
        "I don't think so.",
        'Hmm...',
        'Definitely not.',
        'Extremely so.',
        'As I see it, yes.',
        'Without a doubt.',
        'Very doubtful.'
    ]

    def __init__(self, bot):
        self.bot = bot
        self.description="Gambling but not really but also kind of..."

    @commands.command(help='Choose between any number of options, separated by slashes (/).', aliases=['decide'])
    async def choose(self, ctx, *args):
        split_args = ' '.join(args).split('/')
        await ctx.send(choices(split_args)[0])
    
    @commands.command(help='Ask a yes/no question.', aliases=['8ball'])
    async def ask(self, ctx, *args):
        await ctx.send(choices(self.ASK_RESPONSES)[0])

def setup(bot):
    bot.add_cog(Probability(bot))