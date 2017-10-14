from . import keys
import urllib.request
import urllib.parse
import json

def getMetroText(stationName):
    # 정왕역 전용! => 당고개행, 오이도행 표시
    #              => '전역 도착'은 가독성을 위해 '오이도역 대기/출발'로
    # 해당 역의 상행, 하행
    responseDict = get(stationName)
    if responseDict['status'] == 'fail':
        return '오류발생 ' + responseDict['code']
    elif responseDict['status'] == 'nodata':
        return stationName + '역 지하철 운행은 종료되었습니다'

    #if not responseDict['arrivalList']:
        #return '지하철 운행종료'
    #    return ''

    toDG = '[당고개행 지하철 안내]\n'
    toOido = '[오이도행 지하철 안내]\n'
    for arrival in responseDict['arrivalList']:
        if arrival['updnLine'] == '상행':
            if arrival['arvlStatus'] == '전역 도착':
                toDG += '* 오이도역 출발/대기중' + '\n'
            else:
                toDG += '* ' + arrival['arvlMsg2'] + '\n'
        elif arrival['updnLine'] == '하행':
            toOido += '* ' + arrival['arvlMsg2'] + '\n'

    return toDG + '\n' + toOido

def get(stationName):
    # arvlMsg2(현재 위치), arvlMsg3, arvlCd, updnLine('상행' or '하행')
    # 오류 발생시 status = 'fail', 정상 작동시 'success'
    api_response = request(stationName)
    print('api_response = ' + str(api_response))

    arvlCd = {'0' : '진입', '1' : '도착', '2' : '출발', '3' : '전역출발', '4' : '전역진입', '5' : '전역 도착', '99' : '운행중'}

    resultDict = dict()
    if 'errorMessage' in api_response:
        resultDict['code'] = api_response['errorMessage']['code']
    else:
        resultDict['code'] = api_response['code']

    if resultDict['code'] == 'INFO-000':
        resultDict['status'] = 'success'
    elif resultDict['code'] == 'INFO-200':
        resultDict['status'] = 'nodata'
        return resultDict
    else:
        resultDict['status'] = 'fail'
        return resultDict

    #if not responseDict['arrivalList']: # 운행 종료
    #    resultDict['status'] = 'nodata'
    #    return ''

    arrivalList = list()
    for element in api_response['realtimeArrivalList']:
        arrivalList.append({'arvlMsg2' : element['arvlMsg2'], 'arvlMsg3' : element['arvlMsg3'],'arvlStatus' : arvlCd[element['arvlCd']], 'updnLine' : element['updnLine'], 'btrainNo' : int(element['btrainNo'])})

    #sorted(arrivalList, key = int(arrivalList['btrainNo']))
    arrivalList = sorted(arrivalList, key = lambda arrival : arrival['btrainNo'])
    #print('arrivalList = ' + str(arrivalList))
    resultDict['arrivalList'] = arrivalList
    return resultDict

def request(stationName):
    # stationName : 역명 ex) '정왕', '서울', '잠실'...
    # 응답값을 그대로 파싱한 Dictionary 타입으로 리턴

    url = 'http://swopenapi.seoul.go.kr/api/subway/'
    url += keys.data_seoul_go_kr
    url += '/json/realtimeStationArrival/0/5/'
    url += urllib.parse.quote_plus(stationName)

    #print(url)
    req = urllib.request.Request(url)
    fp = urllib.request.urlopen(req)
    result = fp.read()
    fp.close()

    return json.loads(result.decode('UTF-8'))
