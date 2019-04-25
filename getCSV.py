import csv
from main.models import User
from main.models import Log
import re

with open('test.csv', 'w') as f:
    writer = csv.writer(f, delimiter = ',')
    writer.writerow(['test1'])
    writer.writerow(['test2'])

def getLogCSV():
    with open('log.csv', 'w') as f:
        fieldnames = ['', '']
        writer = csv.DictWriter(f, fieldnames = fieldnames)

def getUsers():
    with open('./csv/users.csv', 'w') as f:
        fieldnames = ['user_key', 'user_name']
        writer = csv.DictWriter(f, fieldnames = fieldnames)
        writer.writeheader()
        for user in User.objects.all():
            writer.writerow({'user_key' : user.user_key,
                'user_name' : user.user_name})

def getLogs():
    with open('./csv/logs.csv', 'w') as f:
        fieldnames = ['user_key', 'user_name', 'userMessage', 'botMessage', 'dateTime']
        writer = csv.DictWriter(f, fieldnames = fieldnames)
        writer.writeheader()
        for log in Log.objects.all():
            userMessage = re.sub('\n', ' ', log.userMessage)
            userMessage = re.sub(',', ' ', userMessage)
            botMessage = re.sub('\n', ' ', log.botMessage)
            botMessage = re.sub(',', ' ', botMessage)
            data = {'user_key' : log.user.user_key,
                    'user_name' : log.user.user_name,
                    'userMessage' : userMessage,
                    'botMessage' : botMessage,
                    'dateTime' : log.dateTime}
            writer.writerow(data)
