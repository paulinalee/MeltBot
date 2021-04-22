import discord
from config import poll_reacts, poll_option_labels, emotes
from discord.ext import commands
from asyncio import sleep
import typing

class Interactive(commands.Cog):
    POLL_INSTRUCTIONS = "To vote, react to the option you want to vote for before the poll expires. You can vote for multiple options for this type of poll."
    def __init__(self, bot):
        self.bot = bot
        self.description="Functions that rely a lot on user input, but aren't exactly games."

    @commands.command(help="Create a poll and get notified via mention once the poll ends. For more info on polls, try !help vote.", aliases=['pollnotify', 'vn'])
    async def votenotify(self, ctx, title, duration: typing.Optional[int]=20, *args):
        await self.vote(ctx, title, duration, True, *args)

    @commands.command(help="Create a poll with up to 10 options and an optional poll duration. If duration is not specified, it will be 20 seconds by default. The creator of the poll can also request to be notified via mention once the poll concludes.", aliases=['poll', 'v'])
    async def vote(self, ctx, title, duration: typing.Optional[int]=20, notify: typing.Optional[bool]=False, *args):
        poll_options = ' '.join(args).split('/')
        if len(poll_options) > 10:
            return await ctx.send('Sorry, polls only support up to 10 options! Please try again.')

        poll_content = ''
        max_iters = min(len(poll_options), 10)
        for i in range(max_iters):
            poll_content += f"{poll_option_labels[i]} {poll_options[i]}"
            if (i != max_iters - 1):
                poll_content += '\n'
        
        embed = discord.Embed(title=f"Poll: {title}", description=f"{self.POLL_INSTRUCTIONS}\n\n{poll_content}")
        embed.add_field(name='Creator', value=ctx.author.name, inline=True)
        embed.add_field(name='Duration', value=f"{duration}s", inline=True)
        embed.add_field(name='Notify?', value=f"{'On' if notify else 'Off'}", inline=True)
        message = await ctx.send(embed=embed)
        
        # set up voting and wait until poll closes
        for i in range(max_iters):
            await message.add_reaction(emoji=poll_reacts[i])
        await sleep(duration)
        message = await ctx.fetch_message(message.id)

        poll_close_embed = message.embeds[0]
        poll_close_embed.title = f"[CLOSED] Poll: {title}"
        await message.edit(embed=poll_close_embed)
        print('done')

        # find winning option
        max_count = 0
        max_index = None
        winning_options = []
        for i in range(len(message.reactions)):
            curr_count = message.reactions[i].count - 1 # subtract the bot's own react
            if (curr_count > max_count):
                max_count = curr_count
                max_index = i
                winning_options = [poll_options[i]]
            elif (curr_count == max_count):
                winning_options.append(poll_options[i])
        
        if max_index == None:
            return await ctx.send("It looks like there were no votes on this poll, so I can't determine a winning choice.")
        
        closing_blurb = f"The poll {title} has closed."
        result_msg = ''
        if (notify):
            result_msg += f"{ctx.author.mention}, your poll {title} has ended!"
        else:
            result_msg += closing_blurb

        if (len(winning_options) == 1):
            result_msg += f"\nThe winning option is: {winning_options[0]}!"
        else:
            result_msg += f"\nThere appears to be a tie, the winning poll_options are: {', '.join(winning_options)}!"

        await ctx.send(result_msg)


    @vote.error
    async def vote_error(self, ctx, error):
        if isinstance(error, commands.BadArgument) or isinstance(error, commands.InvalidEndOfQuotedStringError):
            await ctx.send(f"Stop breaking the bot ree {emotes['kree']}")

def setup(bot):
    bot.add_cog(Interactive(bot))