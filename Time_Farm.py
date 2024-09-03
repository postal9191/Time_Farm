import time
from datetime import datetime, timedelta, timezone
import requests
import json



def get_Token():
    # Загрузка данных из файла config.json
    with open('config.json', 'r', encoding='utf-8') as config_file:
        config_data = json.load(config_file)

    url = "https://tg-bot-tap.laborx.io/api/v1/auth/validate-init/v2"

    payload = json.dumps(config_data)
    headers = {
        'accept': '*/*',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
    }

    response = requests.request("POST", url, headers=headers, data=payload).json()
    return response.get("token")

# Функция для отправки запроса на начало фарминга
def start(token):
    url = "https://tg-bot-tap.laborx.io/api/v1/farming/start"
    payload = json.dumps({})
    headers = {
        'accept': '*/*',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json',
    }
    response = requests.post(url, headers=headers, data=payload)
    print("Старт фарминга:", response.status_code, response.json())

# Функция для отправки запроса на завершение фарминга
def finish(token):
    url = "https://tg-bot-tap.laborx.io/api/v1/farming/finish"
    payload = json.dumps({})
    headers = {
        'accept': '*/*',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json',
    }
    response = requests.post(url, headers=headers, data=payload)
    print("Завершение фарминга:", response.status_code, response.json())

# Функция для получения информации о фарминге
def info(token):
    url = "https://tg-bot-tap.laborx.io/api/v1/farming/info"
    headers = {
        'accept': '*/*',
        'authorization': f'Bearer {token}',
    }
    response = requests.get(url, headers=headers)
    print("Информация о фарминге:", response.status_code, response.json())
    return response.json()

# Основная функция для управления процессом фарминга
def main():
    active_farming_end_time = None

    while True:
        # получает токен
        token = get_Token()

        # Получаем информацию о фарминге
        farming_info = info(token)

        # Проверяем, если фарминг активен
        if 'activeFarmingStartedAt' in farming_info:
            activeFarmingStartedAt = datetime.strptime(farming_info['activeFarmingStartedAt'], '%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=timezone.utc)
            active_farming_end_time = activeFarmingStartedAt + timedelta(hours=4, minutes=2)  # Устанавливаем время окончания фарминга
            print("Ждем до ", active_farming_end_time, "по UTC")

        # Если фарминг не активен, запускаем фарминг
        if 'activeFarmingStartedAt' not in farming_info:
            print("Фарминг не активен. Запуск фарминга...")
            start(token)
            time.sleep(10)  # Ждем 10 секунд перед следующим запросом

        # Если фарминг активен и время вышло, завершаем фарминг
        elif active_farming_end_time and datetime.now(timezone.utc) >= active_farming_end_time:
            print("Время фарминга истекло. Завершение фарминга...")
            finish(token)
            time.sleep(10)  # Ждем 10 секунд перед следующим запросом

        # Ждем перед следующим циклом
        time.sleep(int((active_farming_end_time - datetime.now(timezone.utc)).total_seconds()))

# Запуск основной функции
if __name__ == "__main__":
    main()
