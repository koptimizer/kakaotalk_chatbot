import urllib.request
import urllib.parse
import json

def getPPGTrans(engContent):
    client_id = 'gratov2e3PqpnvmIqZQE'
    client_secret = 'YUj_vKNblW'
    encText = urllib.parse.quote(engContent)
    data = "source=en&target=ko&text=" + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"
    #url = 'https://openapi.naver.com/v1/language/translate'
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request, data = data.encode("utf-8"))
    rescode = response.getcode()

    if(rescode == 200):
        response_body = response.read()
        print(response_body.decode('utf-8'))

    else:
        print("Error Code:" + rescode)

    dict = json.loads(response_body.decode('utf-8'))
    text = dict['message']['result']['translatedText']
    return text
