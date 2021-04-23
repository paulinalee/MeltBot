from discord.ext import commands
from datetime import datetime
from pytz import timezone
import typing

class Time(commands.Cog):
    TIMEZONE_ABBREVIATIONS = {
        # mapping common abbreviations that aren't in pytz since they can refer to multiple zones
        'EST': 'US/Eastern',
        'PST': 'US/Pacific',
        'CST': 'US/Central',
        'JST': 'Japan'
    }
    def __init__(self, bot):
        self.bot = bot
        self.description="Utility functions related to time."
    
    @commands.command(help="[under development]", aliases=['timenow', 'currenttime'])
    async def now(self, ctx, zone: typing.Optional[str]=None):
        tz = None
        print(zone)
        if zone is not None:
            print('hi')
            try:
                tz = timezone(zone)
            except:
                return await ctx.send("Invalid timezone.")
        else:
            tz = timezone("UTC")
        
        print(datetime.now(tz))
        print('finish')
        

    @commands.command(help="Convert from one timezone to another. Use at your own risk cause I hate working with time and it's probably janky as hell.", aliases=['converttime', 'whattime'])
    async def convert(self, ctx, from_zone: str, requested_time: str, to_zone: str):
        # need to do some checks for potential funkiness since gmt+10 is under 'etc/gmt+10'
        from_zone, to_zone = from_zone.upper(), to_zone.upper()
        if from_zone.startswith('GMT'):
            from_zone = 'ETC/' + from_zone
        if to_zone.startswith('GMT'):
            to_zone = 'ETC/' + to_zone

        # also checking if we've used a common abbreviation that's not in pytz
        from_zone, to_zone = self.check_abbreviations(from_zone), self.check_abbreviations(to_zone)
        
        try:
            from_tz = timezone(from_zone)
            to_tz = timezone(to_zone)
        except:
            return await ctx.send("Please recheck timezone format.")

        try:
            hours, minutes = requested_time.split(":")
            from_time_now = datetime.now(from_tz)
            time_to_convert = datetime(from_time_now.year, from_time_now.month, from_time_now.day, int(hours), int(minutes))
            time_to_convert = from_tz.localize(time_to_convert)
            converted_time = time_to_convert.astimezone(to_tz)

            day_modifier = ''

            if converted_time.date() > from_time_now.date():
                day_modifier = ' the next day'
            elif converted_time.date() < from_time_now.date():
                day_modifier = ' the previous day'

            await ctx.send(f"🕒 {time_to_convert.hour:02}:{time_to_convert.minute:02} in {from_zone} is {converted_time.hour:02}:{converted_time.minute:02}{day_modifier} in {to_zone}!")
        except ValueError:
            return await ctx.send("Invalid time format!")

    def check_abbreviations(self, timezone):
        # returns what the abbreviation corresponds to if it exists in TIMEZONE_ABBREVIATIONS, otherwise returns original value
        return self.TIMEZONE_ABBREVIATIONS[timezone] if timezone in self.TIMEZONE_ABBREVIATIONS else timezone

def setup(bot):
    bot.add_cog(Time(bot))