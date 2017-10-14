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

        botMessage = '\'' + userMessage + '\'\n메시지가 전달되었습니다!'
        return botMessage

    elif response.func == 'readMail': # admin만 호출 가능
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

    elif response.func == '교통':
        Shuttle = getattr(importlib.import_module('main.models'), 'Shuttle')

        messageList = eval(user.getMessageList())
        userMessage = messageList.pop()

        if re.search('정왕역?\s?[(셔틀)(버스)]', userMessage) or re.search('ㅈㅇㅇ?[ㅄ(ㅂㅅ)(ㅅㅌ)]', userMessage):
            return Shuttle.getShuttleText('정왕역', '학교') + '\n\n' + busMod.getBusText('정왕역환승센터')
        elif re.search('학교\s?[(셔틀)(버스)]', userMessage) or re.search('ㅎㄱ[ㅄ(ㅂㅅ)(ㅅㅌ)]', userMessage):
            return Shuttle.getShuttleText('학교', '정왕역') + '\n\n' + Shuttle.getShuttleText('학교', '오이도역') + '\n\n' + metroMod.getMetroText('정왕')
        elif re.search('오이도역?\s?[(셔틀)(버스)]', userMessage) or re.search('ㅇㅇㄷㅇ?[ㅄ(ㅂㅅ)(ㅅㅌ)]', userMessage):
            return Shuttle.getShuttleText('오이도역', '학교')
        elif userMessage == '정왕역' or userMessage == 'ㅈㅇㅇ':
            return metroMod.getMetroText('정왕')
        else:
            return '셔틀 도착시간을 알고싶으시다면..\n\'정왕셔틀\'(ㅈㅇㅅㅌ),\n\'학교셔틀\'(ㅎㄱㅅㅌ),\n\'오이도셔틀\'(ㅇㅇㄷㅅㅌ)\n이라고 물어보세요!'

    elif response.func == 'sunfood':
        menuDict = sunfoodMod.getMenuDict()
        botMessage = '오늘 선푸드 메뉴를 알려드릴께요!'
        botMessage += '\n\n' + '[조식]' + menuDict['breakfast']
        botMessage += '\n\n' + '[중식]' + menuDict['lunch']
        botMessage += '\n\n' + '[석식]' + menuDict['dinner']
        return botMessage
