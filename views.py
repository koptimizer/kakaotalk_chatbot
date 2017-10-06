from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse

from main.models import User
from main.models import Response

import json

@csrf_exempt
def message(request):

    if request.method == 'POST':
        request_data = ((request.body).decode('utf-8'))
        request_data = json.loads(request_data)
        userMessage = request_data['content']
        user_key = request_data['user_key']

    user = User.getOrCreate(user_key)

    text = Response.getResponseText(user, userMessage)

    testResult = json.dumps({'message' : {'text' : text}})

    return HttpResponse(testResult)

def keyboard(request):
    result = json.dumps({'type' : 'text'})
    return HttpResponse(result)
