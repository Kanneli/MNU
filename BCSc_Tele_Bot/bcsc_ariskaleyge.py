import os
import time
import random
import telebot
import schedule
import threading
from datetime import datetime
from Components.utilities import *
from Components.error_handler import *

# Bot API
key = open('./Keys/.key').read()
bot = telebot.TeleBot(key, parse_mode='html')

# Variables
scheduled = {}
cancelled = []
error = ErrorHandler()
timetable = load_json('TimeTable')
subjects = load_json('Subjects')
grp_ids = open('./Keys/.groups').read().split(',')
admin_ids = open('./Keys/.admins').read().split(',')
hamajehey = ['ނޫޅެން', 'ކައޭ ޖެހިބަ އަޖައިބެއް ނުން', 'ހަމަ ހުވާތަ', 'ހެހެ ވިސްނާލާނަން', 'ތީ އެންމެ މައިތިރި މީހާ ވިއްޔާ', 'އަޅުގަނޑު ވަރަށް ހަމަ ޖެހިގެން މިހިރިީ']

# Main Commands
@bot.message_handler(commands=['hamajehey'])
def end_bot(message):
	bot.reply_to(message, hamajehey[random.randint(0, len(hamajehey) - 1)])

@bot.message_handler(commands=['table'])
def send_timetable(message):
	out_msg = ''
	param = get_param(message.text)
	
	if param == 'all':
		for day in timetable:
			if len(timetable[day]) == 0: continue
			out_msg = get_times(day, out_msg, timetable, subjects, cancelled)
	else:
		if not param: param = datetime.today().strftime('%A').lower()
		elif param not in timetable: param = autocorrect_day(param)
		out_msg = get_times(param, out_msg, timetable, subjects, get_times)
	bot.reply_to(message, out_msg, disable_web_page_preview=True)

@bot.message_handler(commands=['end'])
def end_bot(message):
	if str(message.from_user.id) not in admin_ids:
		bot.reply_to(message, error.access)
		return
	for grp_id in grp_ids:
		bot.send_message(grp_id, '<b>މަ މިދިޔައީ ނިދަން، ވަރަށް ސަލާން</b>')
	os._exit(0)

@bot.message_handler(commands=['cancel'])
def cancel_alert(message):
	param = get_param(message.text)
	if not param:
		bot.reply_to(message, error.invalid_class)
		return
	elif len(param) != 3:
		bot.reply_to(message, error.invalid)
		return


	param = param.split(' ')
	key = f'{param[0].upper()}-{autocorrect_day(param[1])}-{param[2]}'
	if key not in scheduled or len(scheduled[key]) == 0:
		bot.reply_to(message, error.invalid_class)
		return

	for item in scheduled[key]:
		schedule.cancel_job(item)
		cancelled.append(key)
	bot.reply_to(
		message,
		f'<b>{subjects[param[0].upper()]} class on {autocorrect_day(param[1])} at {param[2]} has been cancelled</b>'
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
	
	for day in timetable:
		if len(timetable[day]) != 0:
			for details in timetable[day]:
				time = details["time"][0]
				key = f'{details["subject"]}-{day}-{time}'
				subj_name = subjects[details["subject"]]
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