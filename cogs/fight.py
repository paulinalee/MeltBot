import discord
from discord.ext import commands
from config import fight_actions, emotes
from random import choices, randrange
import asyncio

class Fight(commands.Cog):
    YES = '\u2713'
    NO = '\u274c'
    def __init__(self, bot):
        self.bot = bot
        self.description="Module that handles fight minigame."

    async def action(self, ctx, player, target, p1_hp, p2_hp):
        await ctx.send(f"{player.mention}, your move! Type `attack` to take a turn.")

        def check(msg):
            return msg.author == player and msg.content.lower() == 'attack'
            
        try:
            msg = await self.bot.wait_for('message', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('Turn timed out! The match has been forfeit.')
        else:
            roll = randrange(0, 100)
            p2_hp -= roll
            if (p2_hp <= 0):
                return await ctx.send(f"The fight has concluded! {player.mention} deals {roll} damage, knocking out {target.mention} and winning with {p1_hp} HP left!")
            await ctx.send(choices(fight_actions)[0])
            await ctx.send(f"{player.mention} deals {roll} damage to {target.mention}, who now has {p2_hp} HP!")
            await self.action(ctx, target, msg.author, p2_hp, p1_hp)

    @commands.command(help="Challenge another user to a fight. Both players start with 100 HP and take turns attacking.")
    async def fight(self, ctx, target: discord.User):
        request = await ctx.send(f"{target.mention}, you have been challenged to a fight! Do you accept?")
        await request.add_reaction("✅")
        await request.add_reaction("❌")

        def check(reaction, user):
            return user == target and (str(reaction.emoji) == "✅" or "❌")

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send('Challenge timeout expired!')
        else:
            if reaction.emoji == "❌":
                await ctx.send(f"Understandable have a nice day {emotes['paimonfrench']}")
            elif reaction.emoji == "✅":
                await ctx.send("Both players will start with 100 HP. Rolling for first turn...")
                p1_roll = randrange(0, 1000)
                p2_roll = randrange(0, 1000)
                while p1_roll == p2_roll:
                    p1_roll = randrange(0, 1000)
                    p2_roll = randrange(0, 1000)
                roll_result = f"{ctx.author.name} rolled {p1_roll} and {target.name} rolled {p2_roll}!"
                if (p1_roll > p2_roll):
                    await ctx.send(f"{roll_result}\n{ctx.author.name} will go first.")
                    await self.action(ctx, ctx.author, target, 100, 100)
                else:
                    await ctx.send(f"{roll_result}\n{target.name} will go first.")
                    await self.action(ctx, target, ctx.author, 100, 100)

    
    @fight.error
    async def fight_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("Couldn't find that user...")

def setup(bot):
    bot.add_cog(Fight(bot))