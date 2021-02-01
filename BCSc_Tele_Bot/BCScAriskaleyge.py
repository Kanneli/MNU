import telebot
import json
from datetime import datetime
import threading
import schedule
import time

# Bot API
key = open('.key').read()
bot = telebot.TeleBot(key, parse_mode='MarkdownV2')

# Variables
timetable = []
subjects = {}
grp_ids = open('.groups').read().split(',')

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

def get_param(text):
	if len(text.split(' ')) > 1: return text.split(' ')[1].lower().strip()

def get_times(day, out_msg):
	out_msg += f'*{day.capitalize()}*\n'
	if len(timetable[day]) == 0: return out_msg + '_No classes found_'
	for subject in timetable[day]: out_msg += f'_{subjects[subject]}_: {timetable[day][subject][0]} \- {timetable[day][subject][1]}\n'
	return out_msg + '\n'

def autocorrect_day(param):
	days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday']
	if param != 'day' and len(param) >= 3:
		for day in days:
			if param in day: return day

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

def send_reminder(subject, time):
	for grp_id in grp_ids:
		bot.send_message(grp_id, f'*Reminder*\n{subjects[subject]} will start at {time}')

def set_scheduler():
	# set_before is in minutes
	set_before = 30

	for day in timetable:
		if len(timetable[day]) != 0:
			for subject in timetable[day]:
				time = timetable[day][subject][0].split(':')
				new_min = (int(time[1]) - set_before) % 60
				if new_min > int(time[1]): new_hr = (int(time[0]) - 1) % 24
				else: new_hr = int(time[0])
				reminder_time = f'{"{0:0=2d}".format(new_hr)}:{"{0:0=2d}".format(new_min)}'
				getattr(schedule.every(), day).at(reminder_time).do(send_reminder, subject, timetable[day][subject][0])

def run_scheduler():
	set_scheduler()
	while True:
		schedule.run_pending()
		time.sleep(1)

for grp_id in grp_ids:
	print(grp_ids)
	bot.send_message(grp_id, f'Test')

threading.Thread(target=run_scheduler).start()
threading.Thread(target=bot.polling).start()
