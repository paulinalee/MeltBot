from discord.ext import commands
from replit import db

class Admin(commands.Cog):
    MY_ID = 192520503443849217

    def __init__(self, bot):
        self.bot = bot
        self.description="Admin/debug commands."
    
    @commands.command(help="[admin] reset points for this server")
    async def equality(self, ctx):
        server = str(ctx.guild.id)
        if ctx.author.id == self.MY_ID:
            try: 
                for key in db['gamble'][server]:
                    del db['gamble'][server][key]
                await ctx.send("eat the rich")
            except KeyError:
                await ctx.send("no-op, table is already gone")
        else:
            await ctx.send("Perish this command is not for you")

    @commands.command(help="[admin] reset all points for all servers")
    async def thanos(self, ctx):
        if (ctx.author.id == self.MY_ID):
            for key in db:
                del db[key]
            try: 
                for key in db['gamble']:
                    del db['gamble'][key]
                await ctx.send("*thanos snaps*")
            except KeyError:
                await ctx.send("no-op, table is already gone")
        else:
            await ctx.send("Perish this command is not for you")
    
    @commands.command(help="[admin] drop all tables")
    async def drop(self, ctx):
        if (ctx.author.id == self.MY_ID):
            for key in db:
                del db[key]
            await ctx.send("monkaSteer")
        else:
            await ctx.send("Perish this command is not for you")
    
    @commands.command(help="[admin] log all tables")
    async def tables(self, ctx):
        if (ctx.author.id == self.MY_ID):
            print('KEYS')
            print(db.keys())
            print('SUBTABLES')
            for key in db:
                print(key)
                for k in db[key]:
                    print(db[key][k])
        else:
            await ctx.send("Perish this command is not for you")

def setup(bot):
    bot.add_cog(Admin(bot))