import sqlite3
import random

# Получение нужного типа вопроса:
type_of_question = 'Страны и города'
# Подключение к базе данных
conn = sqlite3.connect('working_base.db')
cursor = conn.cursor()

# SQL запрос
sql_query = f"""
SELECT Questions.question_text, Questions.correct_answer, Questions.answer_format
FROM Questions
JOIN QuestionTypes ON Questions.type_id = QuestionTypes.type_id
WHERE QuestionTypes.type_name = '{type_of_question}';
"""

# Выполнение запроса
cursor.execute(sql_query)

# Получение результатов
data = cursor.fetchall()
x = [j for j in range(0, len(data) - 1)]
random.shuffle(x)
for i in x:
    if not int(data[i][-1]):
        with open('str_answer.txt', 'r', encoding='utf8') as file:
            text = file.readlines()
            list_of_uncorrected_answer = [text[random.randint(0, 100)].strip('\n') for i in range(3)]
            # Запрос готовый к отправке
            request = tuple([data[0], data[1], *list_of_uncorrected_answer])
    else:
        corr_int_answer = int(data[i][1])
        turn = ['+', '-']
        list_of_incorrect_answer = []
        for j in range(3):
            incorrect_answer = eval(f'{corr_int_answer}{turn[random.randint(0, 1)]}{random.randint(0, 100)}')
            while incorrect_answer <= 0:
                incorrect_answer = eval(f'{corr_int_answer}{turn[random.randint(0, 1)]}{random.randint(0, 100)}')
            list_of_incorrect_answer.append(incorrect_answer)
        request = tuple([data[0], data[1], *list_of_incorrect_answer])

# Закрытие соединения
conn.close()
