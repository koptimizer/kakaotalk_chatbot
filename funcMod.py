import importlib

from . import keys
from . import busMod
from . import metroMod # 이거때문에 시간표가 꼬임..
from . import sunfoodMod

import urllib.request
import urllib.parse
import json
import re

# 각종 함수를 매핑시키기 위한 함수
def getFuncMessage(user, response):

    if response.func == 'sendMail':
        User = getattr(importlib.import_module('main.models'), 'User')
        Mail = getattr(importlib.import_module('main.models'), 'Mail')

        messageList = eval(user.getMessageList())
        userMessage = messageList.pop()

        admin = User.getByGroup('admin')
        Mail.sendMail(user, admin, userMessage)

        botText = '\'' + userMessage + '\'\n메시지가 전달되었습니다!'
        return textMessage(botText)

    elif response.func == 'readMail': # admin만 호출 가능
        Mail = getattr(importlib.import_module('main.models'), 'Mail')
        botText = Mail.readMail(user)
        return textMessage(botText)

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
        botText = dict['message']['result']['translatedText']
        return textMessage(botText)

    elif response.func == '교통':
        Shuttle = getattr(importlib.import_module('main.models'), 'Shuttle')

        messageList = eval(user.getMessageList())
        userMessage = messageList.pop()

        if userMessage == '정왕역' or userMessage == 'ㅈㅇㅇ':
            botText = metroMod.getMetroText('정왕')
        elif re.search('정왕역?\s?[(셔틀)(버스)]', userMessage) or re.search('ㅈㅇ', userMessage):
            botText = Shuttle.getShuttleText('정왕역', '학교') + '\n' + busMod.getBusText('정왕역환승센터')
        elif re.search('학교\s?[(셔틀)(버스)]', userMessage) or re.search('ㅎㄱ', userMessage):
            botText = Shuttle.getShuttleText('학교', '정왕역') + '\n' + Shuttle.getShuttleText('학교', '오이도역') + '\n' + metroMod.getMetroText('정왕')
        elif re.search('오이도역?\s?[(셔틀)(버스)]', userMessage) or re.search('ㅇㅇㄷ', userMessage):
            botText = Shuttle.getShuttleText('오이도역', '학교')
        else:
            botText = '셔틀/지하철 도착시간을 알고싶으시다면..\n\'정왕셔틀\'(ㅈㅇㅅㅌ),\n\'학교셔틀\'(ㅎㄱㅅㅌ),\n\'오이도셔틀\'(ㅇㅇㄷㅅㅌ),\n\'정왕역\'(ㅈㅇㅇ)\n이라고 물어보세요!'
        return textMessage(botText)

    elif response.func == 'sunfood':
        menuDict = sunfoodMod.getMenuDict()
        botText = '오늘 선푸드 메뉴를 알려드릴께요!'
        botText += '\n\n' + '[조식]' + menuDict['breakfast']
        botText += '\n\n' + '[중식]' + menuDict['lunch']
        botText += '\n\n' + '[석식]' + menuDict['dinner']
        return textMessage(botText)

    elif response.func == '산대전':
        return linkMessage('산대전 제보함으로 연결해드릴께요!', '산대전 제보함', 'http://kpu.fbpage.kr/#/submit')

    elif response.func == 'kpuwatch':
        messageList = eval(user.getMessageList())
        userMessage = messageList.pop()
        return linkMessage('KPUWatch로 연결해드릴께요!', userMessage, 'http://kpuwatch.com/bbs/search.php?url=http%3A%2F%2Fkpuwatch.com%2Fbbs%2Fsearch.php&stx=' + userMessage)

    elif response.func == 'on':
        url = 'https://iqmbe7m049.execute-api.ap-northeast-2.amazonaws.com/test/led/on'
        request = urllib.request.Request(url)
        request.add_header("x-api-key", keys.api_gateway)
        response = urllib.request.urlopen(request)
        return textMessage('불을 켰다!')

    elif response.func == 'off':
        url = 'https://iqmbe7m049.execute-api.ap-northeast-2.amazonaws.com/test/led/off'
        request = urllib.request.Request(url)
        request.add_header("x-api-key", keys.api_gateway)
        response = urllib.request.urlopen(request)
        return textMessage('불을 껐다!')

def linkMessage(botText, label, url):
    return {'message' : {'text' : botText, 'message_button' : {'label' : label, 'url' : url}}}

def textMessage(botText):
    return {'message' : {'text' : botText}}

