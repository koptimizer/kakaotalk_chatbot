import urllib.request
from xml.etree import ElementTree
from . import keys

#routeId = {'26' : '224000020', '26-1' : '224000027', '20-1' : '224000011', '25' : '224000007', '28' : '224000021', '28-1' : '224000048', '29' : '224000022', '29-1' : '224000049', '30' : '224000012', '7' : '224000033', '11-A' : '224000036'}


#url = 'http://openapi.gbis.go.kr/ws/rest/busarrivalservice?serviceKey=' + key + '&stationId=' + stationId['정왕역환승센터'] # 버스도착정보항목조회 URL

#url = 'http://openapi.gbis.go.kr/ws/rest/busarrivalservice/station?serviceKey=' + key + '&stationId=' + stationId['정왕역환승센터'] # 버스도착정보항목조회 URL

#print(result.decode('UTF-8'))

def getBusText():
    stationId = {'정왕역' : '224000023', '정왕역환승센터' : '224000837'}
    resultList = getBusArrivalList(stationId['정왕역환승센터'], keys.data_go_kr)

    resultText = '[정왕역환승센터 정류장 실시간 안내]'
    resultText += '\n======================\n'

    routeId = {'224000020' : '26', '224000027' : '26-1',
            '224000011' : '20-1', '224000007' : '25',
            '224000021' : '28', '224000048' : '28-1',
            '224000022' : '29', '224000049' : '29-1',
            '224000012' : '30', '224000033' : '7',
            '224000036' : '11-A'}

    for item in resultList:
        resultText += routeId[item['routeId']] + '번 버스'

        if item['predictTime1']:
            resultText += ' [' + str(item['predictTime1']) + '분 전]'

        if item['predictTime2']:
            resultText += ' [' + str(item['predictTime2']) + '분 전]'

        resultText += '\n'

    resultText += '======================'

    return resultText

def getBusArrivalList(stationId, key):

    if stationId == '224000837':
        print('정왕역환승센터')
    elif stationId == '224000023':
        print('정왕역')
    else:
        print('알 수 없는 stationId')

    url = 'http://openapi.gbis.go.kr/ws/rest/busarrivalservice/station?serviceKey=' + key + '&stationId=' + stationId
    req = urllib.request.Request(url)
    fp = urllib.request.urlopen(req)
    result = fp.read()
    fp.close()

    print(result.decode('UTF-8'))
    root = ElementTree.fromstring(result.decode('UTF-8'))
    if root.find('msgHeader').find('resultCode').text == '4':
        return []

    busArrivalList = root.find('msgBody').findall('busArrivalList')

    resultList = list()
    for item in busArrivalList:
        itemDict = {
                    'routeId' : item.find('routeId').text,
                    'predictTime1' : item.find('predictTime1').text,
                    'predictTime2' : item.find('predictTime2').text
                   }

        resultList.append(itemDict)

    print('getBusArrivalList 종료')
    return resultList
