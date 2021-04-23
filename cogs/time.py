from discord.ext import commands
from datetime import datetime
from pytz import timezone
import typing
import discord
import dateparser

class Time(commands.Cog):
    # mapping common abbreviations that aren't in pytz since they can refer to multiple zones
    TIMEZONE_ABBREVIATIONS = {
        'EST': 'US/Eastern',
        'PST': 'US/Pacific',
        'CST': 'US/Central',
        'JST': 'Japan',
        'AEST': 'Australia/Sydney',
        'ACST': 'Australia/Adelaide',
        'AWST': 'Australia/West'
    }

    def __init__(self, bot):
        self.bot = bot
        self.description="Utility functions related to time."
    
    @commands.command(help="Check the current time for a timezone. Uses UTC if no timezone specified.", aliases=['timenow'])
    async def now(self, ctx, zone: typing.Optional[str]=None):
        tz = None
        original_zone = None

        if zone is not None:
            # checking if we've used a common abbreviation
            zone = self.check_abbreviations(zone.upper())
            original_zone = zone
            zone = self.modify_gmt(zone)
            try:
                tz = timezone(zone)
            except:
                return await ctx.send("Invalid timezone provided.")
        else:
            zone = 'UTC'
            original_zone = zone
            tz = timezone("UTC")
        
        time_date = datetime.now(tz)
        formatted_time = time_date.strftime("%b %d, %Y, %H:%M (%I:%M %p)")
        await ctx.send(f"🕒 It is currently **{formatted_time}** in **{original_zone.upper()}**.")

    @commands.command(brief="Convert from one timezone to another.",
        help="Convert a time (24 hour format) to a specific timezone.\n\nFor convenience, some timezone abbreviations will be synonymous to a zone regardless of daylight savings. As an example, EST will be interpreted as the US/Eastern timezone, even if US/Eastern is currently observing EDT, since EST is the more common abbreviation.\n\nThe converted time will also be auto-adjusted for DST based on the current date (so converting 1:00 from CST to JST would be like converting 1:00 on the current date in CST to JST).",
        aliases=['tz'])
    async def convert(self, ctx, requested_time: str, from_zone: str, to_zone: str, *args):
        from_zone, to_zone = from_zone.upper(), to_zone.upper() # make same case before comparing
        
        date_str = ' '.join(args)
        time_date = dateparser.parse(date_str)

        # checking if we've used a common abbreviation
        from_zone, to_zone = self.check_abbreviations(from_zone), self.check_abbreviations(to_zone)

        # save for output before processing for conversion, we save here instead of after the next line to prevent saving the confusing etc/gmt zones
        original_from, original_to = from_zone, to_zone

        # for some ungodly reason etc/gmt+10 actually means gmt-10, so we have to finangle our args into shape
        # see https://en.wikipedia.org/wiki/Tz_database
        from_zone, to_zone = self.modify_gmt(from_zone), self.modify_gmt(to_zone)
        
        try:
            from_tz = timezone(from_zone)
            to_tz = timezone(to_zone)
        except:
            return await ctx.send("Please recheck timezone format.")

        try:
            # some weird off-by-4minutes bug when using strtotime to parse so just parse time manually and construct a datetime
            hours, minutes = requested_time.split(":")

            # invalid/no date passed in, use current date of starting timezone
            if time_date is None:
                time_date = datetime.now(from_tz)
            
            time_to_convert = datetime(time_date.year, time_date.month, time_date.day, int(hours), int(minutes))
            time_to_convert = from_tz.localize(time_to_convert)
            converted_time = time_to_convert.astimezone(to_tz)
            await ctx.send(embed=self.format_embed(original_from, original_to, time_to_convert, converted_time))
        except ValueError:
            return await ctx.send("Invalid time format!")

    def format_embed(self, start_tz, dest_tz, s_datettime, d_datettime):
        day_modifier = ''
        if d_datettime.date() > s_datettime.date():
            day_modifier = ' (next day)'
        elif d_datettime.date() < s_datettime.date():
            day_modifier = ' (previous day)'

        start_time = s_datettime.strftime(f"%H:%M (%I:%M %p)\n%b %d, %Y\n\n**In DST?**\n{'Yes' if s_datettime.dst() else 'No'}")
        end_time = d_datettime.strftime(f"%H:%M (%I:%M %p)\n%b %d, %Y{day_modifier}\n\n**In DST?**\n{'Yes' if d_datettime.dst() else 'No'}")

        embed = discord.Embed(title='🕒 Convert Time')
        embed.add_field(name=start_tz, value=start_time, inline=True)
        embed.add_field(name=dest_tz, value=end_time, inline=True)
        return embed

    def check_abbreviations(self, timezone):
        # returns what the abbreviation corresponds to if it exists in TIMEZONE_ABBREVIATIONS, otherwise returns original value
        return self.TIMEZONE_ABBREVIATIONS[timezone].upper() if timezone in self.TIMEZONE_ABBREVIATIONS else timezone
    
    def modify_gmt(self, gmt):
        if (gmt.startswith("GMT")):
            gmt = 'ETC/' + gmt
        if '-' in gmt:
            gmt = gmt.replace('-', '+', 1)
        elif '+' in gmt:
            gmt = gmt.replace('+', '-', 1)
        return gmt

def setup(bot):
    bot.add_cog(Time(bot))