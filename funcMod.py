import importlib

from . import keys
from . import busMod
from . import metroMod # 이거때문에 시간표가 꼬임..
from . import shuttleMod

import urllib.request
import urllib.parse
import json

# 각종 함수를 매핑시키기 위한 함수
def getFuncMessage(user, response):

    if response.func == 'sendMail':
        User = getattr(importlib.import_module('main.models'), 'User')
        Mail = getattr(importlib.import_module('main.models'), 'Mail')

        messageList = eval(user.getMessageList())
        userMessage = messageList.pop()

        admin = User.getByGroup('admin')
        Mail.sendMail(user, admin, userMessage)

        botMessage = '\'' + userMessage + '\'\n메시지가 전달되었습니다!'
        return botMessage

    elif response.func == 'readMail':
        # admin만 호출 가능
        Mail = getattr(importlib.import_module('main.models'), 'Mail')
        return Mail.readMail(user)

    elif response.func == 'papago':
        messageList = eval(user.getMessageList())
        userMessage = messageList.pop()

        encText = urllib.parse.quote(userMessage)
        data = "source=en&target=ko&text=" + encText
        url = "https://openapi.naver.com/v1/papago/n2mt"
        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", keys.naver_client_id)
        request.add_header("X-Naver-Client-Secret", keys.naver_client_secret)
        response = urllib.request.urlopen(request, data = data.encode("utf-8"))
        rescode = response.getcode()

        if(rescode == 200):
            response_body = response.read()
            #print(response_body.decode('utf-8'))

        else:
            print("Error Code:" + rescode)

        dict = json.loads(response_body.decode('utf-8'))
        text = dict['message']['result']['translatedText']
        return text

    elif response.func == 'shuttle':
        messageList = eval(user.getMessageList())
        userMessage = messageList.pop()

        if userMessage == '정왕셔틀':
            return shuttleMod.buildText('JWToUniv') + '\n\n' + busMod.getBusText()
        elif userMessage == '학교셔틀':
            return shuttleMod.buildText('UnivToJW') + '\n\n' + shuttleMod.buildText('UnivToOido')
        elif userMessage == '오이도셔틀':
            return shuttleMod.buildText('OidoToUniv')
        else:
            return '\'정왕셔틀\',\n\'학교셔틀\',\n\'오이도셔틀\'\n이라고 물어보세요!'
