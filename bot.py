import os
import telebot
from telebot import types


BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def greet(message):
    bot.reply_to(message, "Hi")


bot.infinity_polling()
