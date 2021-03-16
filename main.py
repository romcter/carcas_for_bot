import telebot
import requests
from config import *
from bs4 import BeautifulSoup as BS
from keyboa import keyboa_maker
from db import db, User

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    try:
        User().get(User.id(message.chat.id))
    except:
        with db:
            User(telegram_id=message.chat.id, first_name=message.chat.first_name, last_name=message.chat.last_name,
                 username=message.chat.username, role='USER').save()
    main_menu(message.chat.id)


@bot.message_handler(content_types=['text'])
def take_text(message):
    if URL_BANKER in message.html_text:
        bot.send_message(ADMIN_ID, text='Активируй ссылку: ' + message.html_text)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data == Ads:
        ads_page(call)
    elif call.data == Score:
        score_page(call)
    elif call.data == Refill:
        bot.send_message(call.from_user.id, text='Я буду ждать чек с BCT Banker')
    elif URL_BANKER in call.data:
        bot.send_message(ADMIN_ID, text='Активируй ссылку: ' + call.data)
    elif call.data == OLX_URL:
        create_keyboard_for_category(call, category_for_olx)
    elif OLX_URL in call.data:
        parser_for_olx(call)
    else:
        main_menu(call.from_user.id)


def main_menu(chat_id):
    main_kb = keyboa_maker(items=main_keyboard, copy_text_to_callback=True, items_in_row=2)
    bot.send_message(chat_id, text='Что то', reply_markup=main_kb)


def ads_page(call):
    user = User().get(User.telegram_id == call.from_user.id)
    if user.score == 0.0:
        sct = 'На балансе: ' + str(user.score) + ' RUB, пополни баланс через BTC Banker баланс\n'
        bot.send_message(call.from_user.id, text=sct)
    else:
        site_keyboard = keyboa_maker(items=site, copy_text_to_callback=True, items_in_row=2)
        bot.send_message(call.from_user.id, text='Выбери площадку для работы: \n', reply_markup=site_keyboard)


def score_page(call):
    user = User().get(User.telegram_id == call.from_user.id)
    sct = 'На балансе: ' + str(user.score) + ' RUB'
    keyboard_for_score = keyboa_maker(items=scores_keyboard, copy_text_to_callback=True, items_in_row=2)
    bot.send_message(call.from_user.id, text=sct, reply_markup=keyboard_for_score)


def create_keyboard_for_category(call, category):
    keyboard_for_category = keyboa_maker(items=category, items_in_row=2)
    bot.send_message(call.from_user.id, text="Выбери рубрику:", reply_markup=keyboard_for_category)


def parser_for_olx(call):
    bot.answer_callback_query(call.id)
    main_request = requests.get(call.data, headers=HEADER).content
    soup = BS(main_request, 'lxml')
    new_ads = soup.find_all('tr', class_='wrap')
    users = []
    bot.send_message(call.from_user.id,
                     text='Подожди 15 секунд.')
    if (len(new_ads) > 0):
        for new_ad in new_ads:
            try:
                if (new_ad.find('span', class_='delivery-badge') != None):
                    link_to_ad = new_ad.find('a', class_='thumb').get('href')
                    price = new_ad.find('p', class_='price').get_text(strip=True)
                    ad_request = requests.get(link_to_ad, headers=HEADER).content
                    soap = BS(ad_request, 'lxml')
                    if (soap.find('strong', class_='offer-details__value').get_text(strip=True) != 'Бизнес'):
                        user_name = soap.find('div', 'quickcontact__user-name').get_text(strip=True)
                        link_to_profile = soap.find('a', 'quickcontact__image-link').get('href')
                        html = requests.get(link_to_profile, headers=HEADER).content
                        soip = BS(html, 'html.parser')
                        ads = str(len(soip.find_all('tr', 'wrap')))
                        users.append({
                            'link_to_ad': link_to_ad,
                            'price': price,
                            'ads': ads,
                            'user_name': user_name
                        })
                    else:
                        print('Бизнес акаунт')
                else:
                    print('Не часные объявления')
            except:
                print('Что то пошло не так')
        for el in users:
            bot.send_message(call.from_user.id, text=return_user_html(el), parse_mode='HTML')
    else:
        bot.send_message(call.from_user.id, text='Что то с площадкой, поменяй сайт', parse_mode='HTML')


def return_user_html(user, diff=None):
    result = '<b>Имя: ' + user['user_name'] + '</b>\n<b>Ссылка: ' + user['link_to_ad'] + '</b>\n' \
                                                                                         '<b>Цена: ' + user[
                 'price'] + '</b>\n<b>Количество объявлений: ' + user['ads'] + '</b>\n'
    return result


if __name__ == '__main__':
    with db:
        db.create_tables([User])
        try:
            User().get(User.telegram_id == ADMIN_ID)
        except:
            User(telegram_id=ADMIN_ID, first_name='Roma Primyk', username='Roman_Primuk', role='ADMIN').save()
    bot.polling(none_stop=True, interval=0)
