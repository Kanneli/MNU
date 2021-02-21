import json

def load_json(file):
    data = open(f'./JSON/{file}.json')
    json_data = json.load(data)
    return json_data

def get_param(text):
	if len(text.strip().split(' ')) > 1: return text.split(' ', 1)[1].lower().strip()

def isSubject(subject, subjects):
	if subject.upper() in subjects: return True

def get_times(day, out_msg, timetable, subjects, cancelled):
	if not day: return '<b>ތަންކޮޅެއް ހަމަޖެހޭ އެއްޗެއް ލިޔަން ދަސްކޮށްބަ</b>'
	out_msg += f'<b>{day.upper()}\n</b>'
	if len(timetable[day]) == 0: return out_msg + 'ކަލޯ ނެތޭ ކުލާހެއް ފެންނާކަށް' + '\n'

	count = 0
	for details in timetable[day]:
		for item in details:
			key = f'{details["subject"]}-{day}-{details["time"][0]}'
			if details[item] != "" and key not in cancelled:
				count += 1
				if item == 'subject':
					out_msg += f'<i>{subjects[details[item]]}:</i>'
					continue
				elif item == 'time':
					out_msg += f' {details[item][0]} - {details[item][1]}\n'
					continue
				out_msg += f'{details[item]}\n'
	if count == 0: return out_msg + 'ކަލޯ ނެތޭ ކުލާހެއް ފެންނާކަށް' + '\n'
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