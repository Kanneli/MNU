import json
from telebot import types
from datetime import datetime
from Components.utilities import *
from Components.error_handler import ErrorHandler

class TableManager:
    def __init__(self):
        self.load_timetable()
        self.load_subjects()
        self.cancelled = []
        self.error = ErrorHandler()

    def load_timetable(self):
        timetable = load_json('TimeTable')
        self.all = timetable
        for day in timetable:
            setattr(self, day, timetable[day])
    
    def load_subjects(self):
        self.subjects = load_json('Subjects')

    def send_timetable(self, param):
        out_msg = ''
        if param == 'all':
            for day in self.all:
                if len(self.all[day]) == 0: continue
                out_msg = get_times(day, out_msg, self.all, self.subjects, self.cancelled)
        else:
            if not param: param = datetime.today().strftime('%A').lower()
            elif param not in self.all: param = autocorrect_day(param)
            out_msg = get_times(param, out_msg, self.all, self.subjects, self.cancelled)
        return out_msg

    def cancel_markup(self, subject):
        markup = types.InlineKeyboardMarkup()
        markup.row_width = 1
        days = []
        for day in self.all:
            for schedule in self.all[day]:
                if schedule["subject"] == subject: days.append(day)
        if len(days) == 0: return None
        markup.add(types.InlineKeyboardButton('All', callback_data=f"{subject.upper()}-all"))
        for day in days:
            markup.add(types.InlineKeyboardButton(day.capitalize(), callback_data=f"{subject.upper()}-{day}"))
        return markup

    def initiate_cancel(self, param):
        out_msg = ''
        if not param: return self.error.missing_class, None
        if not isSubject(param, self.subjects): return self.error.invalid_class, None
        param = param.upper()
        markup = self.cancel_markup(param)
        if markup: out_msg = f"Which classes of {param} do you want to cancel?"
        else: out_msg = self.error.no_class
        return out_msg, markup

    def confirm_cancel(self, response, scheduler):
        cancel = False
        response_split = response.split('-')
        if response_split[1] == 'all': response = response_split[0]
        for data in scheduler.scheduled:
            if response in data:
                for item in scheduler.scheduled[data]:
                    scheduler.cancel_alert(item)
                self.cancelled.append(data)
                cancel = True
        if cancel: return f'The requested classes for {response_split[0]} have been cancelled'
        else: return self.error.something
