import telebot
from telebot import types

from config import TELEGRAM_TOKEN

from keyboa import keyboa_maker

bot = telebot.TeleBot(TELEGRAM_TOKEN)

link = ""
user_id = 0

class Site:

    name = "",
    url = ""

    def __init__(self, name, url):
        self.name = name
        self.url = url

class Category:
    name = '',
    url = ''

    def __init__(self, name, url):
        self.name = name
        self.url = url

# site = [{name: "Avito", 'url': 'https://www.avito.ru/rossiya'}, {"OLX": 'https://www.olx.ua/'}, {"ULA": 'https://youla.ru/'}]
site = [Site("Avito", 'https://www.avito.ru/rossiya'), Site("OLX", 'https://www.olx.ua/'), Site("ULA", 'https://youla.ru/')]
# category_for_olx = [{'Детский мир': 'https://www.olx.ua/detskiy-mir/'},
#                     {'Запчасти для транспорта': 'https://www.olx.ua/zapchasti-dlya-transporta/'},
#                     {'Дом и сад': 'https://www.olx.ua/dom-i-sad/'},
#                     {'Електроника': 'https://www.olx.ua/elektronika/'},
#                     {'Мода и стиль': 'https://www.olx.ua/moda-i-stil/'},
#                     {'Хобби, отдых и спорт': 'https://www.olx.ua/hobbi-otdyh-i-sport/'}]
category_for_olx = [Category('Детский мир', 'https://www.olx.ua/detskiy-mir/'),
                    Category('Запчасти для транспорта', 'https://www.olx.ua/zapchasti-dlya-transporta/'),
                    Category('Дом и сад', 'https://www.olx.ua/dom-i-sad/'),
                    Category('Електроника', 'https://www.olx.ua/elektronika/'),
                    Category('Мода и стиль', 'https://www.olx.ua/moda-i-stil/'),
                    Category('Хобби, отдых и спорт', 'https://www.olx.ua/hobbi-otdyh-i-sport/')]

@bot.message_handler(content_types=['text'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    for el in site:
        markup.add(telebot.types.InlineKeyboardButton(text=el.name, callback_data=el.url))
    bot.send_message(message.chat.id, text="Выбери сайт:", reply_markup=markup)
    # if message.text == '/start':
    #     site_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    #     for el in site:
    #         site_keyboard.add(el.name)
    #     # site_keyboard = keyboa_maker(items=site, copy_text_to_callback=True, items_in_row=3, )
    #     msg = bot.reply_to(message, 'Test text', reply_markup=site_keyboard)
    #     bot.register_next_step_handler(msg, chose_site)
    #     # bot.send_message(chat_id=message.from_user.id, reply_markup=site_keyboard,
    #     #                  text="Выбери сайт:",)
    # else:
    #     bot.send_message(message.from_user.id, 'Напиши /start')
# 547336139
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data == "https://www.olx.ua/":
        markup = telebot.types.InlineKeyboardMarkup()
        for el in category_for_olx:
            markup.add(telebot.types.InlineKeyboardButton(text=el.name, callback_data=el.url))
        bot.send_message(call.from_user.id, text="Выбери сайт:", reply_markup=markup)
    if call.data == "https://www.avito.ru/rossiya":
        pass
    if call.data == "https://youla.ru/":
        pass

# # @bot.callback_query_handler(func=lambda call: True)
# def chose_site(message):
#     # keyboa_maker().
#     if message.data == "https://www.olx.ua/":
#         # category_for_olx_keyboard = keyboa_maker(items=site, copy_text_to_callback=True, items_in_row=3)
#         category_for_olx_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True)
#         for el in category_for_olx:
#             category_for_olx_keyboard.add(el.get())
#         bot.send_message(chat_id=message.from_user.id, reply_markup=category_for_olx_keyboard,
#                          text="Выбери сайт:")
#         # bot.send_message(chat_id=message.from_user.id, reply_markup=category_for_olx_keyboard,
#         #                  text="Выбери подкатегорию:")
#     if message.data == "https://www.avito.ru/rossiya":
#         pass
#     if message.data == "https://youla.ru/":
#         pass

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
