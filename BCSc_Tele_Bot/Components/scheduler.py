import time
import schedule
from Components.utilities import calc_time

class Scheduler():
    def __init__(self, set_before, bot, grps):
        self.scheduled = {}
        self.set_before = set_before #minutes
        self.bot = bot
        self.grps = grps

    def set_table_scheduler(self, table, subjects):
        self.clear_scheduler()
        for day in table:
            if len(table[day]) != 0:
                for details in table[day]:
                    time = details["time"][0]
                    key = f'{details["subject"]}-{day}-{time}'
                    subj_name = subjects[details["subject"]]
                    self.scheduled[key] = []
                    # class starting alert
                    self.scheduled[key].append(getattr(schedule.every(), day).at(time).do(
                        self.send_alert, details, 'Attention', f'{subj_name}</i> has started'
                    ))
                    # class reminders
                    self.scheduled[key].append(getattr(schedule.every(), day).at(calc_time(time, self.set_before)).do(
                        self.send_alert, details, 'Reminder', f'{subj_name}</i> will start at {time}'
                    ))
        # Create all the needed schedules for the week
        schedule.every().thursday.at("00:00").do(self.set_table_scheduler)

    def send_alert(self, details, title, msg):
        for grp_id in self.grps:
            out_msg = f'{msg}\n'
            for item in details:
                if item == 'time' or item == 'subject' or details[item] == '': continue
                out_msg += f'{details[item]}\n'
            self.bot.send_message(grp_id, f'<b>{title}</b>\n<i>{out_msg}', disable_web_page_preview=True)
        return schedule.CancelJob

    def run_scheduler(self, table, subjects):
        self.set_table_scheduler(table, subjects)
        while True:
            idle_time = schedule.idle_seconds()
            time.sleep(idle_time)
            schedule.run_pending()

    def clear_scheduler(self):
        self.scheduled = {}
        schedule.clear()
