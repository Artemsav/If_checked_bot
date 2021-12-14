import telegram
from telegram.ext import Updater, dispatcher, updater
import logging

from telegram.ext.commandhandler import CommandHandler
token='5034070173:AAE8CDJPg_lsWNUTYT5IiQwEBP0YwIozhT4'
user_id = 377157791
bot = Updater(token=token)
dispatcher = bot.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


def start (update, context):
    #this will retrieve the user's username, as you already know
    user = update.message.from_user
    #this will send the information to some Telegram user
    chat_user_client = update.message.from_user.username
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text = f'Hello {chat_user_client}!')

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
bot.start_polling()