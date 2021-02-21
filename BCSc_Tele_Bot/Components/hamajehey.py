import random

class Hamajehey:
    def __init__(self):
        self.replies = ['ނޫޅެން', 'ކައޭ ޖެހިބަ އަޖައިބެއް ނުން', 'ހަމަ ހުވާތަ', 'ހެހެ ވިސްނާލާނަން', 'ތީ އެންމެ މައިތިރި މީހާ ވިއްޔާ', 'އަޅުގަނޑު ވަރަށް ހަމަ ޖެހިގެން މިހިރިީ']
        self.no_replies = len(self.replies)
    def send_reply(self):
        return self.replies[random.randint(0, self.no_replies - 1)]