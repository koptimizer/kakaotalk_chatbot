Python-Django 를 기반으로한 카카오톡 채팅봇 프레임워크 프로젝트입니다.

취미삼아서 개인적으로 사용할 목적으로 만들었습니다.

* 앱 이름은 main 입니다.(python manage.py startapp main)
* models.py에 정의된 대화식 인터페이스(from main.models import manager -> manager.inflate())를 통해 키워드 및 응답을 관리할 수 있습니다.

1. 정규표현식을 통해서 사용자의 메시지를 일반화합니다. 이것은 Keyword 테이블에서 관리됩니다.<br>
ex) '^뭐[해(하니)]\??$' -> '뭐해'<br>
1-1. 단일문장으로 응답이 주로 이루어지는 경우(ㅎㅇ, 안녕, 사랑해 등),<br>
'^ ~ $'로 명확히 시작과 끝을 정의해주는 것을 추천합니다. Keyword가 많아지면 Combine 매칭이 어려워 질 수 있습니다.

2. 특정 Keyword 조합을 별도로 정의하여 특별한 응답을 정의 할 수 있습니다. 이는 Combine에서 정의합니다.

3. 1depth 이상의 대화를 정의할 수 있습니다.<br>
3-1. Response 에서 Combine 조합을 순서대로 정의하면 특정 대화 순서에 맞춰서 응답을 별도로 지정할 수 있습니다.<br>
예를들어, combineIdList = [1,3] 은 combineId가 1인 Combine이 호출되고,<br>
다음으로 combineId가 3인 Combine이 호출될 경우의 봇의 응답 메시지를 설정이 가능합니다.

4. Response 에서 combineIdList = [0] 은 사용자의 메시지가 어떤 키워드도 인식되지 않을 경우 전송할 봇의 응답을 지정해 줄 수 있습니다.

5. 특정 Group에 따라서 별도로 특정 응답을 다르게 줄 수 있습니다.

6. Combine은 다음의 기능을 합니다.<br>
6-1. Keyword로 등록은 했으나 아직 대화에서는 반영하고싶지 않은 경우, Combine에서 등록하지 않으면 됩니다.<br>
6-2. '너 사랑해', '사랑해 너' 등 주어가 앞, 뒤에 나타날 수 있는 우리말 특성을 어느정도 맞출 수 있습니다.
