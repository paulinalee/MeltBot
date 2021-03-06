from discord.ext import commands
from replit import db
from sqlitedict import SqliteDict

class Admin(commands.Cog):
    MY_ID = 192520503443849217

    def __init__(self, bot):
        self.bot = bot
        self.description="Admin/debug commands."
        self.gamble_db = SqliteDict('./gamble.sqlite', autocommit=True)
        self.remind_db = SqliteDict('./remind.sqlite', autocommit=True)
        self.prefix_db = SqliteDict('./prefix.sqlite', autocommit=True)
    
    @commands.command(help="[admin] reset points for this server")
    async def perish(self, ctx):
        server = str(ctx.guild.id)
        if ctx.author.id == self.MY_ID:
            try: 
                # del db['gamble'][server]
                del self.gamble_db[server]
                await ctx.send("donezo")
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

    @commands.command(help="[admin] drop raid table")
    async def rdrop(self, ctx):
        if (ctx.author.id == self.MY_ID):
            if db['reminders']:
                for key in db['reminders']:
                    del db['reminders'][key]
            del db['reminders']
            await ctx.send("all done")

    @commands.command(help="[admin] log all tables")
    async def tables(self, ctx):
        for key, value in self.gamble_db.iteritems():
            print(f"key: {key} value: {value}")
        for key, value in self.prefix_db.iteritems():
            print(f"key: {key} value: {value}")
        if (ctx.author.id == self.MY_ID):
            print('KEYS')
            print(db.keys())
            print('SUBTABLES')
            for key in db:
                print(key)
                for k in db[key]:
                    print(f'KEY: {k} // VALUE: {db[key][k]}')
        else:
            await ctx.send("Perish this command is not for you")

def setup(bot):
    bot.add_cog(Admin(bot))