TIMER = 600
SERVER = 'localhost'
DIR = '' # must exist and must have right to read/write
ACCOUNTS = []
with open(DIR + 'accounts.txt', 'r') as html:
    ACCOUNTS = html.readlines()

HASHTAG = ['framasoft', 'urlab']
PICS = False

account = False
