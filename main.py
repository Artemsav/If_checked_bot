import os
import json
import logging
import pprint
from pathlib import Path

import requests
import telegram
from dotenv import load_dotenv
from environs import Env
from telegram import Bot
from telegram.ext import Filters, Updater, dispatcher
from telegram.ext import callbackcontext
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.commandhandler import CommandHandler
from telegram.ext.callbackqueryhandler import CallbackQueryHandler

env_path = Path('.', '.env')
load_dotenv(dotenv_path=env_path,override=True)
env = Env()
env.read_env()

url = 'https://dvmn.org/api/long_polling/'
headers = {'Authorization': os.getenv('TOKEN_DEVMAN')}
payload = {'timestamp_to_request': ''}
token=os.getenv('TOKEN_TELEGRAM')
user_id=os.getenv('USER_ID')
bot = Bot(token=token)
#dispatcher = bot.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def parse_status(url, headers, payload):
    r = requests.get(url, headers=headers, params=payload)
    review_status = r.json()
    timestamp_to_request = review_status.get('timestamp_to_request')
    pprint.pprint(review_status, indent = 4, depth = 4)
    payload = {'timestamp_to_request':timestamp_to_request}
    return review_status

def handle_status(status):
    title = status.get('lesson_title')
    print(status.get('is_negative'))
    for item in status.get('new_attempts'):
        print(item)
        if item.get('is_negative')==True:
            status_of_work = f'У вас проверили работу {title} \n К сожалению, в работе нашлись ошибки'
        elif item.get('is_negative')==False:
            status_of_work = f'У вас проверили работу {title} \n Преподавателю все понравилось, можно приступать к следующему уроку!'
        else:
            status_of_work = 'Status is incorrect, please try again'
        print(status_of_work)
        return status_of_work

def start (update, context):
    #this will retrieve the user's username, as you already know
    chat_user_client = update.message.from_user.username
    #this will send the information to some Telegram user
    chat_user_client = update.message.from_user.username
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text = f'Hello {chat_user_client}!')

'''def status (update, context):
    callbackcontext
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text = f'Teacher has reviewed your {main(url, headers, payload)} project!')'''

if __name__ == '__main__':
    #start_handler = CommandHandler('start', start)
    #dispatcher.add_handler(start_handler)
    #bot.start_polling()
    while True:
        try:
            handle_status(parse_status(url, headers, payload))
            bot.send_message(chat_id = user_id, text = handle_status(parse_status(url, headers, payload)))

        except ConnectionError:
            pass
        except requests.exceptions.pleReadTimeout:
            pass
