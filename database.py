import sqlite3
import random


def give_categories(s=f"""
    SELECT QuestionTypes.type_name
    FROM QuestionTypes;
    """):
    conn = sqlite3.connect('working_base.db')
    cursor = conn.cursor()
    cursor.execute(s)
    data = cursor.fetchall()
    conn.close()
    return data


def give_variants(type):
    return list(filter(lambda x: not x.isdigit(), map(lambda x: x[0], give_categories(f"""
    SELECT Questions.correct_answer
    FROM Questions
    JOIN QuestionTypes ON Questions.type_id = QuestionTypes.type_id
    WHERE QuestionTypes.type_name = '{type}';
    """))))


def give_questions(cat=-1, cant_use=['1000']):
    cat = cat[0]
    conn = sqlite3.connect('working_base.db')
    cursor = conn.cursor()
    sql_query = f"""
    SELECT Questions.question_id, Questions.question_text, Questions.type_id, Questions.correct_answer, Questions.answer_format
    FROM Questions
    JOIN QuestionTypes ON Questions.type_id = QuestionTypes.type_id
    WHERE QuestionTypes.type_name = '{cat}'
        AND Questions.question_id NOT IN ({','.join(list(map(str, cant_use)))})
    ORDER BY RANDOM()
    LIMIT 1;
    """
    cursor.execute(sql_query)

    data = cursor.fetchall()
    if data:
        return None
    data = data[0]
    if not int(data[-1]):
        text = give_variants(cat)
        list_of_uncorrected_answer = [text[random.randint(0, len(text) - 1)].strip('\n') for i in range(3)]
        while data[3] in list_of_uncorrected_answer:
            list_of_uncorrected_answer = [text[random.randint(0, len(text) - 1)].strip('\n') for i in range(3)]

        request = {'id': data[0],
                   'text': data[1],
                   'correct_answer': data[3],
                   'variants': list_of_uncorrected_answer}
    else:
        corr_int_answer = int(data[2])
        turn = ['+', '-']
        list_of_incorrect_answer = []
        for j in range(3):
            incorrect_answer = eval(f'{corr_int_answer}{turn[random.randint(0, 1)]}{random.randint(0, 100)}')
            while incorrect_answer <= 0:
                incorrect_answer = eval(
                    f'{corr_int_answer}{turn[random.randint(0, 1)]}{random.randint(0, 100)}')
            list_of_incorrect_answer.append(incorrect_answer)

            request = {'id': data[0],
                       'text': data[1],
                       'correct_answer': data[3],
                       'variants': list(map(str, list_of_incorrect_answer))}

    conn.close()
    return request


print(*give_questions(['Озера'], cant_use=[93, 94, 95, 96]), sep='\n')
