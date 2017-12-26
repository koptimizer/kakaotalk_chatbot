import importlib

from . import keys
from . import busMod
from . import metroMod # 이거때문에 시간표가 꼬임..
from . import sunfoodMod
from . import kpuwatchMod

import urllib.request
import urllib.parse
import json
import re

from bs4 import BeautifulSoup
import random
import requests

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
            #botText = Shuttle.getShuttleText('학교', '정왕역') + '\n' + Shuttle.getShuttleText('학교', '오이도역') + '\n' + metroMod.getMetroText('정왕') + '\n' + busMod.getBusText('시흥시외버스터미널')
            #botText = Shuttle.getShuttleText('학교', '정왕역') + '\n' + Shuttle.getShuttleText('학교', '오이도역') + '\n' + metroMod.getMetroText('정왕') 
            #botText = Shuttle.getShuttleText('학교', '정왕역') + '\n' + Shuttle.getShuttleText('학교', '오이도역') + '\n' + Shuttle.getShuttleText('시화터미널', '강남역', ' 3400번 광역버스')  + '\n' + metroMod.getMetroText('정왕')
            botText = Shuttle.getShuttleText('학교', '정왕역') + '\n' + Shuttle.getShuttleText('학교', '오이도역') + '\n' + Shuttle.getShuttleText('시화터미널', '강남역', ' 3400번 광역버스')
        elif re.search('오이도역?\s?[(셔틀)(버스)]', userMessage) or re.search('ㅇㅇㄷ', userMessage):
            botText = Shuttle.getShuttleText('오이도역', '학교')
        else:
            botText = '셔틀/지하철 도착시간을 알고싶으시다면..\n\'정왕셔틀\'(ㅈㅇㅅㅌ),\n\'학교셔틀\'(ㅎㄱㅅㅌ),\n\'오이도셔틀\'(ㅇㅇㄷㅅㅌ),\n\'정왕역\'(ㅈㅇㅇ)\n이라고 물어보세요!'
        return textMessage(botText)

    elif response.func == 'sunfood':
        menuDict = sunfoodMod.getMenuDict()
        botText = '오늘 선푸드 메뉴를 알려드릴게요!'
        botText += '\n\n' + '[조식]' + menuDict['breakfast']
        botText += '\n\n' + '[중식]' + menuDict['lunch']
        botText += '\n\n' + '[석식]' + menuDict['dinner']
        return textMessage(botText)

    elif response.func == '산대전':
        return linkMessage('산대전 제보함으로 연결해드릴게요!', '산대전 제보함', 'http://kpu.fbpage.kr/#/submit')

    elif response.func == 'kpuwatch':
        messageList = eval(user.getMessageList())
        userMessage = messageList.pop()
        typeMessage = messageList.pop() # '교수검색' or '강의검색'

        resultText = kpuwatchMod.getKPUWatchText(typeMessage, userMessage)
        if resultText:
            return linkMessage(resultText, 'KPUWatch에서 보기', 'http://kpuwatch.com/bbs/search.php?url=http%3A%2F%2Fkpuwatch.com%2Fbbs%2Fsearch.php&stx=' + userMessage)
        else:
            return textMessage('원하는 검색결과가 없어요! ㅜㅜ')

        '''
        if re.search('강의', typeMessage):
            url = 'http://kpuwatch.com/rating_search.php?subject=' + userMessage
        elif re.search('교수', typeMessage):
            url = 'http://kpuwatch.com/rating_search.php?professor=' + userMessage

        req = requests.get(url)

        bs = BeautifulSoup(req.text, 'html.parser')
        contentList = bs.find_all('content')

        if contentList:
            rd = random.randrange(0, len(contentList))
            resultText = '* KPUWatch에서 찾아봤어요!\n\n' + contentList[rd].text
            return linkMessage(resultText, 'KPUWatch에서 보기', 'http://kpuwatch.com/bbs/search.php?url=http%3A%2F%2Fkpuwatch.com%2Fbbs%2Fsearch.php&stx=' + userMessage)
        else:
            return textMessage('원하는 검색결과가 없어요..ㅠㅠ')
        '''


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

    elif response.func == 'now_feed':
        messageList = eval(user.getMessageList())
        userMessage = messageList.pop()
        url = 'https://iqmbe7m049.execute-api.ap-northeast-2.amazonaws.com/test/feed'
        resp = requests.get(url)
        return textMessage('밥 맥였따~')

    elif response.func == 'set_resv_feed':
        messageList = eval(user.getMessageList())
        userMessage = messageList.pop()
        p = re.compile('(\d\d?)시\s?(\d\d?)분')

        feedtimeList = list()
        for item in p.findall(userMessage): # 여러개의 튜플들
            item_0 = item[0]
            item_1 = item[1]
            if len(item[0]) == 1:
                item_0 = '0' + item[0]
            if len(item[1]) == 1:
                item_1 = '0' + item[1]
            feedtimeList.append(item_0 + ':' + item_1)

        url = 'https://iqmbe7m049.execute-api.ap-northeast-2.amazonaws.com/test/reserved-feed'

        # requests 모듈로 도전
        data = {'device_num' : '1', 'feedtime' : feedtimeList}

        resp = requests.put(url, data=json.dumps(data), headers={'Content-Type':'application/json'})
        respDict = eval(resp.text)
        respDictf = stringFormatConvert(respDict)
        return textMessage('아래 시간으로 설정되었습니다.\n{}'.format(respDictf))

    elif response.func == 'get_resv_feed':
        url = 'https://iqmbe7m049.execute-api.ap-northeast-2.amazonaws.com/test/reserved-feed'
        resp = requests.get(url)
        respDict = eval(resp.text)
        respDictf = stringFormatConvert(respDict)
        return textMessage('현재 아래와 같이 설정되어있습니다.\n{}'.format(respDictf))

    elif response.func == 'get_condition':
        url = 'https://iqmbe7m049.execute-api.ap-northeast-2.amazonaws.com/test/reserved-feed'
        resp = requests.get(url)
        respDict = eval(resp.text)
        temperature = respDict['state']['reported'].get('temperature')
        humidity = respDict['state']['reported'].get('humidity')
        #respDictf = stringFormatConvert(respDict)
        return textMessage('현재 온도는 {0:0.1f}*,\n습도는 {1:0.1f}%'.format(temperature, humidity))

def linkMessage(botText, label, url):
    return {'message' : {'text' : botText, 'message_button' : {'label' : label, 'url' : url}}}

def textMessage(botText):
    return {'message' : {'text' : botText}}

def stringFormatConvert(respDict):
    return respDict['state']['desired']['feedtime']
