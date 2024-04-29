from flask import Flask, request, jsonify
import json
import logging
import database
app = Flask(__name__)


@app.route('/post', methods=['POST'])
def main():
    resp = make_base_answer(request.json)
    user_id = request.json["session"]["session_id"]
    data, result = load_user_data(user_id)
    if request.json["session"]["new"] or not result:
        resp = create_session(request.json, resp)
        save_dialog(user_id=user_id, state="choice_difficult", resp=resp)
        return jsonify(resp)
    state = data["dialog_state"]
    if state == "choice_difficult":
        resp = choice_difficult(req=request.json, resp=resp, data=data)
        state = 'choice_categories'
        save_dialog(user_id=user_id, state=state, resp=resp)
    elif state == "choice_categories":
        resp = choice_categories(req=request.json, resp=resp, data=data)
        state = 'asking'
        save_dialog(user_id=user_id, state=state, resp=resp)
    elif state == "asking":
        resp, state = asking(req=request.json, resp=resp, data=data)
        save_dialog(user_id=user_id, state=state, resp=resp)
    elif state == "summarizing":
        resp, state = restart(req=request.json, resp=resp, data=data)
        save_dialog(user_id=user_id, state=state, resp=resp)
    else:
        raise Exception(f"Неизвестное состояние диалога: {state}")

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
    data = {"user_id": user_id,
            "total_count_questions": -1,
            "current_question": -1,
            "count_correct_answers": -1,
            "dialog_state": dialog_state,
            "categories": [],
            "last_resp": None,
            "difficult": -1,
            "questions": [],
            "correct_answer": "",
            }

    with open(f"data/users/{user_id}.json", 'w') as file:
        json.dump(data, file)


def save_dialog(user_id, state, resp):
    with open(f'data/users/{user_id}.json') as file:
        data = json.load(file)
        data["dialog_state"] = state
        data["last_resp"] = json.dumps(resp)
    logging.debug(data)
    with open(f'data/users/{user_id}.json', 'w') as file:
        json.dump(data, file)


def load_user_data(user_id):
    try:
        with open(f'data/users/{user_id}.json') as file:
            data = json.load(file)
        return data, True
    except FileNotFoundError:
        return data, False


def choice_difficult(req, resp, data):
    tokens = req["request"]['nlu']["tokens"]

    if len(tokens) > 1:
        resp = json.loads(data["last_resp"])
        resp["response"]["text"] = resp["response"]['tts'] = 'Мы вас не поняли, повторите пожалуйста свой выбор'
        return resp
    chosen_var = tokens[0].lower()
    if chosen_var == 'базовый':
        data["total_count_questions"] = 7
        data["difficult"] = 0
        data["current_question"] = 1
        data["count_correct_answers"] = 0
    elif chosen_var == 'средний':
        data["total_count_questions"] = 10
        data["difficult"] = 1
        data["current_question"] = 1
        data["count_correct_answers"] = 0
    elif chosen_var == 'сложный':
        data["total_count_questions"] = 15
        data["difficult"] = 2
        data["current_question"] = 1
        data["count_correct_answers"] = 0
    else:
        resp = json.loads(data["last_resp"])
        resp["response"]["text"] = resp["response"]['tts'] = 'Мы вас не поняли, повторите пожалуйста свой выбор'
        return resp

    with open(f'data/users/{req["session"]["session_id"]}.json', 'w') as file:
        json.dump(data, file)

    resp["response"]["text"] = resp["response"]['tts'] = 'Теперь выберите категории вопросов'
    categories = database.give_categories()

    resp["response"]["buttons"] = [{"title": "Все",
                                    "hide": True}] + [{"title": cat.capitalize(),
                                                       "hide": True} for cat in categories]

    return resp



def choice_categories(req, resp, data):
    tokens = req["request"]['nlu']["tokens"]
    chosen_cat = tokens[0].lower()
    cats = [cat[0] for cat in database.give_categories()]
    if chosen_cat.lower() == 'все':
        data["categories"].extend([cats])

        data["questions"].extend(database.give_questions())
        return resp
    #
    #
    #
    #
    # for cat in cats:
    #     if chosen_cat in cat:
    # if chosen_var in 'базовый':
    #     data["total_count_questions"] = 7
    #     data["difficult"] = 0
    #     data["current_question"] = 1
    #     data["count_correct_answers"] = 0
    # elif chosen_var == 'средний':
    #     data["total_count_questions"] = 10
    #     data["difficult"] = 1
    #     data["current_question"] = 1
    #     data["count_correct_answers"] = 0
    # elif chosen_var == 'сложный':
    #     data["total_count_questions"] = 15
    #     data["difficult"] = 2
    #     data["current_question"] = 1
    #     data["count_correct_answers"] = 0
    # else:
    #     resp = json.loads(data["last_resp"])
    #     resp["response"]["text"] = resp["response"]['tts'] = 'Мы вас не поняли, повторите пожалуйста свой выбор'
    #     return resp
    #
    # with open(f'data/users/{req["session"]["session_id"]}.json', 'w') as file:
    #     json.dump(data, file)
    #
    # resp["response"]["text"] = resp["response"]['tts'] = 'Теперь выберите категории вопросов'
    # categories = database.give_categories()
    #
    # resp["response"]["buttons"] = [{"title": "Все",
    #                                 "hide": True}] + [{"title": cat.capitalize(),
    #                                                    "hide": True} for cat in categories]
    #
    # return resp
    #
    #

def make_question(resp, data):

    data["current_question"] += 1
    variants = data["questions"][data["current_question"]]["variants"]
    text = data["questions"]["current_question"]["text"]
    resp["response"]["text"] = resp["response"]["tts"] = resp["response"]["text"] + f"\n {text}"
    resp["response"]["buttons"] = [{"title": var,
                                    "hide": True} for var in variants]

    return resp


def asking(req, resp, data):
    check_answer(req, resp, data)
    if data['total_count_questions'] == data["current_question"]:
        state = 'summarizing'
        resp = give_result(req, resp, data)
    resp = make_question(resp, data)

    return resp





def restart(req, resp, data):
    # resp["response"]["text"] = '''Привет, в этом навыке мы проверим твоё знание по предмету "География". Начинаем!
    # Выберите уровень сложности:'''
    # resp["response"]["tts"] = resp["response"]["text"]
    # resp["response"]["buttons"] = [
    #     {
    #         "title": "Базовый",
    #         "hide": True
    #     },
    #
    #     {
    #         "title": "Средний",
    #         "hide": True
    #     },
    #
    #     {
    #         "title": "Сложный",
    #         "hide": True
    #     }
    # ]

    return resp




def check_answer(req, resp, data):
    answer = req['request']["original_utterance"].lower()
    correct_answer = data["questions"][data["current_question"]]["correct_answer"]
    if answer == correct_answer:
        data["count_correct_answers"] += 1
        resp['response']['text'] = resp['response']['tts'] = 'Это правильный ответ'
    else:
        resp['response']['text'] = resp['response']['tts'] = 'К сожалению, это не так'
    return resp


def give_result(req, resp, data):
    return resp


if __name__ == '__main__':
    logging.basicConfig(filename='server.log',
                        level=logging.DEBUG)
    app.run(host='127.0.0.1', port=8000, debug=True)
