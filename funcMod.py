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

import datetime

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

    elif response.func == 'sendMail_admin':
        User = getattr(importlib.import_module('main.models'), 'User')
        Mail = getattr(importlib.import_module('main.models'), 'Mail')

        messageList = eval(user.getMessageList())

        userMessage = messageList.pop()
        target_user_key = messageList.pop()

        target_user = User.getByKey(target_user_key)
        if not target_user:
            return textMessage('존재하지 않는 user_key')

        Mail.sendMail(user, target_user, userMessage)

        botText = '\'' + userMessage + '\'\n메시지가 전달되었습니다!'
        return textMessage(botText)

    elif response.func == 'readMail': # admin만 호출 가능
        Mail = getattr(importlib.import_module('main.models'), 'Mail')
        botText = Mail.readMail(user)
        #botText = addButtonsToTextMessage(botText, ['Test1', 'Test2'])
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

        # 특정 일자는 셔틀버스 운영휴무 알림
        targetDates = ['2018-05-05', '2018-05-07', '2018-05-22']

        for targetDate in targetDates:
            if datetime.datetime.now().date() == datetime.datetime.strptime(targetDate, '%Y-%m-%d').date():
                isBreakDay = True
                break
            else:
                isBreakDay = False
        # 휴무 여부 확인 알고리즘 종료

        if userMessage == '정왕역' or userMessage == 'ㅈㅇㅇ':
            botText = metroMod.getMetroText('정왕')

        elif re.search('정왕역?\s?[(셔틀)(버스)]', userMessage) or re.search('ㅈㅇ', userMessage):
            botText = Shuttle.getShuttleText('정왕역', '학교') + '\n' + busMod.getBusText('정왕역환승센터')

            if isBreakDay:
                botText = '오늘 정왕역 셔틀은 운행 하지 않습니다'
                botText += '\n\n' + busMod.getBusText('정왕역환승센터')

        elif re.search('학교\s?[(셔틀)(버스)]', userMessage) or re.search('ㅎ[ㄱㄳ]', userMessage) or re.search('3400', userMessage):
            #botText = Shuttle.getShuttleText('학교', '정왕역') + '\n' + Shuttle.getShuttleText('학교', '오이도역') + '\n' + metroMod.getMetroText('정왕') + '\n' + busMod.getBusText('시흥시외버스터미널')
            #botText = Shuttle.getShuttleText('학교', '정왕역') + '\n' + Shuttle.getShuttleText('학교', '오이도역') + '\n' + metroMod.getMetroText('정왕') 
            #botText = Shuttle.getShuttleText('학교', '정왕역') + '\n' + Shuttle.getShuttleText('학교', '오이도역') + '\n' + Shuttle.getShuttleText('시화터미널', '강남역', ' 3400번 광역버스')  + '\n' + metroMod.getMetroText('정왕')
            botText = Shuttle.getShuttleText('학교', '정왕역') + '\n' + Shuttle.getShuttleText('학교', '오이도역') + '\n' + Shuttle.getShuttleText('시화터미널', '강남역', ' 3400번 광역버스')


            if isBreakDay:
                botText = '오늘 정왕역/오이도역 셔틀은 운행 하지 않습니다'
                botText += '\n\n' + Shuttle.getShuttleText('시화터미널', '강남역', '3400번 광역버스')

        elif re.search('오이도역?\s?[(셔틀)(버스)]', userMessage) or re.search('ㅇㅇㄷ', userMessage):
            botText = Shuttle.getShuttleText('오이도역', '학교')

            if isBreakDay:
                botText = '오늘 오이도역 셔틀은 운행 하지 않습니다'

        else:
            botText = '셔틀/지하철 도착시간을 알고싶으시다면..\n\'정왕셔틀\'(ㅈㅇㅅㅌ),\n\'학교셔틀\'(ㅎㄱㅅㅌ),\n\'오이도셔틀\'(ㅇㅇㄷㅅㅌ),\n\'정왕역\'(ㅈㅇㅇ)\n이라고 물어보세요!'
        return textMessage(botText)

    elif response.func == 'sunfood':
        Miga = getattr(importlib.import_module('main.models'), 'Miga')
        Semicon = getattr(importlib.import_module('main.models'), 'Semicon')
        menuDict = sunfoodMod.getMenuDict()

        today = datetime.datetime.now().date()

        botText = '{}월 {}일 오늘의 메뉴입니다!\n\n'.format(today.month, today.day)

        botText += '[TIP 선푸드]'
        botText += '\n' + '(조식)' + menuDict['breakfast']
        botText += '\n' + '(중식)' + menuDict['lunch']
        botText += '\n' + '(석식)' + menuDict['dinner']

        #botText += '\n\n[E동 식당]'
        #botText += '\nhttp://ibook.kpu.ac.kr/Viewer/YP7504RLX8E6'

        #botText += '[TIP 선푸드]'
        #botText += '\n' + '(조식)' + ' 쌀밥 참치김치찌개 떡갈비피망조림 계란찜 진미채야채무침 배추김치'
        #botText += '\n' + '(중식)' + ' 주먹밥 꼬치어묵우동 야채비빔만두 김가루 쪽파단무지무침 배추김치'
        #botText += '\n' + '(석식)' + ' 쌀밥 소고기국밥 어묵조림 양파쌈장무침 배추김치'

        #botText += '[TIP 선푸드]'
        #botText += '\n' + '(조식)' + ' 쌀밥 연두부팽이버섯국 닭볶음탕 느타리버섯볶음 오이무침 배추김치'
        #botText += '\n' + '(중식)' + ' 후리가케주먹밥 미역국 열무비빔국수 찐계란 음료수 배추김치'
        #botText += '\n' + '(석식)' + ' 쌀밥 미소된장국 샤워돈까스 양배추샐러드 매쉬드포테이토 볶음김치'

        if Miga.getMenu():
            botText += '\n\n' + '[미가식당]' + '\n' + Miga.getMenu()

        if Semicon.getMenu():
            botText += '\n\n' + '[세미콘식당] 11:30~1:40 / 4:30~6:30' + '\n' + Semicon.getMenu()

        #botText += '\n\n' + '"ㅁㄴ" 명령어로도 오늘의 메뉴를 알수있어요!'
        botText += '\n\n' + '* 각 외부식당 사장님이 직접 등록하므로 메뉴 업데이트가 지연될 수 있습니다'
        botText += '\n' + '* ㅁㄴ 명령어로도 메뉴를 알 수 있어요'

        return textMessage(botText)

    elif response.func == 'semicon':
        Semicon = getattr(importlib.import_module('main.models'), 'Semicon')
        messageList = eval(user.getMessageList())
        userMessage = messageList.pop()

        if not re.search('^\s?중식.+', userMessage):
            userMessage = '(중식) ' + userMessage

        userMessage = re.sub('^\s+중식\s+', '(중식) ', userMessage)

        userMessage = re.sub('\s+', ' ', userMessage)

        userMessage = re.sub('\s*[억석][십식]\s?', '\n(석식) ', userMessage)

        Semicon.createOrUpdateMenu(menu = userMessage)

        return textMessage('세미콘식당 메뉴가 등록되었습니다!\n문의 : 010-9269-2298')

    elif response.func == 'miga':
        Miga = getattr(importlib.import_module('main.models'), 'Miga')
        messageList = eval(user.getMessageList())
        userMessage = messageList.pop()

        userMessage = re.sub('\n+', ' ', userMessage)

        userMessage = re.sub('그?\s?외\s?$', '', userMessage)

        userMessage = re.sub('\s+', ' ', userMessage)

        if not re.search('^\s?중식', userMessage):
            userMessage = '(중식) ' + userMessage
        else:
            userMessage = re.sub('중식', '(중식) ', userMessage)

        userMessage = re.sub('\s+', ' ', userMessage)

        userMessage = re.sub('\s*[억석][십식]\s?', '\n(석식) ', userMessage)

        Miga.createOrUpdateMenu(menu = userMessage)

        return textMessage('미가식당 메뉴가 등록되었습니다!\n문의 : 010-9269-2298')

    elif response.func == '산대전':
        return linkMessage('산대전 제보함으로 연결해드릴게요!', '산대전 제보함', 'http://kpu.fbpage.kr/#/submit')

    elif response.func == 'kpuwatch':
        messageList = eval(user.getMessageList())
        userMessage = messageList.pop()
        typeMessage = messageList.pop() # '교수검색' or '강의검색'

        resultText = kpuwatchMod.getKPUWatchText(typeMessage, userMessage)
        return textMessage('KPUWatch가 산기인과 통합된 관계로 종료합니다.')
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

    elif response.func == 'summary':
        Log = getattr(importlib.import_module('main.models'), 'Log')

        #weekday = {'0' : '월요일', '1' : '화요일', '2' : '수요일', '3' : '목요일', '4' : '금요일', '5' : '토요일', '6' : '일요일'}
        weekday = {0 : '월요일', 1 : '화요일', 2 : '수요일', 3 : '목요일', 4 : '금요일', 5 : '토요일', 6 : '일요일'}

        today_date = datetime.datetime.now()
        today_count = Log.objects.filter(dateTime__contains = str(datetime.datetime.now().date())).values('user_id').distinct().count()
        text = '오늘은 {}! 현재시각까지 사용자 수는 {}명!\n\n'.format(weekday[today_date.weekday()], today_count)

        for i in range(1, 8):
            target_date = datetime.datetime.now().date() - datetime.timedelta(i)
            count = Log.objects.filter(dateTime__contains = str(target_date)).values('user_id').distinct().count()
            text += '{}일 전({}) 사용자 수 {}명\n'.format(i, weekday[target_date.weekday()], count)

        return textMessage(text)

    elif response.func == 'love':
        dDay_dict = {'김재형' : '2015-08-13',
                '임종길' : '2016-07-22',
                '채상원' : '2017-08-22'}

        now = datetime.datetime.now()

        text = str()

        for i in dDay_dict:
            dday = now - datetime.datetime.strptime(dDay_dict[i], '%Y-%m-%d')
            text += '{}, {}부터 사귐.\n 고로 {}일째 연애중!\n\n'.format(i, dDay_dict[i], dday.days)

        text += '윤서율, NULL부터 사귐.\n 고로 -1일째 연애중!\n\n'
        text += '\n결론: 헤어지지말고 오래오래 사귀셈'

        return textMessage(text)

    elif response.func == 'chaesangwon':
        #datetime.datetime.
        pass



def linkMessage(botText, label, url):
    return {'message' : {'text' : botText, 'message_button' : {'label' : label, 'url' : url}}}

def textMessage(botText):
    return {'message' : {'text' : botText}}

def stringFormatConvert(respDict):
    return respDict['state']['desired']['feedtime']


# 추후에 처리!
def addButtonsToTextMessage(targetDict, buttonList):
    targetDict = {'keyboard' :
                    {
                'type' : 'buttons',
                'buttons' : buttonList
                    }
                }
    return targetDict
