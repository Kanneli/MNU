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
json_files = {}
file_names = ['Subjects', 'TimeTable']
grp_ids = open('.groups').read().split(',')

# Load JSONs
def load_json(files):
	global json_files
	for file_name in files:
		json_file = open(f'./JSON/{file_name}.json')
		json_files[file_name] = json.load(json_file)

load_json(file_names)

# Utilities
def get_param(text):
	if len(text.split(' ')) > 1: return text.split(' ')[1].lower().strip()

def get_times(day, out_msg):
	if not day: return '<b>Invalid param</b>'
	out_msg += f'<b>{day.upper()}\n</b>'
	if len(json_files['TimeTable'][day]) == 0: return out_msg + '<i>No classes found</i>'

	for details in json_files['TimeTable'][day]:
		for item in details:
			if details[item] != "":
				if item == 'subject':
					out_msg += f'<i>{json_files["Subjects"][details[item]]}:</i>'
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

def calc_time(time, diff):
	time = time.split(':')
	new_hr = int(time[0])
	new_min = (int(time[1]) - diff) % 60
	if new_min > int(time[1]): new_hr = (new_hr - 1) % 24
	return f'{"{0:0=2d}".format(new_hr)}:{"{0:0=2d}".format(new_min)}'

# Main Commands
@bot.message_handler(commands=['table'])
def send_timetable(message):
	out_msg = ''
	param = get_param(message.text)
	
	if param == 'all':
		for day in json_files['TimeTable']:
			if len(json_files['TimeTable'][day]) == 0: continue
			out_msg = get_times(day, out_msg)
	else:
		if not param: param = datetime.today().strftime('%A').lower()
		elif param not in json_files['TimeTable']: param = autocorrect_day(param)
		out_msg = get_times(param, out_msg)

	bot.reply_to(message, out_msg)

# Set Scheduler and Alerts
def send_alert(details, title, msg):
	for grp_id in grp_ids:
		out_msg = f'{msg}\n'
		for item in details:
			if item == 'time' or item == 'subject' or details[item] == '': continue
			out_msg += f'{details[item]}\n'
		bot.send_message(grp_id, f'<b>{title}</b>\n<i>{out_msg}')

def set_scheduler():
	# set_before is in minutes
	set_before = 30
	
	for day in json_files['TimeTable']:
		if len(json_files['TimeTable'][day]) != 0:
			for details in json_files['TimeTable'][day]:
				time = details["time"][0]
				subj_name = json_files["Subjects"][details["subject"]]
				# class starting alert
				getattr(schedule.every(), day).at(time).do(
					send_alert, details, 'Attention', f'{subj_name}</i> has started'
				)
				# class reminders
				getattr(schedule.every(), day).at(calc_time(time, set_before)).do(
					send_alert, details, 'Reminder', f'{subj_name}</i> will start at {time}'
				)

def run_scheduler():
	set_scheduler()
	while True:
		idle_time = schedule.idle_seconds()
		time.sleep(idle_time)
		schedule.run_pending()

# Running bot
threading.Thread(target=run_scheduler).start()
threading.Thread(target=bot.polling).start()
