from django.db import models
from django.utils import timezone
from . import funcMod
import datetime
import re
import random

class Group(models.Model):
    group_name = models.CharField(max_length = 30, null = False, unique = True)

    def __str__(self):
        return self.group_name

    def createGroup(group_name):
        Group.objects.create(group_name = group_name)

    def get(group_name):
        try:
            return Group.objects.get(group_name = group_name)
        except:
            return None

    def showAll(targetGroup = None):
        print('======================GROUP=======================')
        print('group_name\tuser_name')
        print('- - - - - - - - - - - - - - - - - - - - - - - - - ')
        if targetGroup:
            groups = [targetGroup]
        else:
            groups = Group.objects.all()

        for group in groups:
            print(group.group_name, end = '\t\t')
            users = list(User.objects.filter(group = group))
            for user in users:
                if users.index(user) != 0:
                    print(end = ', ')
                print(user.user_name + '(' + user.user_key + ')', end = '')
            print()

    def removeGroup(group_name):
        try:
            group = Group.objects.get(group_name = group_name)
        except:
            print('존재하지 않는 Group 입니다')
            return
        group.delete()

    def setGroupName(self, group_name):
        self.group_name = group_name
        self.save()

    class manages():
        def manageGroup():
            # 향후에는 Group명 수정, 멤버수정 두가지를 여기서 처리 할 수 있도록 하는게 좋을 듯.
            while(True):
                Group.showAll()
                choice = input('\n[1]Group명 변경 [2]Group멤버 추가 [3]Group멤버 삭제 [exit()]종료 > ')
                if choice == '1':
                    group = Group.manages.selectGroup()
                    if not group:
                        continue

                    print('변경전>' + group.group_name)
                    modGroupName = input('변경후>')
                    if Tools.YoN('변경하시겠습니까? [y/n] > '):
                        group.setGroupName(modGroupName)
                        print('변경되었습니다')
                    else: print('취소되었습니다')

                elif choice == '2':
                    group = Group.manages.selectGroup()
                    if not group:
                            continue

                    user = User.manages.selectUser()
                    if not user:
                        continue

                    if user.group == group:
                        print('이미 해당 Group 소속입니다')
                    else:
                        user.setGroup(group)
                        print('추가되었습니다')

                elif choice == '3':
                    Group.showAll()
                    user = User.manages.selectUser()
                    if not user:
                        continue

                    user.setGroup(None)
                    print('삭제되었습니다')

                elif choice == 'exit()':
                    return

                else:
                    continue

        def selectGroup():
            Group.showAll()
            while(True):
                group_name = input('선택할 Group 명을 입력하세요 [exit()]종료 > ')
                if group_name == 'exit()':
                    return None

                group = Group.get(group_name)
                if group:
                    return group
                else:
                    print('존재하지 않는 Group입니다')

        def createGroup():
            group_name = input('생성할 Group 명을 입력하세요 [exit()]종료 > ')
            if group_name == 'exit()':
                return
            else:
                if Tools.YoN(group_name + '(으)로 생성하시겠습니까? [y/n] > '):
                    Group.createGroup(group_name = group_name)

        def removeGroup():
            Group.showAll()
            group_name = input('삭제할 Group 명을 입력하세요 > ')

            try: targetGroup = Group.objects.get(group_name = group_name)
            except:
                print('존재하지 않는 Group 입니다')
                return

            # 해당 그룹에 속해있는 User 목록
            if User.objects.filter(group = targetGroup):
                Group.showAll(targetGroup)
                if not Tools.YoN('위 User들의 Group 상태가 None이 됩니다. [y/n] > '):
                    return

            # 해당 그룹에 속해있는 Response 목록
            print('targetGroup = ' + str(targetGroup))
            responses = Response.objects.filter(group = targetGroup)
            if responses:
                Response.showAll(responses)
                if not Tools.YoN('위 Response들이 자동적으로 삭제 됩니다. [y/n] > '):
                    return

            if Tools.YoN('정말 ' + targetGroup.group_name + '그룹을 삭제하시겠습니까? [y/n]'):
                Group.removeGroup(group_name)
                print('Group이 삭제되었습니다')
                return

