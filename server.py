from datetime import datetime as dt

from flask import Flask, request, jsonify
import json

import database

app = Flask(__name__)


@app.route('/post', methods=['POST'])
def main():
    resp = make_base_answer(request.json)
    user_id = request.json["session"]["session_id"]
    if request.json["session"]["new"]:
        resp = create_session(request.json, resp)
        save_dialog(user_id=user_id, state="choice_difficult", resp=resp)
        return jsonify(resp)
    data = load_user_data(user_id)
    state = data["dialog_state"]
    if state == "choice_difficult":
        dialog_func = choice_difficult
    elif state == "choice_categories":
        dialog_func = choice_categories
    elif state == "asking":
        dialog_func = asking
    elif state == "summarizing":
        dialog_func = summarizing
    else:
        raise Exception(f"Неизвестное состояние диалога: {state}")
    resp = dialog_func(req=request.json, resp=resp, data=data)
    save_dialog(user_id=user_id, state=state, resp=resp)
    return jsonify(resp)


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
            "total_count_questions": -1,
            "current_question": -1,
            "count_correct_answers": -1,
            "dialog_state": dialog_state,
            "categories": [],
            "last_resp": None,
            "difficult": -1,
            }

    with open(f"/data/users/{user_id}.json", 'w') as file:
        json.dump(data, file)


def save_dialog(user_id, state, resp):
    with open(f'/data/users/{user_id}.json') as file:
        data = json.load(file)
        data["dialog_state"] = state
        data["last_resp"] = json.dumps(resp)

    with open(f'/data/users/{user_id}.json', 'w') as file:
        json.dump(data, file)


def load_user_data(user_id):
    with open(f'/data/users/{user_id}.json') as file:
        data = json.load(file)
    return data


def choice_difficult(req, resp, data):
    answer = req['request']['original_utterance']
    tokens = req["reqquest"]['nlu']["tokens"]

    if len(tokens) > 1:
        resp = json.loads(data["last_resp"])
        resp["response"]["text"] = resp["response"]['tts'] = 'Мы вас не поняли, повторите пожалуйста свой выбор'
        return resp
    chosen_var = tokens[0].lower()
    if chosen_var == 'базовый':
        data["count_quests"] = 7
        data["diff"] = 0
    elif chosen_var == 'средний':
        data["count_quests"] = 10
        data["diff"] = 1
    elif chosen_var == 'сложный':
        data["count_quests"] = 15
        data["diff"] = 2
    else:
        resp = json.loads(data["last_resp"])
        resp["response"]["text"] = resp["response"]['tts'] = 'Мы вас не поняли, повторите пожалуйста свой выбор'
        return resp

    with open(f'/data/users/{req["session"]["session_id"]}.json', 'w') as file:
        json.dump(data, file)

    resp["response"]["text"] = resp["response"]['tts'] = 'Теперь выберите категории вопросов'
    categories = database.give_categories()

    resp["response"]["buttons"] = [{"title": "Все",
                                    "hide": True}] + [{"title": cat.capitalize(),
                                                       "hide": True} for cat in categories]

    return resp


def asking(req, resp, data):
    return resp


def choice_categories(req, resp, data):
    return resp


def summarizing(req, resp, data):
    return resp
