from django.db import models
from django.utils import timezone
import datetime
import re
import random

class Group(models.Model):
    group_name = models.CharField(max_length = 30, primary_key = True)

    def __str__(self):
        return self.group_name

# 실제 db.sqlite3 파일에는 chatbot_User, chatbot_Mail 등과 같은 이름으로 테이블이 생성 된다.
class User(models.Model):
    user_name = models.CharField(max_length = 30, default = None, null = True)
    user_key = models.CharField(max_length = 30, primary_key = True)
    group = models.ForeignKey(Group, on_delete = models.CASCADE, null = True, default = None)
    mailCheck = models.BooleanField(default = False)
    combineIdList = models.CharField(max_length = 50, null = True, default = '[0]')

    def get(user_key):
        try:
            return User.objects.get(user_key = user_key)
        except:
            User.objects.create(user_key = user_key)
            return User.objects.get(user_key = user_key)

    def setMailCheck(self, mailChecked):
        self.mailCheck = mailChecked

    def setName(self, name):
        self.user_name = name

    def __str__(self):
        return self.user_key + '|' + str(self.user_name)

class Mail(models.Model):
    # 만약 여기서 참조하는 User의 데이터가 지워지면 CASCADE 옵션에 의해 같이 삭제
    # ForeignKey는 해당 인스턴스를 파라메터로 넘겨주어야 함
    sender = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'mail_set_sender')
    receiver = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'mail_set_receiver')
    message = models.TextField()
    dateTime = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.sender.user_name + '|' + self.message

