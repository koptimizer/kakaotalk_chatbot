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

    start = datetime.datetime.now()
    botMessageDict = Response.getResponseDict(user, userMessage)
    timeDiff = datetime.datetime.now() - start

    numOfMails = Mail.getNumOfMails(user)
    if numOfMails:
        botMessageDict['message']['text'] = '[' + str(numOfMails) + '개의 메시지]\n\n' + botMessageDict['message']['text']

    Log.write(user, userMessage, botMessageDict['message']['text'], timeDiff.total_seconds())

    botMessageDumped = json.dumps(botMessageDict)

    return HttpResponse(botMessageDumped)

def keyboard(request):
    result = json.dumps({'type' : 'text'})
    return HttpResponse(result)
