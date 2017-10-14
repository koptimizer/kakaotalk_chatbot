from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse

from main.models import User
from main.models import Response
from main.models import Log
from main.models import Mail

import json
import datetime

@csrf_exempt
def message(request):

    if request.method == 'POST':
        request_data = ((request.body).decode('utf-8'))
        request_data = json.loads(request_data)
        userMessage = request_data['content']
        user_key = request_data['user_key']

    user = User.getOrCreate(user_key)

    numOfMails = Mail.getNumOfMails(user)
    if numOfMails:
        botMessage = '[' + str(numOfMails) + '개의 메시지]\n'
    else:
        botMessage = ''

    start = datetime.datetime.now()
    botMessage += Response.getResponseText(user, userMessage)
    timeDiff = datetime.datetime.now() - start

    Log.write(user, userMessage, botMessage, timeDiff.total_seconds())

    botMessageDumped = json.dumps({'message' : {'text' : botMessage}})

    return HttpResponse(botMessageDumped)

def keyboard(request):
    result = json.dumps({'type' : 'text'})
    return HttpResponse(result)
