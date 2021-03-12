import telebot
from config import TELEGRAM_TOKEN
from telebot import types
from db.models import db, Site, Category
from keyboa import keyboa_maker

bot = telebot.TeleBot(TELEGRAM_TOKEN)

link = ""
user_id = 0

site = [{"Avito": 'https://www.avito.ru/rossiya'}, {"OLX": 'https://www.olx.ua/'}, {"ULA": 'https://youla.ru/'}]

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        # markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        # for element in site:
        #     markup.add(element.keys())
        # msg = bot.reply_to(message, 'Выбери сайт для работы', reply_markup=markup)
        # bot.register_next_step_handler(msg, callback_worker)
        # global user_id
        # user_id = message.from_user.id
        # with db:
        #     for el in site:
        #         site.append(el.name)
        site_keyboard = keyboa_maker(items=site, copy_text_to_callback=True, items_in_row=3)
        bot.send_message(
            chat_id=message.from_user.id, reply_markup=site_keyboard,
            text="Please select one of the fruit:")
        # msg = bot.reply_to(chat_id=user_id, reply_markup=site_keyboard, text="Выбери сайт для работы:")
        # bot.register_next_step_handler(msg, callback_worker)
    else:
        bot.send_message(message.from_user.id, 'Напиши /start')

# @bot.message_handler(commands=['help', 'start'])
# def send_welcome(message):
#     markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
#     markup.add('1', '2') #Имена кнопок
#     msg = bot.reply_to(message, 'Test text', reply_markup=markup)
#     bot.register_next_step_handler(msg, process_step)
#
# def process_step(message):
#     chat_id = message.chat.id
#     if message.text=='1':
#         func1()
#     else:
#         func2()

# @bot.callback_query_handler(func=lambda call: True)
def callback_worker(message):
    if message:
        link = 'https://www.olx.ua/'
    if message.data == "2":
        category = []
        with db:
            for el in Category.select().where(Category.site_id == message.data):
                category.append(el.name)
        category_keyboard = keyboa_maker(items=category, copy_text_to_callback=True, items_in_row=3)
        bot.send_message(chat_id=user_id, reply_markup=category_keyboard, text="Выбери категорию для работы:")

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)