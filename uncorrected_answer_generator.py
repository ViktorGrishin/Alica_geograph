with open('str_answer.txt', 'w', encoding='utf8') as file:
    for i in range(0, 100 + 1):
        print(f'Неправильный ответ {i}',file=file)