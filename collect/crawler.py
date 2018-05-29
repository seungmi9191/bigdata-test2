#수집

import requests
import json
from datetime import datetime, timedelta

#변수선언
BASE_URL_FB_API = "https://graph.facebook.com/v3.0"
ACCESS_TOKEN ="EAACEdEose0cBAJTdwwNi7qMWj3Qzx63T9KnS0ADc0isZBZCZAl6qfHcpgV6sp8zsUfr0FPHUuG5EDyPRruWWR3kQlvUU7lC578XZAfZAkKMophtW0b0sDg0TPNIjLswULXBwARxDG9FFImXLo76ctWmVleqeZCyHR2hqwo7dhKdeGHqjiqzE62ewUnggxHEb7Q1w5OKwVuc2xxFQ0ZC1VvoShabyc5xon0ZD"
LIMIT_REQUEST = 30

#URL → JSON 데이터 반환
def get_json_result(url) :
    try :
        #get방식 url 요청
        response = requests.get(url)

        #error 방지(주소 없을 시)
        if response.status_code == 200 :
            return response.json()

    except Exception as e :
        return "%s : Error for request [%s]" % (datetime.now(), url)


#URL → ID값 받아옴
def fb_name_to_id(pagename) :

    base = BASE_URL_FB_API
    node = "/%s" % pagename #%s=string으로 치환
    params = "/?access_token=%s" %ACCESS_TOKEN
    url = base + node + params

    json_result = get_json_result(url)
    print(json_result)

    return json_result["id"]

#URL → POST값 받아옴
def fb_get_post_list(pagename, from_date, to_date) :

    page_id = fb_name_to_id(pagename)

    base = BASE_URL_FB_API
    node = '/%s/posts' % page_id
    fields = '/?fields=id,message,link,name,type,shares,' +\
             'created_time,comments.limit(0).summary(true),' +\
             'reactions.limit(0).summary(true)'
    duration = '&since=%s&until=%s' % (from_date, to_date)
    parameters = '&limit=%s&access_token=%s' % (LIMIT_REQUEST, ACCESS_TOKEN)

    url = base + node + fields + duration + parameters

    #json으로 받아온 데이터의 paging(next)를 계속 불러와야함

    postList = []
    isNext = True

    while isNext :
        temPostList = get_json_result(url)
        for post in temPostList["data"] :

           postVo = preprocess_post(post)
           postList.append(postVo)

        paging = temPostList.get("paging").get("next")
        if paging != None : #이 주소가 아직 있으면
            url = paging #url에 넣어줘 (여기 url은 내가 처음 사용한게 아니라 json으로 다시 준거임,계속 바뀜)
        else :
            isNext = False #없으면 for문 나가버림


    with open("/Users/WOOSEUNGMI/Desktop/2018/javaStudy/facebook/" + pagename + ".json", 'w', encoding='utf-8') as outfile:
        json_string = json.dumps(postList, indent=4, sort_keys=True, ensure_ascii=False)
        outfile.write(json_string)

    return postList


#JSON 데이터 → 원하는 5개 데이터만 뽑아냄
def preprocess_post(post) :

    #작성일 +9시간 해줘야함(표준시간으로)
    created_time = post["created_time"]
    created_time = datetime.strptime(created_time, '%Y-%m-%dT%H:%M:%S+0000')
    created_time = created_time + timedelta(hours=+9)
    created_time = created_time.strftime('%Y-%m-%d %H:%M:%S')


    #공유 수
    if "shares" not in post :
        shares_count = 0
    else :
        shares_count = post["shares"]["count"] #있으면 가져온 실제 숫자를 넣음

    #리액션 수
    if "reactions" not in post :
        reactions_count = 0
    else :
        reactions_count = post["reactions"]["summary"]["total_count"]

    # 댓글 수
    if "comments" not in post:
        comments_count = 0
    else:
        comments_count = post["comments"]["summary"]["total_count"]

    # 메세지 수
    if "message" not in post:
        message_str = ""
    else:
        message_str = post["message"]

    postVo = {
                "created_time":created_time,
                "shares_count": shares_count,
                "reactions_count": reactions_count,
                "comments_count": comments_count,
                "message_str": message_str
             }

    return postVo