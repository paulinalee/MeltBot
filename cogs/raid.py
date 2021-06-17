from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from dateutil.rrule import rrule, WEEKLY, MO, TU, WE, TH, FR, SA, SU
import typing
from replit import db
from sqlitedict import SqliteDict

class Raid(commands.Cog):
    ABBREVIATIONS = {
        "mon": MO,
        "tues": TU,
        "wed": WE,
        "thurs": TH,
        "fri": FR,
        "sat": SA,
        "sun": SU
    }

    def __init__(self, bot):
        self.bot = bot
        self.description="Raid scheduling stuff"
        self.db = SqliteDict('./remind.sqlite', autocommit=True)
    
    @commands.command(help="Set recurring weekly reminders. Default remind_interval is 1 (every week). USE UTC!!")
    async def remind(self, ctx, ping_role, remind_msg, day, remind_time, remind_interval: typing.Optional[int]=1, repeat: typing.Optional[str]='', remind_early_minutes: typing.Optional[int]=30):
        reminder_args = ping_role + day + remind_time + str(remind_interval) + repeat
        recurring = False
        if repeat == 'recurring':
            recurring = True
        server = str(ctx.guild.id)
        if server not in db['reminders']:
            # init tables if they didn't exist before
            db['reminders'][server] = {}
            db['reminders'][server]['list'] = {} # ALL the reminders
            db['reminders'][server]['early_reminders'] = {} # maps reminder key to early reminder key for the above table
            db['reminders'][server]['recurring'] = {}

        await self.init_reminder(ctx, server, ping_role, remind_msg, day, remind_time, remind_interval, recurring, reminder_args, remind_early_minutes)

    @remind.error
    async def remind_error(self, ctx, error):
        await ctx.send(f"Please recheck your command format! Use {self.bot.ctx_prefix(ctx)}help remind for more assistance.")

    @commands.command(help="Check existing reminders.", aliases=['remindlist', 'raidlist'])
    async def reminders(self, ctx):
        server = str(ctx.guild.id)
        if server not in db['reminders']:
            return await ctx.send("There are no reminders set for this server!")
        reminders = db['reminders'][server]['list']
        print(reminders)
        
    @commands.command(help="Delete a reminder.")
    async def deletereminder(self, ctx, raid_index):
        server = str(ctx.guild.id)
        if server not in db['reminders']:
            return await ctx.send(f'Invalid reminder ID. Use {self.bot.ctx_prefix(ctx)}reminders to see reminders active on this server.')
        db['reminders'][server]['list'].keys()
        
    async def init_reminder(self, ctx, server, role, remind_msg, day, remind_time, interval, recurring, reminder_args, remind_early_minutes):
        # before calling this function other functions should check that the correct dbs already exist
        hours, minutes = remind_time.split(':')
        rule = rrule(WEEKLY, byweekday=self.ABBREVIATIONS[day], byhour=int(hours), byminute=int(minutes), bysecond=0, count=1)
        next_time = list(rule)[0] # these are datetimes
        next_early_reminder = next_time - timedelta(minutes=remind_early_minutes)
        next_timef = next_time.strftime("%Y-%m-%d %H:%M:%S")
        next_early_reminderf = next_early_reminder.strftime("%Y-%m-%d %H:%M:%S")
        reminder_key = next_timef + reminder_args
        early_reminder_key = next_early_reminderf + reminder_args

        if reminder_key in db['reminders'][server]['list']:
            return await ctx.send(f'Reminder has already been created! Use {self.bot.ctx_prefix(ctx)}reminders to check the active reminders for this server.')

        if recurring:
            # hacky but we're just gonna set an empty value for the key, the main idea is that if the key exists its recurring
            db['reminders'][server]['recurring'][reminder_key] = ''
            db['reminders'][server]['recurring'][early_reminder_key] = ''

        # save our reminder in the db, for the first one we want to also pass thru info on the server ID and channel
        channel_id = ctx.channel.id
        server_id = ctx.guild.id
        reminder_info = f'{channel_id}/{server_id}/{next_timef}'
        early_reminder_info = f'{channel_id}/{server_id}/{next_early_reminderf}'
        db['reminders'][server]['list'][reminder_key] = reminder_info
        db['reminders'][server]['list'][early_reminder_key] = early_reminder_info
        db['reminders'][server]['early_reminders'][reminder_key] = early_reminder_key
        
        # start the task
        asyncio.create_task(self.send_reminder(channel_id, server_id, server, role, remind_msg, self.ABBREVIATIONS[day], next_time, recurring, reminder_key))
        asyncio.create_task(self.send_reminder(channel_id, server_id, server, role, remind_msg, self.ABBREVIATIONS[day], next_early_reminder, recurring, early_reminder_key, True, remind_early_minutes))

    async def send_reminder(self, channel_id, server_id, server, role, remind_msg, day, wake_time, recurring, reminder_key, is_early_reminder=False, early_by=0):
        # clear the existing db value to mark this as done
        print(db['reminders'][server]['list'][reminder_key])
        del db['reminders'][server]['list'][reminder_key]
        if reminder_key not in db['reminders'][server]['list']:
            print('deleted')
            print(db['reminders'][server]['list'])

        # calc the time to sleep
        sleep_time = wake_time - datetime.now()
        sleep_time = sleep_time.total_seconds()
        print(f'sleeping for {sleep_time}s to wake on {wake_time}')
        if (sleep_time < 0):
            # this can happen if the early remind time set is before the next remind date due to when you run the command
            # if that happens just do nothing and return
            return
        
        await asyncio.sleep(sleep_time)

        # when we get here it's time to remind
        channel = self.bot.get_guild(server_id).get_channel(channel_id)

        if recurring:
            # set the next time
            rule = rrule(WEEKLY, byweekday=self.ABBREVIATIONS[day], byhour=wake_time.hours, byminute=wake_time.minutes, bysecond=0, count=1)
            next_time = list(rule)[0]

            # mark the next times in the db
            reminder_info = f'{channel_id}/{server_id}/{next_time.strftime("%Y-%m-%d %H:%M:%S")}'
            db['reminders'][server]['list'][reminder_key] = reminder_info

            # send off new tasks
            asyncio.create_task(self.send_reminder(channel_id, server_id, server, role, day, next_time, recurring, reminder_key))
        else:
            # if not recurring make sure to remove the key association from early_reminders db if available
            if not is_early_reminder and reminder_key in db['reminders'][server]['early_reminders']:
                del db['reminders'][server]['early_reminders']

        if is_early_reminder:
            await channel.send(f'{role}, {early_by} minute(s) until reminder: {remind_msg}')
        else:
            await channel.send(f'{role}, reminder: {remind_msg}')

    def reinit_reminders(self):
        # go into the db and reinit tasks for each entry

        # for server in db['reminders']:
        #     for reminder_key, reminder in db['reminders'][server]['list'].items():
        #         # parse back out the reminder_info
        #         channel_id, server_id, remind_time = reminder.split('/')

        #         if reminder_key in db['reminders'][server]['early_reminders']:
                    
                


        print('a')

def setup(bot):
    bot.add_cog(Raid(bot))