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
        User().get(User.telegram_id == message.chat.id)
    except:
        with db:
            User(telegram_id=message.chat.id, first_name=message.chat.first_name, last_name=message.chat.last_name,
                 username=message.chat.username, role='USER').save()
    main_menu(message.chat.id)


@bot.message_handler(content_types=['text'])
def take_text(message):
    if URL_BANKER in message.html_text:
        bot.forward_message(ADMIN_ID, message.chat.id, message.id)
        bot.send_message(message.chat.id, text='Подожди минут я всё сделаю и отпишусь')
        bot.send_message(ADMIN_ID, text='Жду ссылку с подтверждением \n')
    if YOU_GET in message.html_text:
        approve(message)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data == SITE_FOR_SALE:
        site_and_filter_page(call)
    elif call.data == ADS:
        ads_page(call)
    elif call.data == FILTER:
        filter_for_ads(call)
    # Score
    elif call.data == SCORE:
        score_page(call)
    elif call.data == REFILL:
        bot.send_message(call.from_user.id, text='Отправь мне чек с BCT Banker и я зачислю тебе деньги')
    elif APPROVE in call.data:
        approve(call)
    # Parsing
    elif call.data == OLX_URL:
        create_keyboard_for_category(call, CATEGORY_FOR_OLX)
    elif OLX_URL in call.data:
        parser_for_olx(call)
    else:
        main_menu(call.from_user.id)


def main_menu(chat_id):
    main_kb = keyboa_maker(items=MAIN_KEYBOARD, copy_text_to_callback=True, items_in_row=2)
    bot.send_message(chat_id, text='Куда дальше?\n', reply_markup=main_kb)


def site_and_filter_page(call):
    site_and_filter_keyboard = keyboa_maker(items=SITE_AND_FILTER, copy_text_to_callback=True, items_in_row=2)
    mess = 'Ты можешь выбрать параметры по которым будешь фильтровать или оставить так как есть (если ничего не настраивать то тебе будут даваться только часные объявления и на которых включена безопасная сделка).'
    bot.send_message(call.from_user.id, text=mess, reply_markup=site_and_filter_keyboard)


def filter_for_ads(call):
    user = User.get(User.telegram_id == call.from_user.id)
    filter_keyboard = keyboa_maker(items=FILTER_KEYBOARD, copy_text_to_callback=True, items_in_row=2)
    bot.send_message(call.from_user.id, text='', reply_markup=filter_keyboard)

def approve(message):
    try:
        user_admin = User().get(User.telegram_id == message.from_user.id)
        if (user_admin.telegram_id == ADMIN_ID) & (user_admin.role == ROLE_ADMIN):
            user_for_refill = User().get(User.telegram_id == message.reply_to_message.chat.id)
            score = user_for_refill.score + float(message.html_text.split('(')[1].split(')')[0].split(' ')[0])
            User.update(score=score).where(User.telegram_id == user_for_refill.telegram_id).execute()
            bot.send_message(ADMIN_ID, text='Деньги зачислены')
            message_for_customer_about_success = 'Тебе зачислено ' + str(score) + ' RUB'
            bot.send_message(user_for_refill.telegram_id, text=message_for_customer_about_success)
    except:
        bot.send_message(ADMIN_ID, text='Что то пошло не так, попробуй ещё раз.')


def ads_page(call):
    user = User().get(User.telegram_id == call.from_user.id)
    if user.score == 0.0:
        sct = 'На балансе: ' + str(user.score) + ' RUB, пополни баланс через BTC Banker баланс\n'
        bot.send_message(call.from_user.id, text=sct)
    else:
        site_keyboard = keyboa_maker(items=SITE_KEYBOARD, copy_text_to_callback=True, items_in_row=2)
        bot.send_message(call.from_user.id, text='Выбери площадку для работы: \n', reply_markup=site_keyboard)


def score_page(call):
    user = User().get(User.telegram_id == call.from_user.id)
    sct = 'На балансе: ' + str(user.score) + ' RUB'
    keyboard_for_score = keyboa_maker(items=SCORE_KEYBOARD, copy_text_to_callback=True, items_in_row=2)
    bot.send_message(call.from_user.id, text=sct, reply_markup=keyboard_for_score)


def create_keyboard_for_category(call, category):
    keyboard_for_category = keyboa_maker(items=category, items_in_row=2)
    bot.send_message(call.from_user.id, text="Выбери рубрику:", reply_markup=keyboard_for_category)


def parser_for_olx(call):
    # bot.answer_callback_query(call.id)
    user = User().get(User.telegram_id == call.from_user.id)
    main_request = requests.get(call.data, headers=HEADER).content
    soup = BS(main_request, 'lxml')
    new_ads = soup.find_all('tr', class_='wrap')
    users = []
    bot.send_message(call.from_user.id,
                     text='Подожди 15 секунд.')
    if (len(new_ads) > 0):
        for new_ad in new_ads:
            try:
                if user.filter_by_safe_ads:
                    if new_ad.find('span', class_='delivery-badge') is not None:
                        pass
                    else:
                        print('без базопасной доставки')
                        continue
                link_to_ad = new_ad.find('a', class_='thumb').get('href')
                price = new_ad.find('p', class_='price').get_text(strip=True)
                ad_request = requests.get(link_to_ad, headers=HEADER).content
                soap = BS(ad_request, 'lxml')
                if user.filter_by_business:
                    if soap.find('strong', class_='offer-details__value').get_text(strip=True) != 'Бизнес':
                        pass
                    else:
                        print('бизнес акаун')
                        continue
                user_name = soap.find('div', 'quickcontact__user-name').get_text(strip=True)
                link_to_profile = soap.find('a', 'quickcontact__image-link').get('href')
                html = requests.get(link_to_profile, headers=HEADER).content
                soip = BS(html, 'html.parser')
                ads = len(soip.find_all('tr', 'wrap'))
                if user.filter_by_all_ads:
                    if ads <= 5:
                        pass
                    else:
                        print('больше 5')
                        continue
                users.append({
                    'link_to_ad': link_to_ad,
                    'price': price,
                    'ads': str(ads),
                    'user_name': user_name
                })
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
            User(telegram_id=ADMIN_ID, first_name='Roma Primyk', username='Roman_Primuk', score=100000,
                 role=ROLE_ADMIN).save()
    bot.polling(none_stop=True, interval=0)
