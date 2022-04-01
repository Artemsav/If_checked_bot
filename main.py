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
    logging_token = os.getenv('TOKEN_LOGGING')
    user_id = os.getenv('USER_ID')
    bot = Bot(token=token)
    logging_bot = Bot(token=logging_token)


    class TelegramLogsHandler(logging.Handler):

        def __init__(self, tg_bot, chat_id):
            super().__init__()
            self.chat_id = chat_id
            self.tg_bot = tg_bot

        def emit(self, record):
            log_entry = self.format(record)
            self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('Bot logging')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(tg_bot=logging_bot, chat_id=user_id))
    logger.info('Бот запущен')
    while True:
        try:
            status = get_status(url, headers, payload)
            if status.get('status')=='found':
                bot.send_message(chat_id=user_id, text=handle_status(status))
                payload = {'timestamp': status.get('last_attempt_timestamp')}
            else:
                payload = {'timestamp': status.get('timestamp_to_request')}
        except ConnectionError as exc:
            logger.error(exc)
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
