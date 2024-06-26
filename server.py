import json
import database


def main(event, context):
    resp = make_base_answer(event)
    user_id = event["session"]["session_id"]
    data, result = load_user_data(resp)
    if event["session"]["new"] or not result:
        resp, data = create_session(event, resp)
        resp = save_dialog(data=data, resp=resp)
        return resp
    state = data["dialog_state"]
    if state == "choice_difficult":
        resp, data = choice_difficult(req=event, resp=resp, data=data)
    elif state == "choice_categories":
        resp, data = choice_categories(req=event, resp=resp, data=data)
    elif state == "asking":
        resp, data = asking(req=event, resp=resp, data=data)
    elif state == "restart":
        resp, data = restart(req=event, resp=resp, data=data)
    else:
        raise Exception(f"Неизвестное состояние диалога: {state}")

    resp, state = save_dialog(user_id=user_id, data=data, resp=resp)
    return resp


def make_base_answer(req):
    return {
        "response": {
            "text": "",
            "tts": "",
            "end_session": False,
        },

        'session': req['session'],
        'version': req['version'],
        'state': {},
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

    data = create_user_memory(req["session"]["session_id"])
    data["dialog_state"] = 'choice_difficult'
    return resp, data


def create_user_memory(dialog_state="start_session"):
    data = {"used_questions": [],
            "count": 0,
            "correct_answers": 0,
            "answer": "",
            "dialog_state": dialog_state,
            "categories": [],
            }

    return data


def save_dialog(data, resp):
    resp["state"]["session"] = data
    return resp


def load_user_data(resp):
    if "state" in resp and "session" in resp["session"]:
        data = resp["state"]["session"]
        return data, True
    return {}, False


def choice_difficult(req, resp, data):
    tokens = req["request"]['nlu']["tokens"]

    if len(tokens) > 1:
        resp["response"] = data["last_resp"]["response"]
        resp["response"]["text"] = resp["response"]['tts'] = 'Мы вас не поняли, повторите пожалуйста свой выбор'
        return resp, data
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
        resp["response"] = data["last_resp"]["response"]
        resp["response"]["text"] = resp["response"]['tts'] = 'Мы вас не поняли, повторите пожалуйста свой выбор'
        data["dialog_state"] = 'choice_difficult'
        return resp, data

    with open(f'data/users/{req["session"]["session_id"]}.json', 'w') as file:
        json.dump(data, file)

    resp["response"]["text"] = resp["response"]['tts'] = 'Теперь выберите категории вопросов'
    categories = [cat[0] for cat in database.give_categories()]

    resp["response"]["buttons"] = [{"title": "Все",
                                    "hide": True}] + [{"title": cat.capitalize(),
                                                       "hide": True} for cat in categories]
    data["dialog_state"] = 'choice_categories'
    return resp, data


def choice_categories(req, resp, data):
    tokens = req["request"]['nlu']["tokens"]
    chosen_cat = tokens[0].lower()
    cats = [cat[0] for cat in database.give_categories()]
    if chosen_cat.lower() == 'все':
        data["categories"].extend([cats])
        data["count"] = 10
        resp, data = make_question(resp, data)
        data["dialog_state"] = 'asking'
        return resp, data
    if chosen_cat.lower() == 'закончили':
        data["count"] = 10
        resp, data = make_question(resp, data)
        data["dialog_state"] = 'asking'
        return resp, data
    for cat in cats:
        if chosen_cat in cat.split()[0].lower():
            data["categories"].append(cat)
            break
    else:
        resp["response"] = data["last_resp"]["response"]
        resp["response"]["text"] = resp["response"]['tts'] = 'Мы вас не поняли, повторите пожалуйста свой выбор'
        data["dialog_state"] = 'choice_categories'
        return resp, data

    resp["response"]["text"] = resp["response"]['tts'] = 'Теперь выберите дополнительные категории вопросов'
    categories = [cat[0] for cat in database.give_categories()]

    resp["response"]["buttons"] = [{"title": "Закончили",
                                    "hide": True}] + [{"title": cat.capitalize(),
                                                       "hide": True} for cat in categories if
                                                      cat not in data["categories"]]

    data["dialog_state"] = 'choice_categories'
    return resp, data


def make_question(resp, data):
    quest = database.give_questions(cat=data["categories"], cant_use=data["used_questions"])
    if quest:
        data["used_questions"].append(quest["id"])
        text = quest["text"]
        resp["response"]["text"] = resp["response"]["tts"] = resp["response"]["text"] + text
        resp["response"]["buttons"] = [{"title": var,
                                        "hide": True} for var in quest["variants"]]
        data["answer"] = quest["correct_answer"]

        return resp, data, True
    else:
        return resp, data, False


def asking(req, resp, data):
    check_answer(req, resp, data)
    if data['total_count_questions'] == len(data["used_questions"]):
        resp = give_result(req, resp, data)
        data["dialog_state"] = 'restart'
        return resp, data
    else:
        resp, data, is_result = make_question(resp, data)
        if is_result:
            return resp, data
        else:
            resp = give_result(req, resp, data)
            data["dialog_state"] = 'restart'
            return resp, data


def restart(req, resp, data):
    answer = req['request']["original_utterance"].lower()
    if answer.startswith('д'):

        resp["response"]["text"] = '''Выберите уровень сложности:'''
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
        data["dialog_state"] = 'choice_difficult'
        return resp, data
    else:

        resp["response"]["text"] = 'Спасибо за игру, до встречи!'
        resp["response"]["tts"] = resp["response"]["text"]
        resp["end_session"] = True
        return resp, {}


def check_answer(req, resp, data):
    answer = req['request']["original_utterance"].lower()
    correct_answer = data["answer"]
    if answer == correct_answer.lower():
        data["count_correct_answers"] += 1
        resp['response']['text'] = resp['response']['tts'] = 'Это правильный ответ \n '
    else:
        resp['response']['text'] = resp['response'][
            'tts'] = f'К сожалению, это не так. Верный ответ - {correct_answer} \n '
    return resp


def give_result(req, resp, data):
    correct = data["count_correct_answers"]
    total = data["total_count_questions"]
    perc = round(correct * 100 / total, 2)
    resp['response']['text'] = resp['response']['tts'] = resp['response']['text'] + f"""Поздравляем, тест закончен!
Ваш результат: {correct} правильных ответа из {total}. Процент выполнения: {perc}%. Хотите попробовать снова?"""
    resp['response']['buttons'] = [{"title": 'Да', "hide": True},
                                   {"title": 'Нет', "hide": True}]
    return resp
