import json
import logging
import os
import time

import requests
from dotenv import load_dotenv
from requests.models import ReadTimeoutError
from telegram import Bot


def main():
    load_dotenv()
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': os.getenv('TOKEN_DEVMAN')}
    payload = {'timestamp': time.time()}
    token = os.getenv('TOKEN_TELEGRAM')
    user_id = os.getenv('USER_ID')
    bot = Bot(token=token)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    while True:
        try:
            status = get_status(url, headers, payload)
            if status.get('new_attempts')=='found':
                bot.send_message(chat_id=user_id, text=handle_status(status))
                payload = {'timestamp': status.get('last_attempt_timestamp')}
            else:
                payload = {'timestamp': status.get('timestamp_to_request')}
        except ConnectionError as exc:
            bot.send_message(chat_id=user_id, text=f'Бот упал с ошибкой: {exc}')
            time.sleep(60)
        except requests.exceptions.ReadTimeout:
            pass


def get_status(url, headers, payload):
    r = requests.get(url, headers=headers, params=payload, timeout=60)
    api_respond = r.json()
    return api_respond


def handle_status(status):
    works_status = []
    for attempt in status.get('new_attempts'):
        title = attempt.get('lesson_title')
        task_link = attempt.get('lesson_url')
        if attempt.get('is_negative'):
            work_status = f'У вас проверили работу "{title}" \n К сожалению, в работе нашлись ошибки. Ссылка на задачу {task_link}'
        elif not attempt.get('is_negative'):
            work_status = f'У вас проверили работу "{title}" \n Преподавателю все понравилось, можно приступать к следующему уроку!'
        else:
            work_status = 'Status is incorrect, please try again'
        works_status.append(work_status)
    return '\n'.join([_ for _ in works_status])


if __name__ == '__main__':
    main()
