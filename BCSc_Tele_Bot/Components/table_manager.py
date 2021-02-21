import json
from Components.utilities import *
from datetime import datetime

class TableManager:
    def __init__(self):
        self.load_timetable()
        self.load_subjects()
        self.cancelled = []

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
