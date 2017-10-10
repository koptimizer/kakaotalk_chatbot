from datetime import datetime
import re

UnivToJW = ['0840-0940:본교 정문, 도착버스 탑승', '0955', '1010', '1039', '1055', '1103', '1111', '1130', '1141', '1152', '1200', '1206', '1215', '1227', '1244', '1254', '1305', '1315', '1334', '1344', '1400', '1410', '1420', '1430', '1440', '1450', '1500', '1510', '1520', '1530', '1540', '1550', '1600', '1610', '1620', '1630', '1640', '1650', '1700-1830:수시운행', '1840', '1850', '1900', '1910', '1920', '1930', '1940', '1950', '2002', '2015', '2030', '2040', '2050', '2103', '2113', '2124', '2136', '2150', '2202', '2210', '2220', '2230', '2240']

JWToUniv = ['0840-1020:열차 도착 후 출발', '1028', '1036', '1049', '1105', '1113', '1118', '1121', '1140', '1151', '1202', '1210', '1216', '1225', '1237', '1254', '1304', '1308', '1315', '1318', '1325', '1344', '1354', '1410', '1420', '1430', '1440', '1450', '1500', '1510', '1520', '1530', '1540', '1550', '1600', '1610', '1620', '1630', '1640', '1650', '1700-2250:도착 버스 탑승']

OidoToUniv = ['0850', '0855', '0905', '0910', '0912', '0955', '1010', '1012', '1110', '1112', '1212', '1312', '1412', '1512', '1600-2000:도착버스 탑승, 마지막 버스(22:20분 학교발) 제외']

UnivToOido = ['0905-0927:본교 정문, 도착버스 탑승', '1140', '1240', '1340', '1440', '1540', '1640', '1728', '1738', '1836', '1848', '1936', '2220']

def test(dest, now = datetime.now()):
    #now = datetime.now().replace(hour = 16, minute = 50)
    print(str(buildText(dest, now)))

def calcTimeDiff(timeobj, currentTime):
    timeDiff = timeobj - currentTime
    return str(int(timeDiff.total_seconds()/60))

def getShuttleTimes(inputTimes, now):
    nowInt = int(str(now.hour) + str(now.minute))
    #cnt = 0
    outputTimes = list()
    for item in inputTimes:
        if re.search(r'\d\d\d\d-\d\d\d\d:?[\s\S]*', item):
            print('첫번째 걸림')
            start = re.sub(r'(\d\d\d\d)-\d\d\d\d:?[\s\S]*', r'\1', item)
            end = re.sub(r'\d\d\d\d-(\d\d\d\d):?[\s\S]*', r'\1', item)
            text = re.sub(r'\d\d\d\d-\d\d\d\d:?([\s\S]*)', r'\1', item)
            if int(end) > nowInt:
                item = dict()
                item['start'] = now.replace(hour = int(start[0:2]), minute = int(start[2:4]))
                item['end'] = now.replace(hour = int(end[0:2]), minute = int(end[2:4]))
                item['text'] = text
                item['type'] = 'range'
                outputTimes.append(item)
                #cnt = cnt + 1

        elif re.search(r'\d\d\d\d', item):
            print('두번째 걸림')
            time = re.sub(r'(\d\d\d\d)', r'\1', item)
            if int(time) > nowInt:
                item = dict()
                item['time'] = now.replace(hour = int(time[0:2]), minute = int(time[2:4]))
                item['type'] = 'single'
                outputTimes.append(item)
                #cnt = cnt + 1

        if len(outputTimes) == 2:
            break

    return outputTimes

def buildText(dest):
    now = datetime.now()
    print('데이트타임:' + str(now))

    if dest == 'JWToUniv':
        inputTimes = JWToUniv
        resultText = '[정왕역 > 학교 실시간 안내]'
    elif dest == 'UnivToJW':
        inputTimes = UnivToJW
        resultText = '[학교 > 정왕역 실시간 안내]'
    elif dest == 'OidoToUniv':
        inputTimes = OidoToUniv
        resultText = '[오이도역 > 학교 실시간 안내]'
    elif dest == 'UnivToOido':
        inputTimes = UnivToOido
        resultText = '[학교 > 오이도역 실시간 안내]'
    resultText += '\n======================'

    nextShuttleTimes = getShuttleTimes(inputTimes, now)

    if len(nextShuttleTimes) == 0: # 그날의 모든 셔틀 운행이 종료되었음!
        resultText += '\n' + '오늘의 운행이 종료되었습니다'

    elif len(nextShuttleTimes) == 1: # 막차만 남았거나 수시운행만 남아있는 경우
        if nextShuttleTimes[0]['type'] == 'range':
            start = nextShuttleTimes[0]['start']
            end = nextShuttleTimes[0]['end']
            text = nextShuttleTimes[0]['text']
            if now >= start:
                resultText += '\n' + str(start.hour) + '시 ' + str(start.minute) + '분~' + str(end.hour) + '시 ' + str(end.minute) + '분/운행중'
            elif now < start:
                resultText += '\n' + str(start.hour) + '시 ' + str(start.minute) + '분~' + str(end.hour) + '시 ' + str(end.minute) + '분[' + calcTimeDiff(start, now) + '분전]'
            resultText += '\n(' + text + ')'
        elif nextShuttleTimes[0]['type'] == 'single':
            time = nextShuttleTimes[0]['time']
            resultText += '\n' + str(time.hour) + '시 ' + str(time.minute) + '분[' + calcTimeDiff(time, now) + '분전]'

    elif len(nextShuttleTimes) == 2:
        if nextShuttleTimes[0]['type'] == 'range':
            start = nextShuttleTimes[0]['start']
            end = nextShuttleTimes[0]['end']
            text = nextShuttleTimes[0]['text']
            if now >= start:
                resultText += '\n' + str(start.hour) + '시 ' + str(start.minute) + '분~' + str(end.hour) + '시 ' + str(end.minute) + '분[운행중]'
            elif now < start:
                resultText += '\n' + str(start.hour) + '시 ' + str(start.minute) + '분~' + str(end.hour) + '시 ' + str(end.minute) + '분[' + calcTimeDiff(start, now) + '분전]'
            resultText += '\n(' + text + ')'
            resultText += '\n'
        elif nextShuttleTimes[0]['type'] == 'single':
            time = nextShuttleTimes[0]['time']
            resultText += '\n' + str(time.hour) + '시 ' + str(time.minute) + '분[' + calcTimeDiff(time, now) + '분전]'
            resultText += '\n'

        if nextShuttleTimes[1]['type'] == 'range':
            start = nextShuttleTimes[1]['start']
            end = nextShuttleTimes[1]['end']
            text = nextShuttleTimes[1]['text']
            if now >= start:
                resultText += '\n' + str(start.hour) + '시 ' + str(start.minute) + '분~' + str(end.hour) + '시 ' + str(end.minute) + '분[운행중]'
            elif now < start:
                resultText += '\n' + str(start.hour) + '시 ' + str(start.minute) + '분~' + str(end.hour) + '시 ' + str(end.minute) + '분[' + calcTimeDiff(start, now) + '분전]'
            resultText += '\n(' + text + ')'
        elif nextShuttleTimes[1]['type'] == 'single':
            time = nextShuttleTimes[1]['time']
            resultText += '\n' + str(time.hour) + '시 ' + str(time.minute) + '분[' + calcTimeDiff(time, now) + '분전]'

    resultText += '\n======================'

    return resultText
