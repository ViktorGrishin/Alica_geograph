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


def give_questions(cat=-1, diff=-1):
    big_request = []
    if cat == -1:
        cat = give_categories()
    for mini_cat in cat:
        conn = sqlite3.connect('working_base.db')
        cursor = conn.cursor()
        sql_query = f"""
        SELECT Questions.question_id, Questions.question_text, Questions.correct_answer, Questions.answer_format
        FROM Questions
        JOIN QuestionTypes ON Questions.type_id = QuestionTypes.type_id
        WHERE QuestionTypes.type_name = "{mini_cat}";
        """
        cursor.execute(sql_query)
        data = cursor.fetchall()

        x = [j for j in range(0, len(data) - 1)]
        random.shuffle(x)

        for i in x:
            if diff == 0:
                break
            diff -= 1
            if not int(data[i][-1]):
                text = give_variants(mini_cat)
                list_of_uncorrected_answer = [text[random.randint(0, len(text) - 1)].strip('\n') for i in range(3)]
                while data[1] in list_of_uncorrected_answer:
                    list_of_uncorrected_answer = [text[random.randint(0, len(text) - 1)].strip('\n') for i in range(3)]

                request = {'id': data[i][0],
                           'text': data[i][1],
                           'correct_answer': data[i][2],
                           'variants': list_of_uncorrected_answer}
            else:
                corr_int_answer = int(data[i][2])
                turn = ['+', '-']
                list_of_incorrect_answer = []
                for j in range(3):
                    incorrect_answer = eval(f'{corr_int_answer}{turn[random.randint(0, 1)]}{random.randint(0, 100)}')
                    while incorrect_answer <= 0:
                        incorrect_answer = eval(
                            f'{corr_int_answer}{turn[random.randint(0, 1)]}{random.randint(0, 100)}')
                    list_of_incorrect_answer.append(incorrect_answer)

                    request = {'id': data[i][0],
                               'text': data[i][1],
                               'correct_answer': data[i][2],
                               'variants': list_of_incorrect_answer}

            big_request.append(request)


        conn.close()
    return big_request

# print(*give_questions(['Столицы'], diff=3), sep='\n')


# print(give_categories())
print(give_questions(cat=-1, diff=7))
