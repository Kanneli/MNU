import telebot
import json

# Bot API
bot = telebot.TeleBot("", parse_mode='MarkdownV2')

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

def get_param(text):
	if len(text.split(' ')) > 1: return text.split(' ')[1].lower().strip()

def autocorrect_day(param):
	days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday']
	if param != 'day' and len(param) >= 3:
		for day in days:
			if param in day: return day

get_timetable()
get_subjects()

@bot.message_handler(commands=['table'], )
def send_welcome(message):
	out_msg = ''
	param = get_param(message.text)
	
	if param:
		param = autocorrect_day(param)
		if param not in timetable: out_msg = '*Invalid Param*'
		else:
			out_msg += f'*{param.capitalize()}*\n'
			for subject in timetable[param]: out_msg += f'_{subjects[subject]}_: {timetable[param][subject][0]} \- {timetable[param][subject][1]}\n'
			out_msg += '\n'
	else:
		for day in timetable:
			if len(timetable[day]) == 0: continue
			out_msg += f'*{day.capitalize()}*\n'
			for subject in timetable[day]: out_msg += f'_{subjects[subject]}_: {timetable[day][subject][0]} \- {timetable[day][subject][1]}\n'
			out_msg += '\n'

	bot.reply_to(message, out_msg)

bot.polling()