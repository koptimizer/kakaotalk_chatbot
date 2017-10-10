from urllib import request
from xml.etree import ElementTree
import datetime
from . import keys

def buildMetroText():
    now = datetime.datetime.now()

    resultText = '[정왕역(상행) 실시간 안내]'
    resultText += '\n======================\n'

    upTimeList = getNextMetroTimes(now, '상행')
    if len(upTimeList) == 1:
        resultText += str(upTimeList[0].hour) + '시 ' + str(upTimeList[0].minute) + '분 [' + getRemainTime(now, upTimeList[0]) + '분 전]'
    elif len(upTimeList) == 2:
        resultText += str(upTimeList[0].hour) + '시 ' + str(upTimeList[0].minute) + '분 [' + getRemainTime(now, upTimeList[0]) + '분 전]'
        resultText += '\n\n' + str(upTimeList[1].hour) + '시 ' + str(upTimeList[1].minute) + '분 [' + getRemainTime(now, upTimeList[1]) + '분 전]'
    resultText += '\n======================'

    return resultText

def getRemainTime(now, metroTime):
    timeDiff = metroTime - now
    timeDiff_minutes = timeDiff.total_seconds() / 60
    return str(int(timeDiff_minutes))

def getNextMetroTimes(now, upDownType):
    # datetime.datetime.now() 객체와 비교하여, 다음 두개의 지하철을 확인

    resultTimes = list()
    for pageNo in range(1, 20):
        metroTimeList = getMetroTimeList(now, upDownType, pageNo)
        if metroTimeList:
            for metroTime in metroTimeList:
                if isNext(now, metroTime):
                    #timeDiff = metroTime - now
                    #timeDiff_minutes = timeDiff.total_seconds() / 60
                    #resultTimes.append(timeDiff_minutes)
                    resultTimes.append(metroTime)
                    if len(resultTimes) >= 2:
                        return resultTimes
        else:
            break

    return resultTimes

def isNext(now, metroTime):
    if now < metroTime:
        return True
    else:
        return False

def getMetroTimeList(now, upDownType, pageNo):
    week = ['평일', '평일', '평일', '평일', '평일', '토요일', '일요일']
    now_week = week[now.weekday()]
    stationId = {'정왕' : 'SES1761'}
    dailyTypeCode = {'평일' : '01', '토요일' : '02', '일요일' : '03'}
    upDownTypeCode = {'상행' : 'U', '하행' : 'D'}

    url = 'http://openapi.tago.go.kr/openapi/service/SubwayInfoService/getSubwaySttnAcctoSchdulList?ServiceKey=' + keys.data_go_kr + '&subwayStationId=' + stationId['정왕'] + '&dailyTypeCode=' + dailyTypeCode[now_week] + '&upDownTypeCode=' + upDownTypeCode[upDownType] + '&pageNo=' + str(pageNo)

    req = request.Request(url)
    fd = request.urlopen(req)
    byteText = fd.read()

    root = ElementTree.fromstring(byteText.decode('UTF-8'))
    items = root.find('body').find('items')

    result = list()
    for item in items:
        arrTime = item.find('arrTime').text
        if int(arrTime[0:2]) >= 24:
            #date = datetime.datetime.now() + datetime.timedelta(1)
            date = now + datetime.timedelta(1)
            tomorrowTime = int(arrTime[0:2]) % 24
            time = now.replace(day = date.day, hour = tomorrowTime, minute = int(arrTime[2:4]), second = int(arrTime[4:6]))
            result.append(time)
        else:
            time = now.replace(hour = int(arrTime[0:2]), minute = int(arrTime[2:4]), second = int(arrTime[4:6]))
            result.append(time)

    return result
