from geography_dictionary import dictionary
import sqlite3

# Устанавливаем соединение с базой данных (или создаем новую, если ее нет)
conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

# Создаем таблицу QuestionTypes
cursor.execute('''
CREATE TABLE QuestionTypes (
    type_id INTEGER PRIMARY KEY,
    type_name TEXT
)
''')

# Создаем таблицу Questions
cursor.execute('''
CREATE TABLE Questions (
    question_id INTEGER PRIMARY KEY,
    question_text TEXT,
    type_id INTEGER,
    correct_answer TEXT,
    answer_format TEXT,
    FOREIGN KEY (type_id) REFERENCES QuestionTypes(type_id)
)
''')
# Добавляем типы вопросов
question_types = [(key,) for key in dictionary.keys()]

cursor.executemany('INSERT INTO QuestionTypes (type_name) VALUES (?)', question_types)

# Добавляем вопросы
questions = []
for i in range(len(question_types)):
    for j in dictionary[question_types[i][0]]:
        question = (j[0], i + 1, j[1], int(j[1].isdigit()))
        questions.append(question)

cursor.executemany('INSERT INTO Questions (question_text, type_id, correct_answer, answer_format) VALUES (?,?,?,?)', questions)

# Сохраняем изменения и закрываем соединение
conn.commit()
conn.close()