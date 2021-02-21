import os
import time
import random
import telebot
import schedule
import threading
from telebot import types
from Components.utilities import *
from Components.error_handler import *
from Components.table_manager import *

# Bot API
key = open('./Keys/.key').read()
bot = telebot.TeleBot(key, parse_mode='html')

# Variables
scheduled = {}
error = ErrorHandler()
table = TableManager()
subjects = load_json('Subjects')
grp_ids = open('./Keys/.groups').read().split(',')
admin_ids = open('./Keys/.admins').read().split(',')
hamajehey = ['ނޫޅެން', 'ކައޭ ޖެހިބަ އަޖައިބެއް ނުން', 'ހަމަ ހުވާތަ', 'ހެހެ ވިސްނާލާނަން', 'ތީ އެންމެ މައިތިރި މީހާ ވިއްޔާ', 'އަޅުގަނޑު ވަރަށް ހަމަ ޖެހިގެން މިހިރިީ']

# Main Commands
def cancel_markup(subject):
	markup = types.InlineKeyboardMarkup()
	days = []
	markup.row_width = 1
	for day in table.all:
		for schedule in table.all[day]:
			if schedule["subject"] == subject.upper(): days.append(day)
	if len(days) == 0: return None
	markup.add(types.InlineKeyboardButton('All', callback_data=f"{subject.upper()}-all"))
	for day in days:
		markup.add(types.InlineKeyboardButton(day.capitalize(), callback_data=f"{subject.upper()}-{day}"))
	return markup

@bot.message_handler(commands=['cancel'])
def cancel_menu(message):
	param = get_param(message.text)
	if not param:
		bot.reply_to(message, error.missing_class)
		return
	if not isSubject(param, subjects):
		bot.reply_to(message, error.invalid_class)
		return
	markup = cancel_markup(param)
	if not markup: bot.send_message(message.chat.id, error.no_class)
	else: bot.send_message(message.chat.id, f"Which classes of {param.upper()} do you want to cancel?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def cancel_class(call):
	cancel = False
	call_data = call.data.split('-')
	param = call.data
	if call_data[1] == 'all': param = call_data[0]
	for data in scheduled:
		if param in data:
			for item in scheduled[data]:
				schedule.cancel_job(item)
			table.cancelled.append(data)
			cancel = True
	if cancel: bot.edit_message_text(f'The requested classes for {call_data[0]} have been cancelled', call.message.chat.id, call.message.id)
	else: bot.edit_message_text(error.something, call.message.chat.id, call.message.id)

@bot.message_handler(commands=['hamajehey'])
def end_bot(message):
	bot.reply_to(message, hamajehey[random.randint(0, len(hamajehey) - 1)])

@bot.message_handler(commands=['table'])
def timetable_handler(message):
	param = get_param(message.text)
	out_msg = table.send_timetable(param)
	bot.reply_to(message, out_msg, disable_web_page_preview=True)

@bot.message_handler(commands=['end'])
def end_bot(message):
	if str(message.from_user.id) not in admin_ids:
		bot.reply_to(message, error.access)
		return
	for grp_id in grp_ids:
		bot.send_message(grp_id, '<b>މަ މިދިޔައީ ނިދަން، ވަރަށް ސަލާން</b>')
	os._exit(0)


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
	
	for day in table.all:
		if len(table.all[day]) != 0:
			for details in table.all[day]:
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