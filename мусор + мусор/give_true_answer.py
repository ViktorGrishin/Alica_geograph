import sqlite3

conn = sqlite3.connect('working_base.db')
cursor = conn.cursor()
cursor.execute(f"""
SELECT Questions.correct_answer
FROM Questions;
""")
data = cursor.fetchall()
conn.close()
with open('str_answer.txt', 'w', encoding='utf8') as file:
    for i in data:
        print(i[0], file=file)