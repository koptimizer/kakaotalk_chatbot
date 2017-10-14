import urllib.request
from xml.etree import ElementTree
from . import keys

def getBusText(stationName):
    stationId = {'정왕역' : '224000023', '정왕역환승센터' : '224000837'}

    responseDict = get(stationId[stationName])
    if responseDict['status'] == 'fail':
        return '오류발생(CODE:' + responseDict['code'] + ')'
    elif responseDict['status'] == 'nodata':
        return stationName + ' 버스 운행은 종료되었습니다'

    routeId = {'224000020' : '26', '224000027' : '26-1',
                '224000011' : '20-1', '224000007' : '25',
                '224000021' : '28', '224000048' : '28-1',
                '224000022' : '29', '224000049' : '29-1',
                '224000012' : '30', '224000033' : '7',
                '224000036' : '11-A'}

    text = '[정왕역환승센터 정류장 실시간 안내]\n'
    for arrival in responseDict['arrivalList']:
        text += routeId[arrival['routeId']] + ' 버스: '
        if arrival['predictTime1']:
            text += '[' + arrival['predictTime1'] + '분 전]'
        if arrival['predictTime2']:
            text += '[' + arrival['predictTime2'] + '분 전]'
        text += '\n'

    return text

def get(stationId):
    api_response = request(stationId)
    root = ElementTree.fromstring(api_response)

    resultCode = root.find('msgHeader').find('resultCode').text
    if resultCode == '0':
        resultDict = {'status' : 'success', 'code' : resultCode}
    elif resultCode == '4':
        resultDict = {'status' : 'nodata', 'code' : resultCode}
        return resultDict
    else:
        resultDict = {'status' : 'fail', 'code' : resultCode}
        return resultDict

    arrivalList = list()
    for arrival in root.find('msgBody').findall('busArrivalList'):
        element = {'routeId' : arrival.find('routeId').text,
                'predictTime1' : arrival.find('predictTime1').text,
                'predictTime2' : arrival.find('predictTime2').text}
        arrivalList.append(element)

    resultDict['arrivalList'] = arrivalList
    return resultDict

def request(stationId):
    url = 'http://openapi.gbis.go.kr/ws/rest/busarrivalservice/station?serviceKey='
    url += keys.data_go_kr + '&stationId='
    url += stationId

    req = urllib.request.Request(url)
    fp = urllib.request.urlopen(req)
    result = fp.read()
    fp.close()

    #return ElementTree.fromstring(result.decode('UTF-8'))
    return result.decode('UTF-8')
