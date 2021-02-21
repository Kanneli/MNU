import os
import time
import random
import telebot
import schedule
import threading
from telebot import types
from Components.utilities import *
from Components.scheduler import Scheduler
from Components.error_handler import ErrorHandler
from Components.table_manager import TableManager

# Bot API
key = open('./Keys/.key').read()
bot = telebot.TeleBot(key, parse_mode='html')

# Initiating Variables
scheduled = {}
error = ErrorHandler()
table = TableManager()
subjects = load_json('Subjects')
grp_ids = open('./Keys/.groups').read().split(',')
admin_ids = open('./Keys/.admins').read().split(',')
hamajehey = ['ނޫޅެން', 'ކައޭ ޖެހިބަ އަޖައިބެއް ނުން', 'ހަމަ ހުވާތަ', 'ހެހެ ވިސްނާލާނަން', 'ތީ އެންމެ މައިތިރި މީހާ ވިއްޔާ', 'އަޅުގަނޑު ވަރަށް ހަމަ ޖެހިގެން މިހިރިީ']

# Initiating Scheduler
alerts = Scheduler(30, bot, grp_ids)

# Main Bot Commands
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

@bot.message_handler(commands=['table'])
def timetable_handler(message):
	param = get_param(message.text)
	out_msg = table.send_timetable(param)
	bot.reply_to(message, out_msg, disable_web_page_preview=True)

@bot.message_handler(commands=['hamajehey'])
def end_bot(message):
	bot.reply_to(message, hamajehey[random.randint(0, len(hamajehey) - 1)])

@bot.message_handler(commands=['end'])
def end_bot(message):
	if str(message.from_user.id) not in admin_ids:
		bot.reply_to(message, error.access)
		return
	for grp_id in grp_ids:
		bot.send_message(grp_id, '<b>މަ މިދިޔައީ ނިދަން، ވަރަށް ސަލާން</b>')
	os._exit(0)

# Scheduler Thread
threading.Thread(target=alerts.run_scheduler, args=(table.all, table.subjects)).start()
# Bot Polling Thread
threading.Thread(target=bot.polling).start()