def destroy(text):
    return text.replace('(', '').replace(')', '').replace('Ответ:', '').strip().rstrip()


names = ['Части света, материки, острова, полуострова и др.', 'Страны и города', 'Горы, плоскогорья, плато, вулканы',
         'Столицы', 'Океаны', 'О России',
         'Моря', 'Заповедники', 'Водопады', 'Реки', 'Озера']

names_dict = {name: [] for name in names}

with open('need.txt', 'r') as text:
    txt = text.read().split()
    lst = []
    string = []
    ans = False
    for i in txt:
        if ans:
            question = destroy(' '.join(string))
            ans = False
            for j in names:
                if j in question:
                    question = question.replace(j, '').strip().rstrip()
                    id = j
                    super_lst = []
                    break
            names_dict[id].append((question, destroy(i).replace('.', '')))
            string = []
        elif 'Ответ' in i:
            ans = True
            string.append(i)
        elif '(' in i:
            question = destroy(' '.join(string))
            for j in names:
                if j in question:
                    question = question.replace(j, '').strip().rstrip()
                    id = j
                    super_lst = []
                    break
            names_dict[id].append((question, destroy(i).replace('.', '')))
            string = []

        else:
            string.append(i)

for key, value in names_dict.items():
    print(f'Ключ: {key}, Значение: {value}')
    print('\n')

print(names_dict)
# print(*lst, sep='\n')
