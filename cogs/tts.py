from discord.ext import commands
from discord import FFmpegPCMAudio
import discord
from gtts import gTTS
from tempfile import TemporaryFile
import urllib3

class TTS(commands.Cog):
    MY_ID = 192520503443849217

    def __init__(self, bot):
        urllib3.disable_warnings()
        self.bot = bot
        self.description="Experimental features..."
        self.voice = None
    
    @commands.command(help="Speak some text.")
    async def s(self, ctx, *args):
        if not self.user_in_vc(ctx):
            return await ctx.send("Please join a voice channel first!")

        speech = ' '.join(args)

        tts = gTTS(speech, lang='ja', tld='co.jp')
        file = TemporaryFile()
        tts.write_to_fp(file)
        file.seek(0)
        audio_src = FFmpegPCMAudio(file, pipe=True)
        if not self.is_connected(ctx):
            await self.join(ctx)

        self.voice.play(audio_src)

    @commands.command(help="Summon Melt to the current voice channel.")
    async def join(self, ctx):
        if not self.user_in_vc(ctx):
            return await ctx.send("Please join a voice channel first!")
        channel = ctx.author.voice.channel
        self.voice = await channel.connect()

    def user_in_vc(self, ctx):
        return ctx.author.voice is not None

    @commands.command(help="Dismiss Melt from the voice channel.")
    async def leave(self, ctx):
        if not self.is_connected(ctx):
            return await ctx.send("I'm not connected to any voice channels!")
        await self.voice.disconnect()
        await ctx.send("You're done already? Come back another time.")
    
    def is_connected(self, ctx):
        self.voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
        return self.voice is not None

def setup(bot):
    bot.add_cog(TTS(bot))