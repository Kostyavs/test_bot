import logging
import os
import requests
import time
import datetime
import random
import matplotlib.pyplot as plt

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext.filters import Filters

import db


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

updater = Updater(token=os.environ['TOKEN'], use_context=True)
exchange_api = 'https://openexchangerates.org/api/'
exchange_key = os.environ['API_KEY']
disp = updater.dispatcher


def start(update, context):
    context.bot.send_message(chat_id=update.message.from_user.id, text='Hello! Welcome to my bot')


def lst(update, context):
    curr_time = time.time()  # timestamp for database
    db_time = db.get_time()
    text = ''
    # If since last insert to database passed more than ten minutes than it will send new request
    # Otherwise it will get data from database
    if curr_time - db_time > 600:
        response = requests.get(exchange_api + 'latest.json?app_id=' + exchange_key)
        response = response.json()
        rates = response['rates']
        for name in rates:
            rates[name] = round(rates[name], 2)
        db.new_data(rates, curr_time)
    else:
        rates = db.get_rates()
    for name in rates:
        rate = rates[name]
        text = text + name + ': ' + str(rate) + '\n'
    context.bot.send_message(chat_id=update.message.from_user.id, text=text)


# When user send /exchange command, exchange_command is called, and adds handler for any text.
# Since we need to delete this handler later, I have created variable with Handler object.
# And since Handler object needs to refer to callback function in it's scope,
# I had to put function exchange_10 over handler object.
def exchange_10(update, context):
    disp.remove_handler(exchange_text_handler)
    currency = update.message.text
    rate = db.get_currency(currency)  # getting rate of currency from database
    rate = float(rate[0][0])
    rate = rate * 10
    context.bot.send_message(chat_id=update.message.from_user.id, text=str(rate))


exchange_text_handler = MessageHandler(Filters.text, exchange_10)  # handler object for handling messages with any text


def exchange_command(update, context):
    context.bot.send_message(chat_id=update.message.from_user.id, text='Type currency')
    disp.add_handler(exchange_text_handler)


# Same issue like in exchange_func
def history_func(update, context):
    disp.remove_handler(history_text_handler)
    # Getting end_date which is today's date, and start_date which is one week ago
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=7)
    currency = update.message.text
    rate = db.get_currency(currency)
    rate = float(rate[0][0])
    rates = {}
    # In this loop rates for each dates except today are generated.
    while end_date != start_date:
        rates[start_date.strftime('%d')] = random.uniform(rate-1, rate+1)
        start_date = start_date + datetime.timedelta(days=1)
    else:
        rates[end_date.strftime('%d.%m')] = rate
    # Drawing graph
    plt.plot(rates.keys(), rates.values())
    plt.xlabel('dates')
    plt.ylabel('rates')
    plt.savefig('fig1.png')
    plt.clf()
    # And sending it to the user
    context.bot.send_photo(chat_id=update.message.from_user.id, photo=open('fig1.png', 'rb'))


history_text_handler = MessageHandler(Filters.text, history_func)  # handler object for handling messages with any text


def history_command(update, context):
    context.bot.send_message(chat_id=update.message.from_user.id, text='Type currency')
    disp.add_handler(history_text_handler)


# Handlers for all commands
disp.add_handler(CommandHandler('start', start))
disp.add_handler(CommandHandler('list', lst))
disp.add_handler(CommandHandler('exchange_10', exchange_command))
disp.add_handler(CommandHandler('history', history_command))

updater.start_polling()
