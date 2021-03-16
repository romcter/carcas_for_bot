import telebot
import requests
from config import TELEGRAM_TOKEN
from bs4 import BeautifulSoup as BS

bot = telebot.TeleBot(TELEGRAM_TOKEN)

OLX_URL = 'https://www.olx.ua'

HEADER = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}

site = [
    {'name': "Olx", 'url': OLX_URL}
]

category_for_olx = [
    {'name': 'Детский мир', 'url': 'https://www.olx.ua/detskiy-mir/'},
    {'name': 'Запчасти для транспорта', 'url': 'https://www.olx.ua/zapchasti-dlya-transporta/'},
    {'name': 'Дом и сад', 'url': 'https://www.olx.ua/dom-i-sad/'},
    {'name': 'Електроника', 'url': 'https://www.olx.ua/elektronika/'},
    {'name': 'Мода и стиль', 'url': 'https://www.olx.ua/moda-i-stil/'},
    {'name': 'Хобби, отдых и спорт', 'url': 'https://www.olx.ua/hobbi-otdyh-i-sport/'}
]

@bot.message_handler(content_types=['text'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton(text=site[0]['name'], callback_data=site[0]['url']))
    bot.send_message(message.chat.id, text="Выбери сайт:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data == OLX_URL:
        category_markup_for_olx(call)
    elif OLX_URL in call.data:
        parser_for_olx(call)
    else:
        pass


def category_markup_for_olx(call):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton(text=category_for_olx[0]['name'], callback_data=category_for_olx[0]['url']),
        telebot.types.InlineKeyboardButton(text=category_for_olx[1]['name'], callback_data=category_for_olx[1]['url']),
        telebot.types.InlineKeyboardButton(text=category_for_olx[2]['name'], callback_data=category_for_olx[2]['url']))
    markup.row(
        telebot.types.InlineKeyboardButton(text=category_for_olx[3]['name'], callback_data=category_for_olx[3]['url']),
        telebot.types.InlineKeyboardButton(text=category_for_olx[4]['name'], callback_data=category_for_olx[4]['url']),
        telebot.types.InlineKeyboardButton(text=category_for_olx[5]['name'], callback_data=category_for_olx[5]['url']))
    bot.send_message(call.from_user.id, text="Выбери рубрику:", reply_markup=markup)


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
    bot.polling(none_stop=True, interval=0)
