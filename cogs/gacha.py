from discord.ext import commands
import discord
from random import randrange, choices
from replit import db
from config import emotes, beg_dialogue

class Gacha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(description='Bet against Melt. Usage: !bet [wager]')
    async def bet(self, ctx, wager: int):
        if wager < 0:
            return await ctx.send("Cannot bet a negative value!")
            
        user = str(ctx.author.id)
        balance = 10000
        
        if user in db:
            balance = int(db[user])

        initial_balance = balance
        if (wager > initial_balance):
            return await ctx.send(f"Unable to bet, wager must not exceed current balance! You have {initial_balance} point{'s'[:initial_balance^1]}.")

        user_roll = randrange(0, 1000)
        cpu_roll = randrange(0, 1000)
        while cpu_roll == user_roll:
            # reroll if tie
            user_roll = randrange(0, 1000)
            cpu_roll = randrange(0, 1000)

        roll_msg = 'Your starting balance was {}.\nYou roll {}, Melt rolls {}! You now have {} {}.'

        if (user_roll > cpu_roll):
            balance += wager
            await ctx.send(roll_msg.format(initial_balance, user_roll, cpu_roll, balance, 'points' if balance != 1 else 'point'))
        else:
            balance -= wager
            await ctx.send(roll_msg.format(initial_balance, user_roll, cpu_roll, balance, 'points' if balance != 1 else 'point'))

        db[user] = balance

    @bet.error
    async def bet_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Use a numerical value when betting ' + emotes['paissabap'])

    @commands.command(description="Check your current balance, or join the betting table and receive a balance of 10000 points. Usage: !balance")
    async def balance(self, ctx):
        user = str(ctx.author.id)
        if user in db:
            await ctx.send(f"Your balance is {int(db[user])} point{'s'[:int(db[user])^1]}.")
        else:
            db[user] = 10000
            await ctx.send('Welcome to the betting table! Your balance is 10000 points.');
            
    @commands.command(description="Gacha for a chance to reset your point balance. Can only be used when points are below 10000. Usage: !beg")
    async def beg(self, ctx):
        user = str(ctx.author.id)
        if user not in db:
            return await ctx.send('Sorry, this command is only available for existing users! Use the command !balance to join the table.');

        user_roll = randrange(0, 5)
        if (db[user] >= 10000):
            return await ctx.send(f"You already have {db[user]} points! No begging {emotes['paissabap']}")

        if (user_roll == 3):
            db[user] = 10000
            return await ctx.send(f"Hmph, I guess I can reset your points just this once...")
        else:
            await ctx.send(f"{choices(beg_dialogue)[0]} (It seems your efforts were unsuccessful... Your balance remains {db[user]} point{'s'[:int(db[user])^1]}.)")

    @commands.command(description="Gift another user points from your own balance. Usage: !gift [user] [points]")
    async def gift(self, ctx, target: discord.User, points: int):
        user = str(ctx.author.id)
        other = str(target.id)
        if other not in db:
            return await ctx.send("Cannot gift points to a user who hasn't joined the table! You can join the table with the !balance command.");
        if user not in db:
            return await ctx.send("Cannot gift points before joining the table! Please initialize your balance with the !balance command.");
        if (points < 0):
            return await ctx.send(f"Unable to gift negative point value!");

        user_pts = int(db[user])

        if (points > user_pts):
            return await ctx.send(f"Unable to gift, gift value exceeds your current balance of {user_pts}!");
        
        db[other] += points
        db[user] -= points
        await ctx.send(f"{target.mention}, you have been gifted {points} point{'s'[:int(db[user])^1]} by {ctx.author.mention}! Your balance is now {int(db[other])}.")

    @gift.error
    async def gift_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send('Please try again! The command format should be !gift @[user] [points]')
    

def setup(bot):
  bot.add_cog(Gacha(bot))