# 실제 db.sqlite3 파일에는 chatbot_User, chatbot_Mail 등과 같은 이름으로 테이블이 생성 된다.
class User(models.Model):
    user_name = models.CharField(max_length = 30, default = None, null = True)
    user_key = models.CharField(max_length = 30, primary_key = True)
    group = models.ForeignKey(Group, on_delete = models.SET_NULL, null = True, default = None)
    mailCheck = models.BooleanField(default = False)
    combineIdList = models.CharField(max_length = 50, null = True, default = '[0]')
    messageList = models.TextField(default = '[]')
    doNextKeywordCheck = models.BooleanField(default = True)

    def showAll():
        print('======================USER========================')
        print('user_key\tuser_name\tgroup')
        print('- - - - - - - - - - - - - - - - - - - - - - - - - ')
        for user in User.objects.all():
            print(user.user_key + '\t' + str(user.user_name) + '\t\t' + str(user.group))

    def setDoNextKeywordCheck(self, TrueOrFalse):
        self.DoNextkeywordCheck = TrueOrFalse
        self.save()

    def getByGroup(group_name):
        try:
            group = Group.objects.get(group_name = group_name)
            return User.objects.get(group = group)
        except:
            return None

    def getOrNoneByName(user_name):
        try: return User.objects.get(user_name = user_name)
        except:
            return None

    def setGroup(self, group):
        self.group = group
        self.save()

    def setCombineIdList(self, combineIdList):
        self.combineIdList = combineIdList
        self.save()

    def getMessageList(self):
        return self.messageList

    def setMessageList(self, messageList):
        self.messageList = str(messageList)
        self.save()

    def getOrCreate(user_key):
        try:
            return User.objects.get(user_key = user_key)
        except:
            User.objects.create(user_key = user_key)
            return User.objects.get(user_key = user_key)

    def setMailCheck(self, mailChecked):
        self.mailCheck = mailChecked
        self.save()

    def setName(self, name):
        self.user_name = name
        self.save()

    def __str__(self):
        return self.user_key + '|' + str(self.user_name)

    class manages():
        def selectUser():
            while(True):
                user_name = input('User의 user_name를 입력하세요 [exit()]종료 > ')
                if user_name == 'exit()':
                    return None

                user = User.getOrNoneByName(user_name = user_name)
                if user:
                    return user
                else:
                    print('존재하지 않는 User입니다')

class Mail(models.Model):
    # 만약 여기서 참조하는 User의 데이터가 지워지면 CASCADE 옵션에 의해 같이 삭제
    # ForeignKey는 해당 인스턴스를 파라메터로 넘겨주어야 함
    sender = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'mail_set_sender')
    receiver = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'mail_set_receiver')
    message = models.TextField()
    dateTime = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return str(self.sender.user_name) + '|' + self.message

    def getNumOfMails(user):
        return len(Mail.objects.filter(receiver = user))

    def readMail(user):
        if Mail.getNumOfMails(user) == 0:
            return '메일함이 비었어요~*'

        mail = Mail.objects.filter(receiver = user).order_by('-dateTime')[0]
        date = datetime.datetime.strptime(str(mail.dateTime), '%Y-%m-%d %H:%M:%S.%f')

        week = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']

        if date.hour <= 11:
            hour = '오전 ' + str(date.hour)
        elif date.hour == 12:
            hour = '오후 ' + str(date.hour)
        elif date.hour > 12:
            hour = '오후 ' + str(date.hour - 12)

        botMessage = str(date.year) + '년 ' + str(date.month) + '월 ' + str(date.day) + '일 ' + week[date.weekday()] + '\n' + hour + '시 ' + str(date.minute) + '분\n' + '발신자 : '  + str(mail.sender.user_name) + '\n\n' + mail.message

        mail.delete()

        return botMessage

    def sendMail(sender, receiver, message):
        Mail.objects.create(sender = sender, receiver = receiver, message = message)

