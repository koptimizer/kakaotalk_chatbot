from chatbot import messageMod
import json
import bs4
import datetime
import requests
import re

def haksaKeywordFinder(sentence):
    keywordList = list()

    simpleFinder(sentence, keywordList, [r'신입생'], '!신입생')
    simpleFinder(sentence, keywordList, [r'1학기'], '!1학기')
    simpleFinder(sentence, keywordList, [r'2학기'], '!2학기')
    simpleFinder(sentence, keywordList, [r'계절학기'], '!계절학기')
    simpleFinder(sentence, keywordList, [r'수강\s?신청'], '수강신청')
    simpleFinder(sentence, keywordList, [r'개[학강]'], '개강')
    simpleFinder(sentence, keywordList, [r'토익', r'어학\s?시험', r'어학\s?자격\s?시험'], '어학자격시험')
    simpleFinder(sentence, keywordList, [r'휴·?복?학', r'복학'], '휴복학')
    simpleFinder(sentence, keywordList, [r'정정', r'과목\s?정정', r'수강\s?정정'], '수강정정')
    simpleFinder(sentence, keywordList, [r'입학식'], '입학식')
    simpleFinder(sentence, keywordList, [r'수강\s?철회'], '수강철회')
    simpleFinder(sentence, keywordList, [r'중간', r'중간\s?고사'], '중간고사')
    simpleFinder(sentence, keywordList, [r'보강', r'기말', r'기말\s?고사'], '기말고사')
    simpleFinder(sentence, keywordList, [r'체전', r'체육\s?대회'], '체육대회')
    simpleFinder(sentence, keywordList, [r'Techno\s?Festival', r'축제'], '축제')
    simpleFinder(sentence, keywordList, [r'미리\s?담기'], '미리담기')
    simpleFinder(sentence, keywordList, [r'개교\s?기념일'], '개교기념일')
    simpleFinder(sentence, keywordList, [r'방학'], '방학')
    simpleFinder(sentence, keywordList, [r'기술\s?대전', r'산업\s?대전', r'산업\s?기술\s?대전'], '산업기술대전')
    simpleFinder(sentence, keywordList, [r'학위\s?수여'], '학위수여식')
    simpleFinder(sentence, keywordList, [r'성적\s?입력'], '성적입력')
    simpleFinder(sentence, keywordList, [r'성적\s?확인'], '성적확인')

    return keywordList

def isCore(keyword):
    # 받은 키워드가 수식인가 아닌가?
    m = re.search(r'^\!.+', keyword)
    if not m:
        return 1
    else:
        return 0

def simpleFinder(sentence, keywordList, list, keyword):
    for i in list:
        m = re.search(i, sentence)
        if m:
            keywordList.append(keyword)
            return

def listCmp(userWordList, haksaWordList):
    print('listCmp:userKeywordList' + str(userWordList) + ', haksaKeywordList' + str(haksaWordList))
    
    isCoreExists = 0

    if len(userWordList) == 0 or len(haksaWordList) == 0:
        return 0 

    for i in range(0, len(userWordList)):
        keyword = messageMod.searchInList(haksaWordList, userWordList[i], size = -1)
        if keyword and isCore(keyword):
            isCoreExists = 1
        elif keyword and not isCore(keyword):
            continue
        else:
            return 0

    if isCoreExists:
        return 1

    else:
        return 0

def getHaksaMessage(sentence):
    # sentence는 ~언제야에서 '언제야'를 제외한 문장
    # sentence는haksaKeywordFinder를 통해서 분류
    # 현재 날자와 비교해서 오늘 날자부터 걸리면 표시
    # keywordList를 받아서 검사

    userKeywordList = haksaKeywordFinder(sentence)
    print('인식된 userKeywordList' + str(userKeywordList))
    now = datetime.datetime.now()
    haksaDictList = getHaksaDictList()

    index = -1
    for i in range(0, len(haksaDictList)):
        # keyword 또는 keyword와 유사한 키워드를 가지는 content를 찾아야 함.
        haksaKeywordList = haksaKeywordFinder(haksaDictList[i]['content'])
        if listCmp(userKeywordList, haksaKeywordList):
        # 찾았음
            textDate_endDate = haksaDictList[i]['year'] + '/' + haksaDictList[i]['endDate']
            textDate_startDate = haksaDictList[i]['year'] + '/' + haksaDictList[i]['startDate']
            haksaDate_endDate = datetime.datetime.strptime(textDate_endDate, '%Y/%m월 %d일')
            haksaDate_startDate = datetime.datetime.strptime(textDate_startDate, '%Y/%m월 %d일')
            dateDiff_endDate = haksaDate_endDate - now
            dateDiff_startDate = haksaDate_startDate - now

            dday_endDate = int(dateDiff_endDate.total_seconds() / 86400)
            dday_startDate = int(dateDiff_startDate.total_seconds() / 86400)

            if dday_endDate >= 0:
                index = i
                break

    if index >= 0:
        text = haksaDictList[index]['content'] + ' 일정은\n'
        if haksaDictList[index]['startDate'] != haksaDictList[index]['endDate']:
            text = text + haksaDictList[index]['year'] + '년 ' + haksaDictList[index]['startDate'] + '부터 ' + haksaDictList[index]['endDate'] + '입니다~^^'
        else:
            text = text + haksaDictList[index]['year'] + '년 ' + haksaDictList[index]['startDate'] + '입니다~^^'

        if dday_startDate > 0:
            text = text + '\n' + str(dday_startDate) + '일 남았네요!'

    elif index == -1:
        text = '찾으시는 일정이 없어요~'

    response = {'message':{'text':text}}
    response = json.dumps(response)

    return response

def getHaksaDictList():
    resq = requests.get('http://www.kpu.ac.kr/front/haksaschedule.do')
    bs = bs4.BeautifulSoup(resq.text, 'html.parser')
    bs = bs('tbody')[0] # 해당 전체 테이블 

    text = ''

    haksaDictList = list()

    for i in range(0, len(bs('tr'))):
        haksaDict = dict()
        bs_tr = bs('tr')[i]
        
        bs_year = bs_tr.find_all('span', {'class':'year'})
        #bs_month = bs_tr.find_all('span', {'class':'month'})
        bs_date = bs_tr.find_all('td', {'class':'date'})
        bs_content = bs_tr.find_all('p', {'class':'bl md'})

        if bs_year:
            year = bs_year[0].get_text()
            year = re.sub(r'\n', '', year)
            haksaDict['year'] = year
        else:
            haksaDict['year'] = year

        #if bs_month:
        #    month = bs_month[0].get_text()
        #    month = re.sub(r'\n', '', month)
        #    haksaDict['month'] = month
        #else:
        #    haksaDict['month'] = month

        if bs_date:
            date = bs_date[0].get_text()
            #date = re.sub(r'\n', '', date)
            startDate = re.sub(r'\n?(\d\d)\.(\d\d)\s?~\s?\d\d\.\d\d\n?', r'\1월 \2일', date)
            endDate = re.sub(r'\n?\d\d\.\d\d\s?~\s?(\d\d)\.(\d\d)\n?', r'\1월 \2일', date)

            haksaDict['startDate'] = startDate
            haksaDict['endDate'] = endDate
        else:
            haksaDict['startDate'] = None
            haksaDict['endDate'] = None

        if bs_content:
            content = bs_content[0].get_text()
            content = re.sub(r'\n', '', content) 
            haksaDict['content'] = content
        else:
            haksaDict['content'] = None

        haksaDictList.append(haksaDict)

    return haksaDictList
