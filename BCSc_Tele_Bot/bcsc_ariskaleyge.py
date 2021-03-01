import os
import telebot
import threading
from Components.utilities import *
from Components.hamajehey import Hamajehey
from Components.scheduler import Scheduler
from Components.error_handler import ErrorHandler
from Components.table_manager import TableManager

# Bot API
key = open('./Keys/.key').read()
bot = telebot.TeleBot(key, parse_mode='html')

# Initiating Keys
grp_ids = open('./Keys/.groups').read().split(',')
admin_ids = open('./Keys/.admins').read().split(',')

# Initiate Variables
error = ErrorHandler()
table = TableManager()
hamajehey = Hamajehey()

# Initiating Scheduler
alerts = Scheduler(30, bot, grp_ids)

# Main Bot Commands
@bot.message_handler(commands=['table'])
def timetable_handler(message):
	param = get_param(message.text)
	out_msg = table.send_timetable(param)
	bot.reply_to(message, out_msg, disable_web_page_preview=True)

@bot.message_handler(commands=['cancel'])
def cancel_handler(message):
	param = get_param(message.text)
	out_msg, markup = table.initiate_cancel(param)
	bot.send_message(message.chat.id, out_msg, reply_markup=markup)

@bot.message_handler(commands=['hamajehey'])
def hamajehey_handler(message):
	out_msg = hamajehey.send_reply()
	bot.reply_to(message, out_msg)

@bot.callback_query_handler(func=lambda call: True)
def call_handler(call):
	out_msg = table.confirm_cancel(call.data, alerts)
	bot.edit_message_text(out_msg, call.message.chat.id, call.message.id)

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