import json
import bs4
import datetime
import requests
import re

def getMenu(datetimeObject):
    print('크롤러진입')
    req = requests.get('http://tip.kpu.ac.kr/front/boardview.do?pkid=13284&currentPage=1&searchField=ALL&menuGubun=2&bbsConfigFK=27&searchLowItem=ALL&searchValue')
    bs = bs4.BeautifulSoup(req.text, 'html.parser')
    menuTable = bs('table')[1] # 날자, 메뉴, 원산지까지 포함
    menuTableRows = menuTable('tr')[0:8] # 날자와 메뉴까지만 포함
    menuTableRows[0] # 날자행
    menuTableRows[1] # 조식행
    menuTableRows[2] # 중식행
    menuTableRows[3] # 석식행
    menuTableRows[4] # 날자행
    menuTableRows[5] # 조식행
    menuTableRows[6] # 중식행
    menuTableRows[7] # 석식행

    index = getMenuIndex(menuTableRows, datetimeObject)

    result = dict()
    result = get(menuTableRows, index)

def getMenuDict():
    datetimeObject = datetime.datetime.now()
    print('getMenuDict()')
    # 결과적으로 해당하는 datetime 날자의 조식, 중식, 석식이 구분된 dict 리턴
    req = requests.get('http://tip.kpu.ac.kr/front/boardview.do?pkid=13284&currentPage=1&searchField=ALL&menuGubun=2&bbsConfigFK=27&searchLowItem=ALL&searchValue')
    bs = bs4.BeautifulSoup(req.text, 'html.parser')
    menuTable = bs('table')[1] # 날자, 메뉴, 원산지까지 포함
    menuTableRows = menuTable('tr')[0:8] # 날자와 메뉴까지만 포함
    index = getMenuIndex(menuTableRows, datetimeObject)
    if index == -1:
        return{'breakfast' : '업데이트되지 않았습니다', 'lunch' : '업데이트되지 않았습니다', 'dinner' : '업데이트되지 않았습니다'}

    result = get(menuTableRows, index)
    print(str(result))
    return result

def get(menuTableRows, index):
    print('get(menuTableRows,%s)'%(index))
    # 우선 해당 날자의 메뉴들에 접근해야 함.
    size1 = len(menuTableRows[1]('td')) # 조식행 사이즈
    size2 = len(menuTableRows[2]('td')) # 중식행
    size3 = len(menuTableRows[3]('td')) # 석식행
    size5 = len(menuTableRows[5]('td')) # 조식행
    size6 = len(menuTableRows[6]('td')) # 중식행
    size7 = len(menuTableRows[7]('td')) # 석식행

    breakfastRows = list()
    for row in menuTableRows[1]('td')[1 : size1] + menuTableRows[5]('td')[1 : size5]:
        #print('breakfastRows = {}'.format(row.get_text()))
        breakfastRows.append(row.get_text().replace('\n', ' '))

    lunchRows = list()
    for row in menuTableRows[2]('td')[1 : size2] + menuTableRows[6]('td')[1 : size6]:
        lunchRows.append(row.get_text().replace('\n', ' '))

    dinnerRows = list()
    for row in menuTableRows[3]('td')[1 : size3] + menuTableRows[7]('td')[1 : size7]:
        dinnerRows.append(row.get_text().replace('\n', ' '))

    print('len(breakfastRows) = %s'%len(breakfastRows))
    print('len(lunchRows) = %s'%len(lunchRows))
    print('len(dinnerRows) = %s'%len(dinnerRows))

    if min([len(breakfastRows), len(lunchRows), len(dinnerRows)]) - 1 < index:
        index = min([len(breakfastRows), len(lunchRows), len(dinnerRows)])
        return {'breakfast' : breakfastRows[index], 'lunch' : breakfastRows[index], 'dinner' : breakfastRows[index]}
    else:
        return {'breakfast' : breakfastRows[index], 'lunch' : lunchRows[index], 'dinner' : dinnerRows[index]}

def getMenuIndex(menuTableRows, datetimeObject):
    print('getMenuIndex()')
    # 해당 날자(datetimeObject)에 해당하는 메뉴의 인덱스를 확인한다
    menuDatetimeList = getMenusDatetimeList(menuTableRows)
    for item in menuDatetimeList:
        if (datetimeObject - item).days == 0:
            print(str(item))
            return menuDatetimeList.index(item)
    print('탐색된 날자 없음' + str(datetimeObject))
    return -1 # 탐색된 날자 없음

def getMenusDatetimeList(menuTableRows):
    # 주어진 날자에서 메뉴가 있는지 확인하고, 몇번째 컬럼인지 리턴, 없으면 0
    size1 = len(menuTableRows[0]('td'))
    size2 = len(menuTableRows[4]('td'))

    menuTableRows1 = menuTableRows[0]('td')[1 : size1]
    menuTableRows2 = menuTableRows[4]('td')[1 : size2]

    datetimeList = list()

    for row in menuTableRows1 + menuTableRows2:
        datetimeList.append(datetime.datetime.strptime(row.find('p').get_text(), '%m월 %d일').replace(year = datetime.datetime.now().year))
        #dateList.append(row.find('p').get_text()) # 전체를 찾지 않고 첫번째를 찾는다.

    return datetimeList

def crawler(date, type = 'all'): # all breakfast lunch dinner
    print('크롤러진입')
    trim_date = date.replace(" ", "")
    resq = requests.get('http://tip.kpu.ac.kr/front/boardview.do?pkid=13284&currentPage=1&searchField=ALL&menuGubun=2&bbsConfigFK=27&searchLowItem=ALL&searchValue')
    bs = bs4.BeautifulSoup(resq.text, 'html.parser')
    bs = bs("table")[1]

    date_index = -1
    tr_index = 0

    for i in [0,4]:
        bs_tr = bs("tr")[i]
        for j in range(len(bs_tr("td"))): # range(5): 0~4, 길이
            bs_td = bs_tr("td")[j].get_text()
            bs_td = bs_td.replace(" ", "")
            bs_td = bs_td.replace("\n", "")
            print(bs_td)
            if bs_td == trim_date:
               tr_index = i
               date_index = j

    food_text = ""
    print(1)

    if date_index != -1:
        print('학식업뎃됨')
        food_text = date + ' 썬푸드 식단을 알려드릴께요~\n'

        for i in range(3): #날자를 찾은 테이블의 조식, 중식, 석식
            print('range(3) 들어감' + str(i))
            inner_tr_index = tr_index + 1 + i # 해당 테이블 내부를 도는 index
            bs_tr = bs("tr")[inner_tr_index]
            food_text = food_text + bs_tr("td")[0].get_text() + "\n" + bs_tr("td")[date_index].get_text() + "\n"

        print(food_text)
    else:
        print('학식업뎃안됨')
        food_text = '학교 사이트에 ' + date + '의 학식정보가 업데이트되지 않았어요!'

    print(2)
    food_response = {'message':{'text':food_text}}
    food_response = json.dumps(food_response)

    print('크롤러종료됨')
    return food_response