class Log(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    userMessage = models.TextField(null = True)
    botMessage = models.TextField(null = True)
    dateTime = models.DateTimeField(auto_now_add = True)
    delay = models.FloatField(null = True)
    keywordList = models.CharField(max_length = 100, null = True)

    def showAllByKeyword(keywordList):
        # keywordList에 해당하는 Log의 목록을 보여줌
        print('=======================LOG========================')
        print('user_key\tuserMessage\t')
        print('- - - - - - - - - - - - - - - - - - - - - - - - - ')
        for log in Log.objects.filter(keywordList = keywordList):
            print(log.user.user_key + '\t' + log.userMessage)

    def showAllByDelay():
        # Response 중에서 delay가 긴 명령어를 찾아낸다
        print('=======================LOG========================')
        print('user_key\tuserMessage\t')
        print('- - - - - - - - - - - - - - - - - - - - - - - - - ')

    def __str__(self):
        return self.user.user_name + '(' + self.user.user_key + ')' + '|' + self.userMessage.replace('\n', '') + '|' + self.botMessage.replace('\n', '')

    def write(user, userMessage, botMessage, delay = None):
        keywordList = Combine.convertKeywords(userMessage)
        Log.objects.create(user = user, userMessage = userMessage, botMessage = botMessage, keywordList = keywordList, delay = delay)

    class manages():
        def showAll():
            print('Log를 검색할 keywordList를 입력해 주세요')
            targetList = Tools.listBuilder.build()
            Log.showAll(targetList)

class Tools():
    def YoN(text):
        while(True):
            yon = input(text)
            if yon == 'y':
                return True
            elif yon == 'n':
                return False
            else:
                continue

    class listBuilder():
        def build(elements = None):
            if type(elements) == type(str()):
                elements = eval(elements)
            if not elements:
                elements = list()

            while(True):
                print(str(elements))
                choice = input('[1]추가 [2]수정 [3]삭제 [exit()]완료 > ')
                if choice == '1':
                    Tools.listBuilder.create(elements)
                elif choice == '2':
                    Tools.listBuilder.modify(elements)
                elif choice == '3':
                    Tools.listBuilder.remove(elements)
                elif choice == 'exit()':
                    return elements

        def create(elements):
            Tools.listBuilder.show(elements)
            element = input('추가할 문자열를 입력하세요 > ')
            elements.append(element)

        def remove(elements):
            Tools.listBuilder.show(elements)
            index = input('삭제할 문자열의 번호를 입력하세요 > ')
            if index == 'exit()':
                return

            try: index = int(index)
            except:
                print('정수만 입력이 가능합니다')
                return

            if index in range(0, len(elements)):
                if Tools.YoN(elements[index] + '를 삭제할까요? [y/n] > '):
                    if index in range(0, len(elements)):
                        del elements[index]
                else:
                    print('취소되었습니다')
            else:
                print('존재하지 않는 번호입니다')

        def modify(elements):
            Tools.listBuilder.show(elements)
            index = input('수정할 문자열의 번호를 입력하세요 > ')
            if index == 'exit()':
                return

            try:
                index = int(index)
            except:
                print('정수만 입력이 가능합니다')
                return

            if index in range(0, len(elements)):
                updateElement = input('수정전 > ' + elements[index] + '\n수정중 > ')
                if Tools.YoN('수정할까요? [y/n] > '):
                    elements[index] = updateElement
                else: print('취소하였습니다.')
            else:
                print('존재하지 않는 문자열 번호입니다')
            print()

        def show(elements):
            print('==================================================')
            for element in elements:
                print('[' + str(elements.index(element)) + '] ' + element)
            print('')


class Keyword(models.Model):
    elements = models.TextField()
    expression = models.CharField(max_length = 30, null = False, unique = True)

    def __str__(self):
        return self.expression + ' | ' + self.elements

    def showAll():
        print('=====================KEYWORD======================')
        for keyword in Keyword.objects.all():
            if not Combine.objects.filter(keyword = keyword):
                print('*', end = '')
            print(keyword.expression, end = ' --> ')
            print(keyword.elements)
        print('')

    def getKeywordOrNone(expression):
        try: return Keyword.objects.get(expression = expression)
        except: return None

    def createKeyword(elements, expression):
        if type(elements) != type(str()):
            elements = str(elements)

        Keyword.objects.create(elements = elements, expression = expression)

    def modifyKeyword(elements, expression):
        if type(elements) != type(str()):
            elements = str(elements)

        target = Keyword.objects.get(expression = expression)
        target.elements = elements
        target.save()

    def removeKeyword(expression):
        try:
            target = Keyword.objects.get(expression = expression)
        except:
            print(str(expression) + ' expression은 존재하지 않습니다')
            return

        combineIds = Combine.getDistinctCombineIds(target)
        responses = Response.getResponsesWithCombineId(combineIds)

        for response in responses:
            responses.delete()
        target.delete()

    class manages():
        def createKeyword():
            Keyword.showAll()
            expression = input('생성할 Keyword의 expression을 입력하세요 > ')
            if expression == 'exit()':
                return

            if Keyword.getKeywordOrNone(expression):
                print('이미 존재하는 Keyword입니다')
                return

            elements = Tools.listBuilder.build()
            if not elements:
                print('취소되었습니다')
                return

            Keyword.createKeyword(elements, expression)
            print('Keyword가 생성되었습니다')

        def removeKeyword():
            Keyword.showAll()
            expression = input('삭제할 Keyword의 expression을 입력하세요 > ')
            if expression == 'exit()':
                return

            try:
                target = Keyword.objects.get(expression = expression)
            except:
                print('Keyword 삭제 실패. 존재하지 않는 Keyword입니다')
                return

            combineIds = Combine.getDistinctCombineIds(target)
            if combineIds:
                Combine.showAll(combineIds)
                if not Tools.YoN('[경고] 위 Combine 데이터가 삭제될 것입니다. [y/n] > '):
                    return

            responses = Response.getResponsesWithCombineId(combineIds)
            if responses:
                Response.showAll(responses)
                if not Tools.YoN('[경고] 위 Response 데이터가 삭제될 것입니다. [y/n] > '):
                    return

            if not (responses or combineIds):
                if Tools.YoN('정말로 삭제하시겠습니까? [y/n] > '):
                    Keyword.removeKeyword(expression)
                else:
                    print('취소되었습니다')

        def modifyKeyword():
            Keyword.showAll()
            expression = input('element를 수정할 Keyword의 expression을 입력하세요. [exit()] 종료 > ')
            if expression == 'exit()':
                return

            try:
                keyword = Keyword.objects.get(expression = expression)
            except:
                print('존재하지 않는 Keyword 입니다.')
                return

            elements = Tools.listBuilder.build(keyword.elements)
            Keyword.modifyKeyword(elements, expression)

        def selectKeywords():
            Keyword.showAll()
            keywords = list()
            while(True):
                expression = input('Keyword 조합을 생성합니다. 선택할 expression을 입력하세요. [exit()] 완료 > ')
                try:
                    item = Keyword.objects.get(expression = expression)
                    if item in keywords:
                        print('이미 입력된 Keyword 입니다.')
                    else:
                        keywords.append(item)
                except:
                    if expression == 'exit()':
                        return keywords
                    else:
                        print('해당하는 expression이 존재하지 않음')

                print(str(keywords))

class Combine(models.Model):
    combineId = models.IntegerField(null = True)
    keyword = models.ForeignKey(Keyword, null = False, default = None)

    def __str__(self):
        return str(self.combineId) + ' | ' + str(self.keyword)

    def str(combineId):
        # combineId를 통해 대응되는 Combine 정보 리턴
        result = str()
        combines = Combine.objects.filter(combineId = combineId)
        for combine in combines:
            if list(combines).index(combine) > 0:
                result += ', '
            result += combine.keyword.expression
        if combineId == 0:
            return '0:없음'
        else:
            return str(combineId) + ':' + result

    def showAll(combineIds = None):
    # combineId 리스트를 받고 해당 combineId를 가지는 
        print('=====================COMBINE======================')
        print('combineId\texpression')
        print('- - - - - - - - - - - - - - - - - - - - - - - - - ')

        if not combineIds:
            combineIds = Combine.getDistinctCombineIds()

        for combineId in combineIds:
            if not Response.getResponsesWithCombineId(combineId):
                print('*', end = '')
            print(str(combineId), end = '\t\t')
            combines = Combine.objects.filter(combineId = combineId)
            for combine in combines:
                if list(combines).index(combine) > 0:
                    print(', ', end = '')
                print(combine.keyword.expression, end = '')
            print('')
        print('')

    def createCombine(keywords):
        if not Combine.getCombineIdByKeywordList(keywords): # 중복되는 Keyword 조합인지 확인한다.
            combineId = Combine.genCombineId()
            for keyword in keywords:
                Combine.objects.create(combineId = combineId, keyword = keyword)
            return True
        else:
            print('생성 실패. 중복된 Keyword 조합입니다.')
            return False


    def removeCombine(combineId):
        if Response.getResponsesWithCombineId(combineId):
            print('해당 Combine에 등록되어있는 Response가 존재합니다.')
            return False

        target = Combine.objects.filter(combineId = combineId)
        if target:
            target.delete()
            return True
        else:
            print('존재하지 않는 combineId 입니다.')
            return False

    def getDistinctCombineIds(keyword = None):
        if keyword:
            # keyword가 주어졌으면 해당 keyword를 가지는 중복제거된 모든 combineId 리스트 리턴
            return Combine.objects.filter(keyword = keyword).values_list('combineId', flat = True).distinct()
        else:
            # 중복제거된 모든 combineId 리스트 리턴
            return Combine.objects.values_list('combineId', flat = True).distinct()

    def getCombineIdByKeywordList(keywords):
        # Combine 테이블에 keywords와 동일한 조합이 하나라도 존재하는지 확인할 수 있음.
        # 하나라도 있으면 combineId, 없으면 False 을 반환
        for combineId in Combine.getDistinctCombineIds():
            if len(keywords) != len(Combine.objects.filter(combineId = combineId)):
                continue

            duplicated = False
            for combine in Combine.objects.filter(combineId = combineId):
                if combine.keyword in keywords:
                    duplicated = True
                    continue
                else:
                    duplicated = False
                    break
            if duplicated:
                return combineId
        return 0

    def genCombineId():
        if Combine.objects.all():
            return Combine.objects.all().order_by('combineId').last().combineId + 1
        else: return 1

    def convertKeywords(userMessage):
        # 자연어 문장을 Combine과 비교가능한 형태인 Keyword 리스트로 반환한다.
        keywords = list()
        for keyword in Keyword.objects.all():
            for item in eval(keyword.elements):
                if re.search(item, userMessage):
                    keywords.append(keyword)
                    break
        return keywords

    class manages():
        def createCombine():
            Combine.showAll()
            keywords = Keyword.manages.selectKeywords()
            Combine.createCombine(keywords)

        def removeCombine():
            Combine.showAll()
            combineId = input('제거할 Combine의 combineId를 입력하세요. [exit()] 종료 > ')
            if combineId == 'exit()':
                return

            try:
                combineId = int(combineId)
            except:
                print('정수를 입력하세요')
                return

            Combine.removeCombine(combineId)

        def selectCombines():
            # Response 생성을 위한 Combine 조합 선택
            # 여기서는 순서가 중요함
            Combine.showAll()
            combineIds = list()
            while(True):
                combineId = input('Combine 조합으로 생성할 combineId를 선택하세요[0]없음 [exit()]종료 > ')

                if combineId == 'exit()':
                    if combineIds:
                        return combineIds
                    else:
                        return None

                try:
                    combineId = int(combineId)
                except:
                    print('정수를 입력하세요.')
                    continue

                if Combine.objects.filter(combineId = combineId) or combineId == 0:
                    combineIds.append(combineId)
                else:
                    print('존재하지 않는 combineId 입니다')

                print(str(combineIds))

class Response(models.Model):
    combineIdList = models.CharField(max_length = 50, null = False, default = [0])
    group = models.ForeignKey(Group, on_delete = models.CASCADE, null = True)
    responseType = models.CharField(max_length = 10, null = False, default = 'text') # text or func
    message = models.TextField(default = None, null = True)
    func = models.CharField(max_length = 30, null = True, default = None)

    def __str__(self):
        if self.responseType == 'text':
            message = self.message
        elif self.responseType == 'func':
            message = '[함수]' + self.func

        return str(self.combineIdList) + '|' + message

    def existsNextCombineId(self, combineId): # 현재 response의 다음 해당 combineId가 존재하는지
        targetList = eval(self.combineIdList)
        targetList.append(combineId)
        try:
            return Response.objects.get(combineIdList = targetList)
        except:
            return None

    def showAll(responses = None):
        if not responses:
            responses = Response.objects.all()

        responses = Response.sort(responses)
        print('====================RESPONSE======================')
        print('id\tgroup\tcombineIdList\tmessage/func')
        print('- - - - - - - - - - - - - - - - - - - - - - - - - ')
        for response in responses:
            if response.responseType == 'text':
                print(str(response.id) + '\t' + str(response.group) + '\t' + Response.convert(response.combineIdList) + '\t\t' + str(response.message))
            elif response.responseType == 'func':
                print(str(response.id) + '\t' + str(response.group) + '\t' + Response.convert(response.combineIdList) + '\t\t[함수]' + str(response.func))
        print()

    def sort(responses):
        responses = list(responses)
        for response in responses:
            for response2 in responses[responses.index(response) : len(responses)]:
                if eval(response.combineIdList) > eval(response2.combineIdList):
                    responseIndex = responses.index(response)
                    response2Index = responses.index(response2)
                    responses[responseIndex], responses[response2Index] = responses[response2Index], responses[responseIndex]
        return responses

    def convert(combineIdList):
        combineIdList = eval(combineIdList)
        result = str()
        for combineId in combineIdList:
            if combineIdList.index(combineId) > 0:
                result += '>'
            result += Combine.str(combineId)
        return result

    def createResponse(combineIdList, responseType, msgOrFunc, group = None): # responseType은 'func', 'text' 둘중 하나
        if type(combineIdList) != type(list()):
            print('combineIdList는 리스트타입이어야 합니다.')
            return False

        if not msgOrFunc:
            if responseType == 'text':
                print('메시지가 정의되지 않았습니다')
            elif responseType == 'func':
                print('함수가 정의되지 않았습니다')
            return False

        try:
            if responseType == 'text':
                Response.objects.create(combineIdList = combineIdList, message = str(msgOrFunc), responseType = responseType, group = group)
            elif responseType == 'func':
                Response.objects.create(combineIdList = combineIdList, func = msgOrFunc, responseType = responseType, group = group)
            return True
        except:
            print('이미 존재하는 combineIdList 입니다')
            return False

        print('올바르지 않은 responseType')
        return False

    def removeResponseById(id):
        try:
            Response.objects.get(id = id).delete()
            return True
        except:
            print('올바르지 않은 Response id')
            return False

    def modifyResponseById(id, messageOrFunc):
        try:
            response = Response.objects.get(id = id)
        except:
            print('올바르지 않은 Response id')
            return False

        if not messageOrFunc:
            print('메시지 혹은 함수명이 정의되지 않았습니다')
            return False

        if response.responseType == 'func':
            response.func = messageOrFunc
        elif response.responseType == 'text':
            response.message = messageOrFunc
        response.save()
        return True

    def getResponsesWithCombineId(combineIds):
        # 해당 combineId를 가지는 Response가 있으면 해당 Response 객체 리스트를 리턴.

        if type(combineIds) == type(int()):
            combineIds = [combineIds]

        resultResponses = list()
        for response in Response.objects.all().order_by('combineIdList'):
            for combineId in combineIds:
                if combineId in eval(response.combineIdList):
                    resultResponses.append(response)

        return resultResponses

    def getResponse(user, combineIdList):
        # combineIdList에서 [0]이 단독으로 있는 것을 제외하고
        # 두번째 index 이후로 [0]이 포함된 경우를 찾아야 함.
        # 만약에 combineIdList + 0 이 존재하다면, combineIdList의 다음 응답은 반드시 0으로 인식되어야 함

        for response in Response.objects.filter(group = user.group):
            if combineIdList == eval(response.combineIdList):
                if response.existsNextCombineId(0):
                    user.setDoNextKeywordCheck(False)
                return response

        for response in Response.objects.filter(group = None):
            if combineIdList == eval(response.combineIdList):
                if response.existsNextCombineId(0):
                    user.setDoNextKeywordCheck(False)
                return response

        return None

    def getResponseText(user, userMessage):
        # 만약 user.keywordCheck가 True이면 정상적으로 진행
        # False이면, userMessage를 convert할 필요도 없고 그것을 getCombineId 할 필요도 없음
        # User 입장에서 combineIdList는 뭐라고 입력하지 -> 그냥0을 추가할까 -> 나쁘지 않은 듯?
        # 즉, False이면 combineIdList에다가는 0을 추가하는 것임

        if user.doNextKeywordCheck:
            keywordList = Combine.convertKeywords(userMessage)
            combineIdFromKeywordList = Combine.getCombineIdByKeywordList(keywordList)

            # user의 combineIdList에 keywordList의 CombineId를 추가해야함.
            combineIdList = eval(user.combineIdList)
            combineIdList.append(combineIdFromKeywordList)
        else:
            user.setDoNextKeywordCheck(True)
            combineIdList = eval(user.combineIdList)
            combineIdList.append(0)

        response = Response.getResponse(user, combineIdList) # user의 combineIdList에 새로 keywordList에서 찾은 combineId를 추가한 리스트로 탐색
        if response:
            user.setCombineIdList(str(combineIdList))
            messageList = eval(user.getMessageList())
            messageList.append(userMessage)
            user.setMessageList(messageList)
            return Response.getMessage(user, response)

        user.setCombineIdList(str([combineIdFromKeywordList]))
        user.setMessageList([userMessage])

        response = Response.getResponse(user, [combineIdFromKeywordList]) # user의 combineIdList를 업데이트 하고 keywordList에서 찾은 combineId로만 탐색
        if response:
            return Response.getMessage(user, response)
        else:
            return 'Combine으로 등록되었으나 해당하는 Response가 없습니다'

    def getMessage(user, response):
        if response.responseType == 'text':
            message = eval(response.message)
            randNum = random.randrange(0, len(message))
            return message[randNum]

        elif response.responseType == 'func':
            message = funcMod.getFuncMessage(user, response)
            return message

    class manages():
        def createResponse():
            #print('Response를 생성할 combineIdList를 만듭니다')
            combineIdList = Combine.manages.selectCombines()
            if not combineIdList:
                print('취소되었습니다')
                return

            while(True):
                group_name = input('Group 이름을 입력해주세요. [None]없음, [exit()]종료 > ')
                if group_name == 'exit()':
                    return
                elif group_name == 'None':
                    group = None
                    break
                else:
                    group = Group.get(group_name)
                    if group:
                        break
                    else:
                        print('존재하지 않는 Group입니다.')
                        continue

            while(True):
                choice = input('응답형식을 선택하세요 : [1]텍스트 [2]함수 [exit()]종료 > ')

                if choice == '1':
                    message = Tools.listBuilder.build()
                    if Response.createResponse(combineIdList, 'text', message, group):
                        print('생성되었습니다')
                    return

                elif choice == '2':
                    func = input('사용할 함수명을 입력하세요. > ')
                    if Response.createResponse(combineIdList, 'func', func, group):
                        print('생성되었습니다')
                    return

                elif choice == 'exit()':
                    return
                else: print('잘못된 입력입니다')

        def removeResponse():
            Response.showAll()
            responseId = input('삭제할 Response의 id를 입력하세요 [exit()]종료 > ')
            if responseId == 'exit()':
                return

            try: responseId = int(responseId)
            except: print('정수를 입력하세요.')

            if Tools.YoN('정말로 삭제하시겠습니까? [y/n] > '):
                Response.removeResponseById(responseId)
                print('삭제되었습니다')
            else: print('삭제가 취소되었습니다')

        def modifyResponse():
            # Response 수정
            Response.showAll()
            responseId = input('수정할 Response의 id를 입력하세요 > ')
            #if responseId == 'exit()': return

            try: responseId = int(responseId)
            except:
                print('정수를 입력하세요')
                return

            try: response = Response.objects.get(id = responseId)
            except:
                print('존재하지 않는 Response 입니다')
                return

            if response.responseType == 'func':
                messageOrFunc = input('변경할 함수명을 입력하세요 > ')
            elif response.responseType == 'text':
                messageOrFunc = Tools.listBuilder.build(response.message)

            if Response.modifyResponseById(responseId, messageOrFunc):
                print('수정되었습니다')

class manager():
    def inflate():
        manager.init()

        while(True):
            print()
            print('=====================MENU=========================')
            print('[1] Keyword 목록 확인\t[3] Keyword 수정')
            print('[2] Keyword 생성\t[4] Keyword 삭제')
            print('- - - - - - - - - - - - - - - - - - - - - - - - - ')
            print('[5] Combine 목록 확인\t[7] Combine 삭제')
            print('[6] Combine 생성')
            print('- - - - - - - - - - - - - - - - - - - - - - - - - ')
            print('[8] Response 목록 확인\t[10] Response 수정')
            print('[9] Response 생성\t[11] Response 삭제')
            print('- - - - - - - - - - - - - - - - - - - - - - - - - ')
            print('[12] Group 목록 확인\t[14] Group 관리')
            print('[13] Group 생성\t\t[15] Group 삭제')
            print('- - - - - - - - - - - - - - - - - - - - - - - - - ')
            print('[16] Keyword가 인식되지 않는 Log 목록 확인')
            print('[17] delay가 긴 명령어 확인하기')
            print('- - - - - - - - - - - - - - - - - - - - - - - - - ')
            print('[20] 직접 대화해보면서 테스트하기\n')
            c = input('명령번호를 입력하세요. [exit()] 종료 > ')
            print()

            if c == '1':
                Keyword.showAll()
            elif c == '2':
                Keyword.manages.createKeyword()
            elif c == '3':
                Keyword.manages.modifyKeyword()
            elif c == '4':
                Keyword.manages.removeKeyword()
            elif c == '5':
                Combine.showAll()
            elif c == '6':
                Combine.manages.createCombine()
            elif c == '7':
                Combine.manages.removeCombine()
            elif c == '8':
                Response.showAll()
            elif c == '9':
                Response.manages.createResponse()
            elif c == '10':
                Response.manages.modifyResponse()
            elif c == '11':
                Response.manages.removeResponse()
            elif c == '12':
                Group.showAll()
            elif c == '13':
                Group.manages.createGroup()
            elif c == '14':
                Group.manages.manageGroup()
            elif c == '15':
                Group.manages.removeGroup()
            elif c == '16':
                Log.showAll('[]')
            elif c == '17':
                pass
            elif c == '20':
                manager.test()
            elif c == 'exit()':
                return
            else:
                print('잘못된 입력입니다.')

    def test():
        user = User.getOrCreate(user_key = 'testuser')
        while(True):
            userMessage = input('[exit()]종료 > ')
            if userMessage == 'exit()':
                return
            start = datetime.datetime.now()
            print('응답 > ' + Response.getResponseText(user, userMessage), end = ' ')
            timeDiff = datetime.datetime.now() - start
            print(str(timeDiff.total_seconds()) + 's')

    def init():
        # 초기에 여기서 init을 해주어야 inflate을 호출가능 하도록 해야 할 듯?
        # init 했는지 안했는지는 관리자의 USER_KEY를 입력함에 따라..?
        # Response의 combineIdList = [0]이 등록되어야 함

        if Response.getResponsesWithCombineId([0]):
            return

        #Combine.createCombine(combineId = combineId, keyword = None)
        #print('Combine(combineId=0)이 생성되었습니다')

        print('Keyword에 등록되지 않아 봇이 알아들을 수 없는 사용자의 질문에 대해 기본적으로 응답할 메시지를 등록해야 합니다\n')
        print('다음 문자열 리스트 빌더에 등록되는 메시지에서 랜덤으로 사용자에게 응답합니다')
        elements = Tools.listBuilder.build()
        Response.createResponse([0], 'text', elements, group = None)
        print('Response(combineIdList=[0])이 생성되었습니다')

        Group.createGroup('admin')

