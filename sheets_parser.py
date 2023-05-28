from datetime import datetime
import gspread
import time
import requests
import json


appid = ['730', '570', '440']


def Error(e):
    print('Ошибка')
    now = datetime.now()
    with open('Log.txt', 'a+') as f:
        f.write(f'[{now.day}.{now.month}.{now.year} {now.hour}:{now.minute}] {e} \n')
    f.close()
    time.sleep(15)
    main(start_place)


def main(line):
    try:
        cell = column + str(line)

        if worksheet.acell(cell).value is None:  # Если клетка с названием пуста
            time.sleep(30)  # ждем
            main(start_place)  # начинаем заново

        if worksheet.acell(cell).value == 'n':  # Проверка на специальный символ если True то пропуск
            line = int(line) + 1
            main(line)

        item = worksheet.acell(cell).value  # Название предмета из клеточки
        data = checker(item)
        request(data, line, item)
        line = int(line) + 1
        main(line)
    except Exception as e:
        Error(e)


def checker(item):  # Вызов JSON файла от Steam с информацией о предмете
    try:
        url = 'https://steamcommunity.com/market/priceoverview/?'
        item = replacer(item)
        for game_id in appid:
            params = {'market_hash_name': item,  # Название предмета
                      'appid': game_id,  # Номер игры
                      'currency': '5',  # Валюта (5 = рубль)
                      'format': 'json'
                      }
            req = requests.get(url, params=params)  # Получение HTML
            if req.status_code == 200:
                data = req.json()
                return data
    except Exception as e:
        Error(e)


def request(data, line, item):   # Получение средней цены и внесение в таблицу изменения
    try:
        value = data['median_price']
        value = value.replace(' pуб.', '')
        worksheet.update(end_column + str(line), value)
        print(f'[{item}] Был обновлен')
        time.sleep(2)
    except Exception as e:
        Error(e)


def replacer(item_name):  # Замена специальных символов
    try:
        item_name = item_name.replace('%20', ' ')
        item_name = item_name.replace('%7C', '|')
        item_name = item_name.replace('%28', '(')
        item_name = item_name.replace('%29', ')')
        item_name = item_name.strip()
        return item_name
    except Exception as e:
        Error(e)


def UserPreset():  # проверяем настройки пользователя для парсинга
    try:
        global column
        global end_column
        global SheetID
        global start_place
        with open("user/preferences.json", "r+") as jsonFile:
            data = json.load(jsonFile)
            
            column = data["column"]
            end_column = data['end_column']
            SheetID = data['SheetID']
            start_place = data['start_place']
            
            if SheetID == '':
                data['SheetID'] = input('Введите ID гугл таблицы: ')
            if column == '':
                data['column'] = input('Введите букву колонки с английскими названиями: ').upper()
            if end_column == '':
                data['end_column'] = input('Введите букву колонки для цен: ').upper()
            if start_place == '':
                data['start_place'] = input('Введите цифру первой строки с названием: ')
            
            jsonFile.seek(0)  # Убрать лишние - 0 = убрать
            json.dump(data, jsonFile, indent=4)  # Запись
            jsonFile.truncate()
    except Exception as e:
        Error(e)   


if __name__ == '__main__':
    UserPreset()
    gs = gspread.service_account(filename='place credits here/credits.json')  # подключаем файл с ключами и пр.
    sh = gs.open_by_key(SheetID)  # подключаем таблицу по ID
    worksheet = sh.sheet1  # получаем первый лист
    main(start_place)
