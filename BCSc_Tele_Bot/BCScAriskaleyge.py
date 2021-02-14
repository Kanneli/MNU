import os
import json
import time
import random
import telebot
import schedule
import threading
from datetime import datetime

# Bot API
key = open('.key').read()
bot = telebot.TeleBot(key, parse_mode='html')

# Variables
scheduled = {}
cancelled = []
json_files = {}
file_names = ['Subjects', 'TimeTable']
grp_ids = open('.groups').read().split(',')
admin_ids = open('.admins').read().split(',')
hamajehey = ['ނޫޅެން', 'ކައޭ ޖެހިބަ އަޖައިބެއް ނުން', 'ހަމަ ހުވާތަ', 'ހެހެ ވިސްނާލާނަން', 'ތީ އެންމެ މައިތިރި މީހާ ވިއްޔާ', 'އަޅުގަނޑު ވަރަށް ހަމަ ޖެހިގެން މިހިރިީ']

# Load JSONs
def load_json(files):
	global json_files
	for file_name in files:
		json_file = open(f'./JSON/{file_name}.json')
		json_files[file_name] = json.load(json_file)

load_json(file_names)

# Utilities
def get_param(text):
	if len(text.strip().split(' ')) > 1: return text.split(' ', 1)[1].lower().strip()

def get_times(day, out_msg):
	if not day: return '<b>ތަންކޮޅެއް ހަމަޖެހޭ އެއްޗެއް ލިޔަން ދަސްކޮށްބަ</b>'
	out_msg += f'<b>{day.upper()}\n</b>'
	if len(json_files['TimeTable'][day]) == 0: return out_msg + 'ކަލޯ ނެތޭ ކުލާހެއް ފެންނާކަށް'

	count = 0
	for details in json_files['TimeTable'][day]:
		for item in details:
			key = f'{details["subject"]}-{day}-{details["time"][0]}'
			if details[item] != "" and key not in cancelled:
				count += 1
				if item == 'subject':
					out_msg += f'<i>{json_files["Subjects"][details[item]]}:</i>'
					continue
				elif item == 'time':
					out_msg += f' {details[item][0]} - {details[item][1]}\n'
					continue
				out_msg += f'{details[item]}\n'
	if count == 0: return out_msg + 'ކަލޯ ނެތޭ ކުލާހެއް ފެންނާކަށް' 
	return out_msg + '\n'

def autocorrect_day(param):
	days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
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
@bot.message_handler(commands=['hamajehey'])
def end_bot(message):
	bot.reply_to(message, hamajehey[random.randint(0, len(hamajehey) - 1)])

@bot.message_handler(commands=['table'])
def send_timetable(message):
	out_msg = ''
	param = get_param(message.text)
	print(message)
	
	if param == 'all':
		for day in json_files['TimeTable']:
			if len(json_files['TimeTable'][day]) == 0: continue
			out_msg = get_times(day, out_msg)
	else:
		if not param: param = datetime.today().strftime('%A').lower()
		elif param not in json_files['TimeTable']: param = autocorrect_day(param)
		out_msg = get_times(param, out_msg)
	bot.reply_to(message, out_msg, disable_web_page_preview=True)

@bot.message_handler(commands=['end'])
def end_bot(message):
	if str(message.from_user.id) not in admin_ids:
		bot.reply_to(message, '<b>މަނޫޅެން ކައޭ ބުނާ ކަމެއް ކުރާކަށް</b>')
		return
	for grp_id in grp_ids:
		bot.send_message(grp_id, '<b>މަ މިދިޔައީ ނިދަން، ވަރަށް ސަލާން</b>')
	os._exit(0)

@bot.message_handler(commands=['cancel'])
def cancel_alert(message):
	param = get_param(message.text).split(' ')
	if not param or len(param) != 3:
		bot.reply_to(message, '<b>ތަންކޮޅެއް ހަމަޖެހޭ އެއްޗެއް ލިޔަން ދަސްކޮށްބަ</b>')
		return

	key = f'{param[0].upper()}-{autocorrect_day(param[1])}-{param[2]}'
	if key not in scheduled or len(scheduled[key]) == 0:
		bot.reply_to(message, '<b>ތި ބުނި ކުލާހެއް ހޯދޭނީ ކައެޔަށް އެކަނި</b>')
		return

	for item in scheduled[key]:
		schedule.cancel_job(item)
		cancelled.append(key)
	bot.reply_to(
		message,
		f'<b>{json_files["Subjects"][param[0].upper()]} class on {autocorrect_day(param[1])} at {param[2]} has been cancelled</b>'
	)

# Set Scheduler and Alerts
def send_alert(details, title, msg):
	for grp_id in grp_ids:
		out_msg = f'{msg}\n'
		for item in details:
			if item == 'time' or item == 'subject' or details[item] == '': continue
			out_msg += f'{details[item]}\n'
		bot.send_message(grp_id, f'<b>{title}</b>\n<i>{out_msg}', disable_web_page_preview=True)
	return schedule.CancelJob

def set_scheduler():
	# clear scheduled tasks
	global scheduled
	scheduled = {}
	cancelled = []
	schedule.clear()

	# set_before is in minutes
	set_before = 30
	
	for day in json_files['TimeTable']:
		if len(json_files['TimeTable'][day]) != 0:
			for details in json_files['TimeTable'][day]:
				time = details["time"][0]
				key = f'{details["subject"]}-{day}-{time}'
				subj_name = json_files["Subjects"][details["subject"]]
				scheduled[key] = []
				# class starting alert
				scheduled[key].append(getattr(schedule.every(), day).at(time).do(
					send_alert, details, 'Attention', f'{subj_name}</i> has started'
				))
				# class reminders
				scheduled[key].append(getattr(schedule.every(), day).at(calc_time(time, set_before)).do(
					send_alert, details, 'Reminder', f'{subj_name}</i> will start at {time}'
				))

# Create all the needed schedules for the week
schedule.every().thursday.at("00:00").do(set_scheduler)

def run_scheduler():
	set_scheduler()
	while True:
		idle_time = schedule.idle_seconds()
		time.sleep(idle_time)
		schedule.run_pending()

# Running bot
threading.Thread(target=run_scheduler).start()
threading.Thread(target=bot.polling).start()