from discord.ext import commands
import discord
from random import randrange, choices
from replit import db
from config import emotes, beg_dialogue
from disputils import BotEmbedPaginator
import typing

class Gacha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.description = "Gambling functions."
        if 'gamble' not in db:
            db['gamble'] = {}

    @commands.command(help="Check the betting leaderboard.", aliases=['leaderboards', 'rankings'])
    async def leaderboard(self, ctx):
        LEADERBOARD_PAGE_LIMIT = 15
        if not self.server_table_exists(ctx):
            return await ctx.send(f"No leaderboard available, no one in the server has made any bets! Use `{self.bot.ctx_prefix(ctx)}help bet` to see how to play.")

        server = db['gamble'][str(ctx.guild.id)]
        leaderboard = sorted(server, key=server.get, reverse=True)
        
        output_list = []
        users = []
        pts = []
        for player_id in leaderboard:
            player_name = ctx.guild.get_member(int(player_id)).display_name
            player_pts = server[player_id]
            output_list.append(f"{player_name}: {player_pts}")
            users.append(player_name)
            pts.append(str(player_pts))
        
        paginated_users = [users[x:x + LEADERBOARD_PAGE_LIMIT] for x in range(0, len(users), LEADERBOARD_PAGE_LIMIT)]
        paginated_pts = [pts[x:x + LEADERBOARD_PAGE_LIMIT] for x in range(0, len(pts), LEADERBOARD_PAGE_LIMIT)]
        embeds = []
        for i in range(len(paginated_users)):
            embed = discord.Embed(title='Betting Leaderboard')
            embed.add_field(name='Player', value='\n'.join(paginated_users[i]), inline=True)
            embed.add_field(name='Points', value='\n'.join(paginated_pts[i]), inline=True)
            embeds.append(embed)
        
        paginator = BotEmbedPaginator(ctx, embeds)
        await paginator.run()

    @commands.command(help='Bet against Melt. Wager can be a numerical value, or \"all\" to bet everything.', aliases=['gamble'])
    async def bet(self, ctx, wager: typing.Union[int, str]):
        use_all = False;
        try:
            wager = int(wager)
        except ValueError:
            if wager.lower() == 'all':
                use_all = True
            else:
                raise commands.BadArgument
        else:
            if wager < 0:
                return await ctx.send("Cannot bet a negative value!")

        player, server = self.get_ids(ctx, ctx.author.id)
        balance = 10000
        first_time = False

        if self.at_table(ctx, player):
            balance = int(db['gamble'][server][player])
        else:
            first_time = True
            self.init_server_table(ctx)

        initial_balance = balance
        if (use_all):
            wager = balance
        elif (wager > initial_balance):
            return await ctx.send(
                f"Unable to bet, wager must not exceed current balance! You have {initial_balance} point{'s'[:initial_balance^1]}."
            )

        player_roll = randrange(0, 1000)
        cpu_roll = randrange(0, 1000)
        while cpu_roll == player_roll:
            # reroll if tie
            player_roll = randrange(0, 1000)
            cpu_roll = randrange(0, 1000)

        first_time_msg = 'Welcome to the betting table!\n' if first_time else ''
        roll_msg = first_time_msg + 'Your starting balance was {}.\nYou roll {}, Melt rolls {}! You now have {} {}.'

        if (player_roll > cpu_roll):
            balance += wager
            await ctx.send(
                roll_msg.format(initial_balance, player_roll, cpu_roll,
                                balance,
                                'points' if balance != 1 else 'point'))
        else:
            balance -= wager
            await ctx.send(
                roll_msg.format(initial_balance, player_roll, cpu_roll,
                                balance,
                                'points' if balance != 1 else 'point'))

        db['gamble'][server][player] = balance

    @bet.error
    async def bet_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Use a numerical value or `all` when betting ' +
                           emotes['paissabap'])

    @commands.command(
        help=
        "Check your current balance, or join the betting table and receive a balance of 10000 points.",
        aliases=['points']
    )
    async def balance(self, ctx):
        player, server = self.get_ids(ctx, ctx.author.id)
        if self.at_table(ctx, player):
            await ctx.send(
                f"Your balance is {int(db['gamble'][server][player])} point{'s'[:int(db['gamble'][server][player])^1]}."
            )
        else:
            if not self.server_table_exists(ctx):
                self.init_server_table(ctx)
            db['gamble'][server][player] = 10000
            await ctx.send(
                'Welcome to the betting table! Your balance is 10000 points.')

    @commands.command(
        help=
        "Gacha for a chance to reset your point balance. Can only be used when points are below 10000.",
        aliases=['mercy', 'pls']
    )
    async def beg(self, ctx):
        player, server = self.get_ids(ctx, ctx.author.id)
        if not self.at_table(ctx, player):
            return await ctx.send(
                f"Sorry, this command is only available for existing players! Use the command `{self.bot.ctx_prefix(ctx)}balance` to join the table."
            )

        player_roll = randrange(0, 4)
        if (db['gamble'][server][player] >= 10000):
            return await ctx.send(
                f"You already have {db['gamble'][server][player]} points! No begging {emotes['paissabap']}"
            )

        if (player_roll == 3):
            db['gamble'][server][player] = 10000
            return await ctx.send(
                f"Hmph, I guess I can reset your points just this once...")
        else:
            await ctx.send(
                f"{choices(beg_dialogue)[0]} (It seems your efforts were unsuccessful... Your balance remains {db['gamble'][server][player]} point{'s'[:int(db['gamble'][server][player])^1]}.)"
            )

    @commands.command(help="Gift another player points from your own balance.",
                      aliases=['give'])
    async def gift(self, ctx, target: discord.User, points: int):
        player, server = self.get_ids(ctx, ctx.author.id)
        target_player = str(target.id)
        prefix = self.bot.ctx_prefix(ctx)
        if not self.at_table(ctx, target_player):
            return await ctx.send(
                f"Cannot gift points to a player who hasn't joined the table! You can join the table with the `{prefix}balance` command."
            )
        if not self.at_table(ctx, player):
            return await ctx.send(
                f"Cannot gift points before joining the table! Please initialize your balance with the `{prefix}balance` command."
            )
        if (points < 0):
            return await ctx.send(f"Unable to gift negative point value!")

        player_pts = int(db['gamble'][server][player])

        if (points > player_pts):
            return await ctx.send(
                f"Unable to gift, gift value exceeds your current balance of {player_pts}!"
            )

        db['gamble'][server][target_player] += points
        db['gamble'][server][player] -= points
        await ctx.send(
            f"{target.mention}, you have been gifted {points} point{'s'[:int(db['gamble'][server][player])^1]} by {ctx.author.mention}! Your balance is now {int(db['gamble'][server][target_player])}."
        )

    def at_table(self, ctx, player_id):
        player, server = self.get_ids(ctx, player_id)
        return self.server_table_exists(ctx) and player in db['gamble'][server]

    def server_table_exists(self, ctx):
        return str(ctx.guild.id) in db['gamble']

    def init_server_table(self, ctx):
        if 'gamble' not in db:
            db['gamble'] = {}

        db['gamble'][str(ctx.guild.id)] = {}

    def get_ids(self, ctx, player_id: int):
        # returns player id (as string) and server id (as string) so I don't have to keep converting them
        return str(player_id), str(ctx.guild.id)

    @gift.error
    async def gift_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(
                'Please try again! The command format should be !gift @[player] [points]'
            )


def setup(bot):
    bot.add_cog(Gacha(bot))
