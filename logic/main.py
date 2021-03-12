import telebot
from telebot import types
from config import TELEGRAM_TOKEN
from db.models import db, Site, Category
from keyboa import keyboa_maker

bot = telebot.TeleBot(TELEGRAM_TOKEN)

link = ""

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        bot.send_message(message.from_user.id, "Выбери сайт для работы:")
        # keyboard = types.InlineKeyboardMarkup()
        site = []
        with db:
            for el in Site.select():
                site.append(el.name)
        site_keyboard = keyboa_maker(items=site, copy_text_to_callback=True, items_in_row=3)
        bot.send_message(chat_id=message.from_user.id, reply_markup=site_keyboard,
            text="Выбери сайт для работы:")
        # for el in site:
        #     key = types.InlineKeyboardButton(text=el.name, callback_data=el.id)
        #     keyboard.add(key)
        # question = "Выбери сайт для работы:"
        # bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    else:
            bot.send_message(message.from_user.id, 'Напиши /start')

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 1:
        link = 'https://www.olx.ua/'
    if call.data == "2":
        work_with_avito(call.data)

def work_with_avito(site_id_avito):
    keyboard = types.InlineKeyboardMarkup()
    with db:
        category = Category.select().where(Category.site_id == site_id_avito)
    for el in category:
        key = types.InlineKeyboardButton(text=el.name, callback_data=el.id)
        keyboard.add(key)

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)