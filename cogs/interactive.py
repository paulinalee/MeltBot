import discord
from config import poll_reacts, poll_option_labels, emotes
from discord.ext import commands
import asyncio
import typing

class Interactive(commands.Cog):
    POLL_INSTRUCTIONS = "To vote, react to the option you want to vote for before the poll expires. You can vote for multiple options for this type of poll. The creator can close the poll at any time before the duration is up by reacting with ✅"
    def __init__(self, bot):
        self.bot = bot
        self.description="Functions that rely a lot on user input, but aren't exactly games."

    @commands.command(help=f"Create a poll and get notified via mention once the poll ends. For more info on polls, see vote.", aliases=['pollnotify', 'vn'])
    async def votenotify(self, ctx, title, duration: typing.Optional[int]=20, *args):
        await self.run_poll(ctx, title, duration, True, *args)

    @commands.command(help="Create a poll with up to 10 options and an optional poll duration (20 seconds by default). Poll options should be separated by slashes (/). Use the votenotify or vn commands instead if you want to be notified via mention once the poll ends.", aliases=['poll', 'v'])
    async def vote(self, ctx, title, duration: typing.Optional[int]=20, *args):
        await self.run_poll(ctx, title, duration, False, *args)

    async def run_poll(self, ctx, title, duration, notify=False, *args):
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
        embed.add_field(name='Creator', value=ctx.guild.get_member(ctx.author.id).display_name, inline=True)
        embed.add_field(name='Duration', value=f"{duration}s", inline=True)
        embed.add_field(name='Notify?', value=f"{'On' if notify else 'Off'}", inline=True)
        message = await ctx.send(embed=embed)
        
        # set up voting and wait until poll closes
        for i in range(max_iters):
            await message.add_reaction(emoji=poll_reacts[i])
        await message.add_reaction("✅")

        # make background task to end the poll/count votes
        poll_task = asyncio.create_task(self.manage_poll(ctx, message, duration, title, poll_options, notify))

        # meanwhile, listen for incoming checkmark react which can prematurely end the poll
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "✅"
      
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=duration, check=check)
            if reaction.emoji == "✅":
                # end the background task managing poll and manually end it
                poll_task.cancel()
                await self.end_poll(ctx, message, duration, title, poll_options, notify)
        except asyncio.TimeoutError:
            return
    
    async def manage_poll(self, ctx, message, duration, title, poll_options, notify):
        await asyncio.sleep(duration)
        await self.end_poll(ctx, message, duration, title, poll_options, notify)
       
    async def end_poll(self, ctx, message, duration, title, poll_options, notify):
        message = await ctx.fetch_message(message.id)

        poll_close_embed = message.embeds[0]
        poll_close_embed.title = f"[CLOSED] Poll: {title}"
        await message.edit(embed=poll_close_embed)

        # find winning option
        max_count = 0
        max_index = None
        winning_options = []
        for i in range(len(message.reactions) - 1):
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