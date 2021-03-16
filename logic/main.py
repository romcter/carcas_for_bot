import telebot
import requests
from config import TELEGRAM_TOKEN
from bs4 import BeautifulSoup as BS
import json

bot = telebot.TeleBot(TELEGRAM_TOKEN)

OLX_URL = 'https://www.olx.ua'
AVITO_URL = 'https://www.avito.ru'
YOULA_URL = 'https://youla.ru'

HEADER = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}


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


site = [
    Site("Avito", AVITO_URL),
    Site("Olx", OLX_URL),
    Site("Youla", YOULA_URL)
]

category_for_olx = [Category('Детский мир', 'https://www.olx.ua/detskiy-mir/'),
                    Category('Запчасти для транспорта', 'https://www.olx.ua/zapchasti-dlya-transporta/'),
                    Category('Дом и сад', 'https://www.olx.ua/dom-i-sad/'),
                    Category('Електроника', 'https://www.olx.ua/elektronika/'),
                    Category('Мода и стиль', 'https://www.olx.ua/moda-i-stil/'),
                    Category('Хобби, отдых и спорт', 'https://www.olx.ua/hobbi-otdyh-i-sport/')]

category_for_avito = [Category('Личные вещи', 'https://www.avito.ru/rossiya/lichnye_veschi'),
                      Category('Хобби и отдых', 'https://www.avito.ru/rossiya/hobbi_i_otdyh'),
                      Category('Транспорт', 'https://www.avito.ru/rossiya/transport'),
                      Category('Для дома и дачи', 'https://www.avito.ru/rossiya/dlya_doma_i_dachi'),
                      Category('Готовый бизнес и оборудование', 'https://www.avito.ru/rossiya/dlya_biznesa')]

category_for_youla = [Category('Женская одежда', 'https://youla.ru/all/zhenskaya-odezhda'),
                      Category('Телефоны и планшеты', 'https://youla.ru/all/smartfony-planshety'),
                      Category('Запчасти и автотовары', 'https://youla.ru/all/avto-moto'),
                      Category('Десткая одежда', 'https://youla.ru/all/detskaya-odezhda'),
                      Category('Хендмейд', 'https://youla.ru/all/hehndmejd'),
                      Category('Фото и видео камеры', 'https://youla.ru/all/foto-video'),
                      Category('Компьютерная техника', 'https://youla.ru/all/kompyutery'),
                      Category('Спорт и отдых', 'https://youla.ru/all/sport-otdyh'),
                      Category('Красота и здоровье', 'https://youla.ru/all/krasota-i-zdorove'),
                      Category('Для дома и дачи', 'https://youla.ru/all/dom-dacha'),
                      Category('Бытовая техника', 'https://youla.ru/all/bytovaya-tekhnika'),
                      Category('Електроника', 'https://youla.ru/all/ehlektronika'),
                      Category('Детские товары', 'https://youla.ru/all/detskie'),
                      Category('Мужская одежда', 'https://youla.ru/all/muzhskaya-odezhda')]


@bot.message_handler(content_types=['text'])
def start(message):
    markup = telebot.types.InlineKeyboardMarkup()
    for el in site:
        markup.add(telebot.types.InlineKeyboardButton(text=el.name, callback_data=el.url))
    bot.send_message(message.chat.id, text="Выбери сайт:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    if call.data == OLX_URL:
        create_markup(call, category_for_olx)
    elif call.data == AVITO_URL:
        create_markup(call, category_for_avito)
    elif call.data == YOULA_URL:
        create_markup(call, category_for_youla)
    elif OLX_URL in call.data:
        parser_for_olx(call)
    elif AVITO_URL in call.data:
        parser_for_avito(call)
    elif YOULA_URL in call.data:
        parser_for_youla(call)
    else:
        pass


def create_markup(call, category):
    markup = telebot.types.InlineKeyboardMarkup()
    for el in category:
        markup.add(telebot.types.InlineKeyboardButton(text=el.name, callback_data=el.url))
    bot.send_message(call.from_user.id, text="Выбери рубрику:", reply_markup=markup)


def parser_for_olx(call):
    bot.answer_callback_query(call.id)
    main_request = requests.get(call.data, headers=HEADER).content
    soup = BS(main_request, 'lxml')
    new_ads = soup.find_all('tr', class_='wrap')
    users = []
    bot.send_message(call.from_user.id, text='Подожди 15 секунд и ничего не делай потому что я ещё не тестил нормально.')
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


def parser_for_avito(call):
    bot.answer_callback_query(call.id)
    main_request = requests.get(call.data, headers=HEADER).content
    print(main_request.decode())
    soup = BS(main_request, 'lxml')
    new_ads = soup.find_all('div', class_='iva-item-root-G3n7v')
    if (len(new_ads) > 0):
        users = []
        for new_ad in new_ads:
            try:
                if (new_ad.find('div', class_='delivery-icon-root-1WkFb') != None):
                    link_to_ad = AVITO_URL + new_ad.find('a', class_='iva-item-sliderLink-2hFV_').get('href')
                    price = new_ad.find('span', class_='price-text-1HrJ_').get_text(strip=True)
                    ad_request = requests.get(link_to_ad, headers=HEADER).content
                    soap = BS(ad_request, 'lxml')
                    if (soap.find('div', {'data-marker': 'seller-info/label'}).get_text(strip=True) == 'Частное лицо'):
                        user_name = soap.find('div', 'seller-info-name').get_text(strip=True)
                        link_to_profile = soap.find('a', 'seller-info-avatar-image').get('href')
                        hz = link_to_profile.split("/")[4]
                        req = 'https://www.avito.ru/web/1/profile/public/items?hashUserId=' + hz + '&shortcut=active'
                        profile_html = requests.get(req, headers=HEADER).content
                        ads = len(json.loads(profile_html)['result']['list'])
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


def parser_for_youla(call):
    bot.answer_callback_query(call.id)
    main_request = requests.get(call.data, headers=HEADER).content
    soup = BS(main_request, 'lxml')
    new_ads = soup.find_all('li', class_='product_item')
    users = []
    for new_ad in new_ads:
        if (new_ad.find('span', class_='status_badge__icon') != None):
            link_to_ad = YOULA_URL + new_ad.contents[0].get('href')
            price = new_ad.find('div', class_='product_item__description').contents[0].get_text(strip=True)
            ad_request = requests.get(link_to_ad, headers=HEADER).content
            hz = json.loads(ad_request)
            print(ad_request.decode())
            # soap = BS(ad_request, 'lxml')
            # user_name = soap.find('span', class_='sc-pDabv')
            # ads = soap.find('span', class_='sc-pDabv')
            # users.append({
            #     'link_to_ad': link_to_ad,
            #     'price': price,
            #     'ads': ads,
            #     'user_name': user_name
            # })
    else:
        print('Не часные объявления')
    for el in users:
        bot.send_message(call.from_user.id, text=return_user_html(el), parse_mode='HTML')


def return_user_html(user, diff=None):
    result = '<b>Имя: ' + user['user_name'] + '</b>\n<b>Ссылка: ' + user['link_to_ad'] + '</b>\n' \
                                                                                         '<b>Цена: ' + user[
                 'price'] + '</b>\n<b>Количество объявлений: ' + user['ads'] + '</b>\n'
    return result


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
