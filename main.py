import json
import logging
import os
import time

import requests
from dotenv import load_dotenv
from requests.models import ReadTimeoutError
from telegram import Bot

logger = logging.getLogger('Bot logging')


class TelegramLogsHandler(logging.Handler):

    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


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
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(TelegramLogsHandler(tg_bot=logging_bot, chat_id=user_id))
    logger.info('Бот запущен')
    while True:
        try:
            r = requests.get(url, headers=headers, params=payload, timeout=60)
            r.raise_for_status()
            result_of_checking = r.json()
            if result_of_checking.get('status') == 'found':
                bot.send_message(chat_id=user_id, text=handle_status(result_of_checking))
                payload = {'timestamp': result_of_checking.get('last_attempt_timestamp')}
            else:
                payload = {'timestamp': result_of_checking.get('timestamp_to_request')}
        except ConnectionError as exc:
            logger.error(exc)
            time.sleep(60)
        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.HTTPError as exc:
            logger.error(exc)
            time.sleep(60)


def handle_messages(message):
    works_status = []
    for attempt in message.get('new_attempts'):
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
