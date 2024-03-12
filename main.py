import requests
import argparse
import json
import clipboard as cb
import os
from os.path import join



# parser = argparse.ArgumentParser(description="입력한 도시의 현재 기온 등을 알려준다!")
# parser.add_argument('-city', '--city', required=True, help="알고 싶은 도시명을 -city 하고 뒤에 넣으세요ㅛㅛㅛㅛㅛ")
# args = parser.parse_args()

# city = args.city
def get_lon_lat():
    url_front = "http://api.openweathermap.org/geo/1.0/direct?"
    url_q = "q="
    q = "Seoul"
    url_limit = "&limit=1"
    url_appid = "&appid="
    appid = "352c996fe72fdcd2fbb99f6d64bae0f1"

    url = url_front + url_q + q + url_limit + url_appid + appid
    result = requests.get(url)
    json_data = result.json()

    lat = json_data[0]['lat']
    lon = json_data[0]['lon']

    print(f"{q}의 위도 : {lat}, 경도 : {lon}")
    return (lat, lon)


def get_weather():
    lat, lon = get_lon_lat()
    url_appid = "&appid="
    appid = "352c996fe72fdcd2fbb99f6d64bae0f1"
    q = "Seoul"
    url_weather_front = "http://api.openweathermap.org/data/2.5/weather?"
    url_lat = f"lat={lat}"
    url_lon = f"&lon={lon}"
    url_units = "&units=metric"
    url_weather = url_weather_front + url_lat + url_lon + url_units + url_appid + appid

    result_weather = requests.get(url_weather)
    json_data_weather = result_weather.json()
    print(json_data_weather['main'])
    json_data_weather_main = json_data_weather['main']


    temp = json_data_weather_main['temp']
    feels_like = json_data_weather_main['feels_like']
    temp_min = json_data_weather_main['temp_min']
    temp_max = json_data_weather_main['temp_max']

    msg = f"{q}의 온도 : {temp}, 체감 온도 : {feels_like}, 최저 온도 : {temp_min}, 최고 온도 : {temp_max}"
    return msg


# https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={APIKey}
# rest API key 5db78ce08c31cd3f73a9b08f25301944 인가 코드
# https://kauth.kakao.com/oauth/token 인증 토큰 받기
def get_authorize_code():
    Rest_API = "5db78ce08c31cd3f73a9b08f25301944"
    url_rest_api = f"https://kauth.kakao.com/oauth/authorize?response_type=code&client_id={Rest_API}&redirect_uri=https://example.com/oauth"

    cb.copy(url_rest_api)
    return input(str("지금 브라우져 링크 칸에서 'ctrl' 키와 'v'를 동시에 누른후 동의후\n나오는 example.com/oauth 사이트 뒤에 있는 code= 뒤를 싹다 복사 붙여넣기 해주세요! : "))

def get_tokens_network(authorize_code):
    url_token = f"https://kauth.kakao.com/oauth/token"
    Rest_API = "5db78ce08c31cd3f73a9b08f25301944"

    data = {
        'grant_type':'authorization_code',
        'client_id':Rest_API,
        'redirect_uri':'https://example.com/oauth',
        'code':authorize_code
    }

    result_token = requests.post(url_token, data=data)
    json_data_token = result_token.json()

    print(json_data_token)

    access_token = json_data_token['access_token']
    refresh_token = json_data_token['refresh_token']
    return json_data_token


def send_msg(access_token, msg):

    url_result = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + access_token
    }
    data = {
        "object_type": "text",
        "text": msg,
        "link": {
            "web_url": "https://developers.kakao.com",
            "mobile_web_url": "https://developers.kakao.com"
        },
    }
    data = {"template_object": json.dumps(data)}

    result_result = requests.post(url_result, headers=headers, data=data)
    return result_result.json().get("result_code")

def refresh_access_token(refresh_token):
    url_result = "https://kauth.kakao.com/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    data = {
        "grant_type": "refresh_token",
        "client_id": "5db78ce08c31cd3f73a9b08f25301944",
        "refresh_token" : refresh_token
    }

    result = requests.post(url_result, headers=headers, data=data)
    return result.json()

token_file = 'token.json'
access_token = ''



if not os.path.exists(token_file):
    print("debug token no")
    authorize_code = get_authorize_code()
    tokens = get_tokens_network(authorize_code)
    send_msg(tokens['access_token'], get_weather())
    print(tokens)
    with open(token_file, "w") as kakao:
        json.dump(tokens, kakao)
else:
    with open(token_file, "r") as kakao:
        tokens = json.load(kakao)
        if send_msg(tokens['access_token'], get_weather()) == 0:
            pass
        else:
            print("access token 만료")
            result = refresh_access_token(tokens['refresh_token'])
            print(result)
            if len(result) > 3:
                print("리프레시 토큰 갱신")
                with open(token_file, "w") as kakao:
                    json.dump(result, kakao)
                send_msg(result['access_token'], get_weather())

            else:
                print(result)
                tokens['access_token'] = result['access_token'] 
                print("access_token 갱신")
                with open(token_file, "w") as kakao:
                    json.dump(tokens, kakao)
                send_msg(tokens['access_token'], get_weather())
