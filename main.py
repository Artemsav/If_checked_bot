import json
import logging
import os
import time

import requests
from dotenv import load_dotenv
from telegram import Bot


def main():
    load_dotenv()
    url = 'https://dvmn.org/api/long_polling/'
    headers = {'Authorization': os.getenv('TOKEN_DEVMAN')}
    payload = {'timestamp_to_request': time.time()}
    token = os.getenv('TOKEN_TELEGRAM')
    user_id = os.getenv('USER_ID')
    bot = Bot(token=token)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    while True:
        try:
            bot.send_message(chat_id=user_id, text=handle_status(get_status(url, headers, payload)))
            payload = {'timestamp_to_request': get_status(url, headers, payload).get('timestamp_to_request')}
            time.sleep(60)
        except Exception as exc:
            bot.send_message(chat_id=user_id, text=f'Бот упал с ошибкой: {exc}')
            time.sleep(60)


def get_status(url, headers, payload):
    r = requests.get(url, headers=headers, params=payload)
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
