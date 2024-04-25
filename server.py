from datetime import datetime as dt

from flask import Flask, request, jsonify
import json

app = Flask(__name__)


@app.route('/post', methods=['POST'])
def main():
    resp = make_base_answer(request.json)
    user_id = request.json["session"]["session_id"]
    if request.json["session"]["new"]:
        resp = create_session(request.json, resp)
        change_dialog_state(user_id=user_id, state="choice_difficult")
        return jsonify(resp)
    data = load_user_data(user_id)
    state = data["dialog_state"]
    if state == "choice_difficult":
        pass
    elif state == "choice_categories":
        pass
    elif state == "asking":
        pass
    elif state == "summarizing":
        pass
    else:
        raise Exception(f"Неизвестное состояние диалога: {state}")


def make_base_answer(req):
    return {
        "response": {
            "text": "",
            "tts": "",
            "end_session": False,
        },

        'session': req['session'],
        'version': req['version'],
    }


def create_session(req, resp):
    resp["response"]["text"] = '''Привет, в этом навыке мы проверим твоё знание по предмету "География". Начинаем!
Выберите уровень сложности:'''
    resp["response"]["tts"] = resp["response"]["text"]
    resp["response"]["buttons"] = [
        {
            "title": "Базовый",
            "hide": True
        },

        {
            "title": "Средний",
            "hide": True
        },

        {
            "title": "Сложный",
            "hide": True
        }
    ]

    create_user_memory(req["session"]["session_id"])

    return resp


def create_user_memory(user_id, dialog_state="start_session"):
    data = {"last_request": dt.now(),
            "user_id": user_id,
            "total_count_questions": 0,
            "current_question": 0,
            "count_correct_answers": 0,
            "dialog_state": dialog_state,
            "categories": []
            }

    with open(f"/data/users/{user_id}.json", 'w') as file:
        json.dump(data, file)


def change_dialog_state(user_id, state):
    with open(f'/data/users/{user_id}.json') as file:
        data = json.load(file)
        data["dialog_state"] = state

    with open(f'/data/users/{user_id}.json', 'w') as file:
        json.dump(data, file)

def load_user_data(user_id):
    with open(f'/data/users/{user_id}.json') as file:
        data = json.load(file)
    return data