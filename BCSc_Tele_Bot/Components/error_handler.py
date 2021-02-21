import random

class ErrorHandler:
    def __init__(self):
        self.access = "<b>މަނޫޅެން ކައޭ ބުނާ ކަމެއް ކުރާކަށް</b>"
        self.invalid = "<b>ތަންކޮޅެއް ހަމަޖެހޭ އެއްޗެއް ލިޔަން ދަސްކޮށްބަ</b>"
        self.invalid_class = "<b>ތި ބުނި ކުލާހެއް ހޯދޭނީ ކައެޔަށް އެކަނި</b>"
        self.missing_class = "<b>ކުލާހެއްގެ ނަމެއް ކިޔާބަ ނޫނީ އެވެސް މަތަ ހޯދަން ޖެހެނީ؟</b>"
        self.no_class = "<b>....މީ ކިޔަވާ މާެއްދާ އެއްތަ؟</b>"
        self.something = "<b>ހެހެހެ، ކޮންމެސް ކަމެއް ވެއްޖެ، ނޭނގޭ ވީ ކަމެއް</b>"