class Log(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    userMessage = models.TextField(null = True)
    botMessage = models.TextField(null = True)
    dateTime = models.DateTimeField(auto_now_add = True)
    keywordList = models.CharField(max_length = 100, null = True)

    def __str__(self):
        return self.user.user_name + '(' + self.user.user_key + ')' + '|' + self.userMessage.replace('\n', '') + '|' + self.botMessage.replace('\n', '')

class Keyword(models.Model):
    elements = models.TextField()
    expression = models.CharField(max_length = 30, null = False)

    def __str__(self):
        return self.expression + ' | ' + self.elements

    def showAll():
        print('=====================KEYWORD======================')
        for keyword in Keyword.objects.all():
            if not Combine.objects.filter(keyword = keyword):
                print('?', end = '')
            print(keyword.expression, end = ' --> ')
            print(keyword.elements)
        print('')

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

    def showElements(elements):
        print('==================================================')
        for element in elements:
            print('[' + str(elements.index(element)) + '] ' + element)
        print('')

    def createElement(elements, element):
        elements.append(element)

    def removeElement(elements, index):
        if index in range(0, len(elements)):
            del elements[index]

    def modifyElements(elements, element, index):
        elements[index] = element

class Combine(models.Model):
    combineId = models.IntegerField(null = True)
    keyword = models.ForeignKey(Keyword)

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
                print('?', end = '')
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
        else:
            return 1

    def convertKeywords(userMessage):
        # 자연어 문장을 Combine과 비교가능한 형태인 Keyword 리스트로 반환한다.
        keywords = list()
        for keyword in Keyword.objects.all():
            for item in eval(keyword.elements):
                if re.search(item, userMessage):
                    keywords.append(keyword)
                    break
        return keywords

class Response(models.Model):
    combineIdList = models.CharField(max_length = 50, null = False, default = [0], unique = True)
    responseType = models.CharField(max_length = 10, null = False, default = 'text') # text or func
    message = models.TextField(default = None)
    func = models.CharField(max_length = 30, null = True, default = None)

    def __str__(self):
        if self.responseType == 'text':
            message = self.message
        elif self.responseType == 'func':
            message = '[함수]' + self.func

        return str(self.combineIdList) + '|' + message

    def showAll(responses = None):
        if not responses:
            responses = Response.objects.all()

        responses = Response.sort(responses)
        print('====================RESPONSE======================')
        print('id\tcombineIdList\tmessage/func')
        print('- - - - - - - - - - - - - - - - - - - - - - - - - ')
        for response in responses:
            if response.responseType == 'text':
                print(str(response.id) + '\t' + Response.convert(response.combineIdList) + '\t\t' + str(response.message))
            elif response.responseType == 'func':
                print(str(response.id) + '\t' + Response.convert(response.combineIdList) + '\t\t[함수]' + str(response.func))
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

    def createResponse(combineIdList, responseType, msgOrFunc): # type은 'func', 'text' 둘중 하나
        if type(combineIdList) != type(list()):
            print('combineIdList는 리스트타입이어야 합니다.')
            return False
        try:
            if responseType == 'text':
                Response.objects.create(combineIdList = combineIdList, message = msgOrFunc, responseType = 'text')
                return True
            elif reseponseType == 'func':
                Response.objects.create(combineIdList = combineIdList, func = msgOrFunc, responseType = 'func')
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

    def getResponse(combineIdList):
        # combineIdList는 리스트 타입
        for response in Response.objects.all():
            if combineIdList == eval(response.combineIdList):
                return response
        return None

    def getResponseText(user, userMessage):
        print('getResponseText 진입')
        keywordList = Combine.convertKeywords(userMessage)
        combineIdFromKeywordList = Combine.getCombineIdByKeywordList(keywordList)
        #print(userMessage + '라는 말은 '+ str(keywordList) + '로 변환 되었으며, combineId는 ' + str(combineIdFromKeywordList))

        # user의 combineIdList에 keywordList의 CombineId를 추가해야함.
        combineIdList = eval(user.combineIdList)
        combineIdList.append(combineIdFromKeywordList)

        response = Response.getResponse(combineIdList) # user의 combineIdList에 새로 keywordList에서 찾은 combineId를 추가한 리스트로 탐색
        if response:
            print(str(combineIdList))
            # response.message 혹은 response.func를 반환해야함.
            return response.getMessage()

        user.combineIdList = str([combineIdFromKeywordList])
        user.save()

        response = Response.getResponse([combineIdFromKeywordList]) # user의 combineIdList를 업데이트 하고 keywordList에서 찾은 combineId로만 탐색
        if response:
            print([combineIdFromKeywordList])
            return response.getMessage()
        else:
            return '해당하는 response가 존재하지 않음 ' + str(response)

    def getMessage(self):
        if self.responseType == 'text':
            message = eval(self.message)
        elif self.responseType == 'func':
            # 뭔가를 호출하고 그것이 리턴해야대
            pass

        if type(message) == type(list()):
            rdnum = random.randrange(0, len(message))
            message = message[rdnum]
            return message
        elif type(message) == type(str()):
            return message

class Handler():
    # 대화형 메소드 클래스
    def YoN(text):
        while(True):
            yon = input(text)
            if yon == 'y':
                return True
            elif yon == 'n':
                return False
            else:
                continue

    def createKeyword():
        # 새로운 Keyword 생성
        # elements를 빌드
        # expression을 입력
        Keyword.showAll()
        expression = input('expression? > ')

        if expression == 'exit()':
            return

        elements = Handler.elementsBuilder()

        Keyword.createKeyword(elements, expression)
        print('Keyword가 생성되었습니다')

    def removeKeyword():
        Keyword.showAll()
        expression = input('expression? > ')
        if expression == 'exit()':
            return

        try:
            target = Keyword.objects.get(expression = expression)
        except:
            print('Keyword 삭제 실패. expression이 존재하지 않습니다')
            return False

        combineIds = Combine.getDistinctCombineIds(target)
        if combineIds:
            Combine.showAll(combineIds)
            if not Handler.YoN('[경고] 위 Combine 데이터가 삭제될 것입니다. [y/n] > '):
                return False

        responses = Response.getResponsesWithCombineId(combineIds)
        if responses:
            Response.showAll(responses)
            if not Handler.YoN('[경고] 위 Response 데이터가 삭제될 것입니다. [y/n] > '):
                return False

        if not (responses or combineIds):
            if Handler.YoN('정말로 삭제하시겠습니까? [y/n] > '):
                Keyword.removeKeyword(expression)
                return True
            else:
                print('취소되었습니다')
                return False

    def modifyKeyword():
        # elements, expression 무엇을 수정할지 선택
        # elements는 별도로 내부에서 추가, 수정, 삭제 선택
        Keyword.showAll()

        expression = input('element를 수정할 Keyword의 expression을 입력하세요. [exit()] 종료 > ')
        if expression == 'exit()':
            return

        try:
            keyword = Keyword.objects.get(expression = expression)
        except:
            print('존재하지 않는 Keyword 입니다.')
            return

        elements = Handler.elementsBuilder(keyword.elements)

        Keyword.modifyKeyword(elements, expression)

    def elementsBuilder(elements = None):
        if type(elements) == type(str()):
            elements = eval(elements)

        if not elements:
            elements = list()

        while(True):
            print(str(elements))
            choice = input('[1]추가 [2]수정 [3]삭제 [exit()]완료 > ')
            if choice == '1':
                Handler.createElement(elements)
            elif choice == '2':
                Handler.modifyElement(elements)
            elif choice == '3':
                Handler.removeElement(elements)
            elif choice == 'exit()':
                return elements

    def createElement(elements):
        Keyword.showElements(elements)
        element = input('추가할 element를 입력하세요 > ')
        Keyword.createElement(elements, element)

    def removeElement(elements):
        Keyword.showElements(elements)
        index = input('삭제할 element 인덱스를 입력하세요 > ')
        if index == 'exit()':
            return

        try:
            index = int(index)
        except:
            print('정수만 입력이 가능합니다')
            return

        if index in range(0, len(elements)):
            if Handler.YoN(elements[index] + '를 삭제할까요? [y/n] > '):
                Keyword.removeElement(elements, index)
            else:
                print('취소되었습니다')
        else:
            print('존재하지 않는 index입니다')

    def modifyElement(elements):
        Keyword.showElements(elements)
        index = input('수정할 element의 인덱스를 입력하세요 > ')
        if index == 'exit()':
            return

        try:
            index = int(index)
        except:
            print('정수만 입력이 가능합니다')
            return

        if index in range(0, len(elements)):
            updateElement = input('수정전 > ' + elements[index] + '\n수정중 > ')
            if Handler.YoN('수정할까요? [y/n] > '):
                elements[index] = updateElement
            else:
                print('취소하였습니다.')
        else:
            print('해당 index는 존재하지 않습니다.')
        print()

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

    def createCombine():
        Combine.showAll()
        keywords = Handler.selectKeywords()
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
            combineId = input('Combine 조합 생성중. combineId를 선택하세요. [exit()] 종료 > ')

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
                print('존재하지 않는 combineId 입니다.')

            print(str(combineIds))

    def createResponse():
        print('Response를 생성할 combineIdList를 만듭니다.')
        combineIdList = Handler.selectCombines()
        if not combineIdList:
            print('취소되었습니다')
            return

        while(True):
            choice = input('응답형식을 선택하세요 : [1]텍스트 [2]함수 [exit()]종료 > ')

            if choice == '1':
                #message = input('응답할 텍스트를 입력하세요 > ')
                message = str(Handler.elementsBuilder())
                Response.createResponse(combineIdList, 'text', message)
                return

            elif choice == '2':
                func = input('사용할 함수명을 입력하세요. > ')
                Response.createResponse(combineIdList, 'func', func)
                return

            elif choice == 'exit()':
                return

    def removeResponse():
        Response.showAll()
        responseId = input('삭제할 Response의 id를 입력하세요. [exit()]종료 > ')
        if responseId == 'exit()':
            return

        try:
            responseId = int(responseId)
        except:
            print('정수를 입력하세요.')

        if Handler.YoN('정말로 삭제하시겠습니까? [y/n] > '):
            Response.removeResponseById(responseId)
        else:
            print('삭제가 취소되었습니다')

class Menu():
    def start():
        while(True):
            print()
            print('=====================MENU=========================')
            print('[1] show all keywords\t[3] modify a keyword(element)')
            print('[2] create a keyword\t[4] remove a keyword')
            print('- - - - - - - - - - - - - - - - - - - - - - - - - ')
            print('[5] show all combines\t[7] remove a combine')
            print('[6] create a combine')
            print('- - - - - - - - - - - - - - - - - - - - - - - - - ')
            print('[8] show all response\t[10] remove a response')
            print('[9] create a response')
            print('- - - - - - - - - - - - - - - - - - - - - - - - - ')
            print('[20] 직접 대화해보면서 테스트하기\n')
            #print('* Response가 등록되지 않은 Combine을 탐색하도록!')
            #print('* 문장을 던지면 해당 문장의 Keyword와 응답을 표시하는 메뉴')

            c = input('명령번호를 입력하세요. [exit()] 종료 > ')
            print()

            if c == '1': # show all keywords
                Keyword.showAll()

            elif c == '2': # create a keyword
                Handler.createKeyword()

            elif c == '3': # modify a keyword
                Handler.modifyKeyword()

            elif c == '4': # remove a keyword
                Handler.removeKeyword()

            elif c == '5': # show all combines
                Combine.showAll()

            elif c == '6': # create a combine
                Handler.createCombine()

            elif c == '7': # remove a combine
                Handler.removeCombine()

            elif c == '8': # show all responses
                Response.showAll()

            elif c == '9': # create a response
                Handler.createResponse()

            elif c == '10': # remove a response
                Handler.removeResponse()

            elif c == '20':
                text = input('테스트할 문장을 입력하세요. [exit()] 종료 > ')
                if text == 'exit()':
                    continue
                jg = User.objects.get(user_name = '임종길')
                print(Response.getResponseText(jg, text))

            elif c == 'exit()':
                return

            else:
                print('잘못된 입력입니다.')
