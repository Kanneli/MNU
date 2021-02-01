import telebot
import json
from datetime import datetime

# Bot API
key = open('.key').read()
bot = telebot.TeleBot(key, parse_mode='MarkdownV2')

# Variables
timetable = []
subjects = {}

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
		out_msg = get_times(param, out_msg)

	bot.reply_to(message, out_msg)

bot.polling()