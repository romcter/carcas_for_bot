import telebot
import requests
from config import *
from bs4 import BeautifulSoup as BS
from keyboa import keyboa_maker, keyboa_combiner
from db import db, User

bot = telebot.TeleBot(TELEGRAM_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    try:
        User().get(User.telegram_id == message.chat.id)
    except:
        with db:
            User(telegram_id=message.chat.id, first_name=message.chat.first_name, last_name=message.chat.last_name,
                 username=message.chat.username).save()
    main_menu(message.chat.id)

def main_menu(chat_id):
    main_kb = keyboa_maker(items=[SCORE, SITE_FOR_SALE, FILTER], copy_text_to_callback=True, items_in_row=2)
    bot.send_message(chat_id, text='Куда дальше?\n', reply_markup=main_kb)


@bot.message_handler(content_types=['text'])
def take_text(message):
    if URL_BANKER in message.html_text:
        bot.forward_message(ADMIN_ID, message.chat.id, message.id)
        bot.send_message(message.chat.id, text='Подожди минуту я всё сделаю и отпишусь')
        bot.send_message(ADMIN_ID, text='Жду ссылку с подтверждением \n')
    if YOU_GET in message.html_text:
        approve(message)


@bot.callback_query_handler(func=lambda call: True)
def main_keyboard(call):
    if call.data == MAIN_MENU:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        main_menu(call.message.chat.id)
    elif call.data == FILTER:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        filters(call)
    elif call.data == SITE_FOR_SALE:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        board_ads(call)
    elif call.data == SCORE:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        score_page(call)
    #Filter
    elif call.data == FILTER_BY_SAFE_ADS:
        user = User.get(User.telegram_id == call.from_user.id)
        if user.filter_by_safe_add:
            user.filter_by_safe_add = False
        else:
            user.filter_by_safe_add = True
        user.save()
        bot.delete_message(call.message.chat.id, call.message.message_id)
        filters(call)
    elif call.data == FILTER_BY_TYPE_ADS:
        user = User.get(User.telegram_id == call.from_user.id)
        if user.filter_by_type_ads == 'Бизнес':
            user.filter_by_type_ads = 'Все объявления'
        else:
            user.filter_by_type_ads = 'Бизнес'
        user.save()
        bot.delete_message(call.message.chat.id, call.message.message_id)
        filters(call)
    elif call.data == FILTER_BY_COUNT_OF_ADS:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        msg = bot.send_message(call.from_user.id, text='Введи нужное кол-во объявлений')
        bot.register_next_step_handler(msg, needed_quantity_ads)
    elif call.data == FILTER_BY_YEAR_REGISTRATION:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        msg = bot.send_message(call.from_user.id, text='Введи нужный год')
        bot.register_next_step_handler(msg, needed_year)
    # elif call.data == FILTER:
    #     filter_for_ads(call)
    # # Score
    # elif call.data == REFILL:
    #     bot.send_message(call.from_user.id, text='Отправь мне чек с BCT Banker и я зачислю тебе деньги')
    # elif APPROVE in call.data:
    #     approve(call)
    # # Parsing
    # elif call.data == OLX_URL:
    #     create_keyboard_for_category(call, CATEGORY_FOR_OLX)
    # elif OLX_URL in call.data:
    #     parser_for_olx(call)
    # else:
    #     main_menu(call.from_user.id)


def filters(call):
    try:
        user = User.get(User.telegram_id == call.from_user.id)
    except:
        user = User.get(User.telegram_id == call.message_id)
    site_and_filter_keyboard = keyboa_maker(items=[FILTER_BY_SAFE_ADS, FILTER_BY_TYPE_ADS, FILTER_BY_COUNT_OF_ADS, FILTER_BY_YEAR_REGISTRATION],
                                            copy_text_to_callback=True, items_in_row=2)
    keyboard = keyboa_combiner(keyboards=(site_and_filter_keyboard, comeback_button(MAIN_MENU)))
    if user.filter_by_type_ads == 'Бизнес':
        type_ads = 'только часные'
    else:
        type_ads = 'все'
    if user.filter_by_safe_add:
        safe_add = 'Включена'
    else:
        safe_add = 'Выключена'
    mess = 'Настройки фильтрации:\n\n' \
        ' ➖ Год регистрации: ' + user.filter_by_year_registration + '\nМинимально допустимый год регистрации аккаунта продавца\n\n' \
        ' ➖ Кол-во объявлений: ' + str(user.filter_by_all_ads) + '\nМаксимальное количество объявлений на аккаунте продавца\n\n' \
        ' ➖ Тип объявлений: ' + type_ads + '\nВладелец акаунта часное лицо или бизнес\n\n' \
        ' ➖ Безопасная сделка: ' + safe_add
    try:
        bot.send_message(call.from_user.id, text=mess, reply_markup=keyboard)
    except:
        bot.send_message(call.message_id, text=mess, reply_markup=keyboard)


def needed_quantity_ads(message):
    user = User().get(User.telegram_id == message.chat.id)
    user.filter_by_all_ads = message.html_text
    user.save()
    bot.delete_message(message.from_user.id, message.message_id)
    filters(message)


def needed_year(message):
    user = User().get(User.telegram_id == message.chat.id)
    user.filter_by_year_registration = message.html_text
    user.save()
    bot.delete_message(message.chat.id, message.message_id)
    filters(message)

def board_ads(call):
    # user = User().get(User.telegram_id == call.from_user.id)
    # if user.score == 0.0:
    #     sct = 'На балансе: ' + str(user.score) + ' RUB, пополни баланс через BTC Banker баланс\n'
    #     bot.send_message(call.from_user.id, text=sct)
    # else:
    site_keyboard = keyboa_maker(items=[{"Olx": OLX_URL}], copy_text_to_callback=True, items_in_row=2)
    bot.send_message(call.from_user.id, text='Выбери площадку для работы: \n', reply_markup=site_keyboard)


def approve(message):
    try:
        user_admin = User().get(User.telegram_id == message.from_user.id)
        if (user_admin.telegram_id == ADMIN_ID) & (user_admin.role == ROLE_ADMIN):
            user_for_refill = User().get(User.telegram_id == message.reply_to_message.chat.id)
            score = user_for_refill.score + float(message.html_text.split('(')[1].split(')')[0].split(' ')[0])
            User.update(score=score).where(User.telegram_id == user_for_refill.telegram_id).execute()
            bot.send_message(ADMIN_ID, text='Деньги зачислены')
            message_for_customer_about_success = 'У тебя на балансе ' + str(score) + ' RUB'
            bot.send_message(user_for_refill.telegram_id, text=message_for_customer_about_success)
    except:
        bot.send_message(ADMIN_ID, text='Что то пошло не так, попробуй ещё раз.')


def score_page(call):
    user = User().get(User.telegram_id == call.from_user.id)
    sct = 'На балансе: ' + str(user.score) + ' RUB'
    keyboard_for_score = keyboa_maker(items=SCORE_KEYBOARD, copy_text_to_callback=True, items_in_row=2)
    bot.send_message(call.from_user.id, text=sct, reply_markup=keyboard_for_score)


def create_keyboard_for_category(call, category):
    keyboard_for_category = keyboa_maker(items=category, items_in_row=2)
    bot.send_message(call.from_user.id, text="Выбери рубрику:", reply_markup=keyboard_for_category)


def parser_for_olx(call):
    user = User().get(User.telegram_id == call.from_user.id)
    bot.answer_callback_query(call.id)
    main_request = requests.get(call.data, headers=HEADER).content
    soup = BS(main_request, 'lxml')
    new_ads = soup.find_all('tr', class_='wrap')
    users = []
    try:
        if len(new_ads) > 0:
            for new_ad in new_ads:
                if new_ad.find('span', class_='delivery-badge') is not None:
                    link_to_ad = new_ad.find('a', class_='thumb').get('href')
                    price = new_ad.find('p', class_='price').get_text(strip=True)
                    ad_request = requests.get(link_to_ad, headers=HEADER).content
                    soap = BS(ad_request, 'lxml')
                    if soap.find('strong', class_='offer-details__value').get_text(
                            strip=True) != user.filter_by_type_ads:
                        user_name = soap.find('div', 'quickcontact__user-name').get_text(strip=True)
                        link_to_profile = soap.find('a', 'quickcontact__image-link').get('href')
                        html = requests.get(link_to_profile, headers=HEADER).content
                        soip = BS(html, 'html.parser')
                        all_ads = len(soip.find_all('tr', 'wrap'))
                        if all_ads < user.filter_by_all_ads:
                            users.append({
                                'link_to_ad': link_to_ad,
                                'price': price,
                                'ads': str(all_ads),
                                'user_name': user_name
                            })
                        else:
                            print('Больше ' + str(user.filter_by_all_ads) + ' объявлений')
                    else:
                        print('Бизнес акаунт')
                else:
                    print('Без безопасной сделки')
            for el in users:
                bot.send_message(call.from_user.id, text=return_user_html(el), parse_mode='HTML')
        else:
            bot.send_message(call.from_user.id, text='Что то с площадкой, поменяй сайт', parse_mode='HTML')
    except:
        print('Что то пошло не так')


def return_user_html(user):
    result = '<b>Имя: ' + user['user_name'] + '</b>\n<b>Ссылка: ' + user['link_to_ad'] + '</b>\n' \
                                                                                         '<b>Цена: ' + user[
                 'price'] + '</b>\n<b>Количество объявлений: ' + user['ads'] + '</b>\n'
    return result

def comeback_button(comeback_to):
    return keyboa_maker(items=[{COMEBACK: comeback_to}], items_in_row=2)


if __name__ == '__main__':
    with db:
        db.create_tables([User])
        try:
            User().get(User.telegram_id == ADMIN_ID)
        except:
            User(telegram_id=ADMIN_ID, first_name='Roma Primyk', username='Roman_Primuk', score=100000,
                 role=ROLE_ADMIN).save()
    bot.polling(none_stop=True, interval=0)
