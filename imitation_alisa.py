import json
import requests
URL = "http//:127.0.0.1:8000"


base = {
    "meta": {
        "locale": "ru-RU",
        "timezone": "Europe/Moscow",
        "client_id": "ru.yandex.searchplugin/7.16 (none none; android 4.4.2)",
        "interfaces": {
            "screen": {},
            "account_linking": {},
            "audio_player": {}
        }
    },
    "request": {
        "type": "String",
        "original_utterance": "",
        "nlu": {
            "tokens": [
                "закажи",
                "пиццу",
                "на",
                "льва",
                "толстого",
                "16",
                "на",
                "завтра"
            ]}
    },
    "session": {
        "message_id": 0,
        "session_id": "2eac4854-fce721f3-b845abba-20d60",
        "skill_id": "3ad36498-f5rd-4079-a14b-788652932056",
        "user_id": "47C73714B580ED2469056E71081159529FFC676A4E5B059D629A819E857DC2F8",
        "user": {
            "user_id": "6C91DA5198D1758C6A9F63A7C5CDDF09359F683B13A18A151FBF4C8B092BB0C2",
            "access_token": "AgAAAAAB4vpbAAApoR1oaCd5yR6eiXSHqOGT8dT"
        },
        "application": {
            "application_id": "47C73714B580ED2469056E71081159529FFC676A4E5B059D629A819E857DC2F8"
        },
        "new": True
    },
    "state": {
        "session": {
            "value": 10
        },
        "user": {
            "value": 42
        },
        "application": {
            "value": 37
        }
    },
    "version": "1.0"
}

while True:
    text = input()
    tokens = text.split()
    res = base.copy()
    res["request"]["original_utterance"] = text
    res["request"]["nlu"]["tokens"] = tokens[:]
    data = json.dumps(res)
    requests.post(url=URL, data=data)
