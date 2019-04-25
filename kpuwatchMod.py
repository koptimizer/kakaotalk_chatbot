import json
import re
import requests
from bs4 import BeautifulSoup
import random

def getKPUWatchText(typeMessage, userMessage):
    resultText = '\'' + userMessage + '\'\nKPUWatch에서 찾아봤어요!\n\n'
    userMessage = userMessage.replace(' ', '')

    if re.search('강의', typeMessage):
        url = 'http://kpuwatch.com/rating_search.php?subject=' + userMessage
    elif re.search('교수', typeMessage):
        url = 'http://kpuwatch.com/rating_search.php?professor=' + userMessage

    req = requests.get(url)

    bs = BeautifulSoup(req.text, 'html.parser')
    contentList = bs.find_all('content')
    contentList = list(map(lambda x: '\"' + re.sub('\d.\s', '', x.text, 1) + '\"', contentList)) # 앞의 숫자 요소 제거

    if len(contentList) >= 2:
        rd = random.sample(range(0, len(contentList)), 2)
        resultText += contentList[rd[0]] + '\n\n' + contentList[rd[1]]
        print('type은 ' + str(type(resultText)))
        return resultText

    elif len(contentList) == 1:
        rd = random.randrange(0, len(contentList))
        resultText += contentList[rd]
        return resultText

    else:
        return None
