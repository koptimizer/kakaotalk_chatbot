from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse

from main.models import User
from main.models import Response
from main.models import Log

import json

@csrf_exempt
def message(request):

    if request.method == 'POST':
        request_data = ((request.body).decode('utf-8'))
        request_data = json.loads(request_data)
        userMessage = request_data['content']
        user_key = request_data['user_key']

    user = User.getOrCreate(user_key)

    botMessage = Response.getResponseText(user, userMessage)

    Log.write(user, userMessage, botMessage)

    botMessageDumped = json.dumps({'message' : {'text' : botMessage}})

    return HttpResponse(botMessageDumped)

def keyboard(request):
    result = json.dumps({'type' : 'text'})
    return HttpResponse(result)
