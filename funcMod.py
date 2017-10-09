import importlib

# 각종 함수를 매핑시키기 위한 함수
def getFuncMessage(user, response):

    if response.func == 'mail':
        User = getattr(importlib.import_module('main.models'), 'User')
        Mail = getattr(importlib.import_module('main.models'), 'Mail')

        messageList = eval(user.getMessageList())
        admin = User.getByGroup('admin')
        userMessage = messageList.pop()
        Mail.sendMail(user, admin, userMessage)
        botMessage = '\'' + userMessage + '\'\n메시지가 전달되었습니다!'
        return botMessage
