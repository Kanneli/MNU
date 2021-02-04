import telebot
import json
from datetime import datetime
import threading
import schedule
import time

# Bot API
key = open('.key').read()
bot = telebot.TeleBot(key, parse_mode='html')

# Variables
timetable = []
subjects = {}
grp_ids = open('.groups').read().split(',')

# Load Files
def get_timetable():
	global timetable
	timetable_file = open('./JSON/TimeTable.json')
	timetable = json.load(timetable_file)

def get_subjects():
	global subjects
	subjects_file = open('./JSON/Subjects.json')
	subjects = json.load(subjects_file)

get_timetable()
get_subjects()

# Utilities
def get_param(text):
	if len(text.split(' ')) > 1: return text.split(' ')[1].lower().strip()

def get_times(day, out_msg):
	out_msg += f'<b>{day.upper()}\n</b>'
	if len(timetable[day]) == 0: return out_msg + '<i>No classes found</i>'

	for details in timetable[day]:
		for item in details:
			if details[item] != "":
				if item == 'subject':
					out_msg += f'<i>{subjects[details[item]]}:</i>'
					continue
				elif item == 'time':
					out_msg += f' {details[item][0]} - {details[item][1]}\n'
					continue
				out_msg += f'{details[item]}\n'
	return out_msg + '\n'

def autocorrect_day(param):
	days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday']
	if param != 'day' and len(param) >= 3:
		for day in days:
			if param in day: return day

# Main
@bot.message_handler(commands=['table'])
def send_timetable(message):
	out_msg = ''
	param = get_param(message.text)
	
	if param == 'all':
		for day in timetable:
			if len(timetable[day]) == 0: continue
			out_msg = get_times(day, out_msg)
	else:
		if not param: param = datetime.today().strftime('%A').lower()
		elif param not in timetable: param = autocorrect_day(param)
		out_msg = get_times(param, out_msg)

	bot.reply_to(message, out_msg)

# Scheduler
def send_reminder(details):
	for grp_id in grp_ids:
		out_msg = f'{subjects[details["subject"]]}</i> will start at {details["time"][0]}\n'
		for item in details:
			if item == 'time' or item == 'subject' or details[item] == '': continue
			out_msg += f'{details[item]}\n'
		bot.send_message(grp_id, f'<b>Reminder</b>\n<i>{out_msg}')

def send_class_start(details):
	for grp_id in grp_ids:
		out_msg = f'{subjects[details["subject"]]}</i> has started\n'
		for item in details:
			if item == 'time' or item == 'subject' or details[item] == '': continue
			out_msg += f'{details[item]}\n'
		bot.send_message(grp_id, f'<b>Attention</b>\n<i>{out_msg}')

def set_scheduler():
	# set_before is in minutes
	set_before = 30

	# class reminders
	for day in timetable:
		if len(timetable[day]) != 0:
			for details in timetable[day]:
				time = details["time"][0].split(':')
				new_min = (int(time[1]) - set_before) % 60
				if new_min > int(time[1]): new_hr = (int(time[0]) - 1) % 24
				else: new_hr = int(time[0])
				reminder_time = f'{"{0:0=2d}".format(new_hr)}:{"{0:0=2d}".format(new_min)}'
				getattr(schedule.every(), day).at(reminder_time).do(send_reminder, details)

	# class starting alert
	for day in timetable:
		if len(timetable[day]) != 0:
			for details in timetable[day]:
				time = details["time"][0]
				getattr(schedule.every(), day).at(time).do(send_class_start, details)

def run_scheduler():
	set_scheduler()
	while True:
		schedule.run_pending()
		time.sleep(1)

# Running bot
threading.Thread(target=run_scheduler).start()
threading.Thread(target=bot.polling).start()
