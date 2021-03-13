import telebot
import requests
from config import TELEGRAM_TOKEN
from bs4 import BeautifulSoup as BS
from selenium import webdriver

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


class User:
    price = '',
    user_name = '',
    ads = '',
    number = '',
    link_to_ad = ''

    def __init__(self, price, link_to_ad):
        self.price = price
        self.link_to_ad = link_to_ad

    # def __init__(self, price, user_name, ads, number, link_to_ad):
    #     self.price = price
    #     self.user_name = user_name
    #     self.ads = ads
    #     self.number = number
    #     self.link_to_ad = link_to_ad


site = [Site("Avito", 'https://www.avito.ru/rossiya'), Site("Olx", 'https://www.olx.ua/'),
        Site("Youla", 'https://youla.ru/')]

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
    for new_ad in new_ads:
        try:
            if (new_ad.find('span', class_='delivery-badge') != None):
                link_to_ad = new_ad.find('a', class_='thumb').get('href')
                price = new_ad.find('p', class_='price').get_text(strip=True)
                ad_request = requests.get(link_to_ad, headers=HEADER).content
                soap = BS(ad_request, 'lxml')
                if (soap.find('strong', 'offer-details__value').get_text(strip=True) != 'Бизнес'):
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
        bot.send_message(call.from_user.id, text=el, parse_mode='HTML')


def return_user_html(users, diff=None):
    result = ''
    for el in users:
        result += '<b>Имя: '+el['user_name']+'</b>\n<b>Ссылка: '+el['link_to_ad']+'</b>\n' \
                                        '<b>Цена: '+el['price']+'</b>\n<b>Количество объявлений: '+el['ads']+'</b>\n'
    return result


def parser_for_avito(avito_category_url):
    main_request = requests.get(avito_category_url, headers=HEADER)
    soup = BS(main_request.content, 'html.parser')
    ads = soup.findAll('div', class_='iva-item-body-NPl6W')
    for ad in ads:
        link_to_ad = 'https://www.avito.ru' + ad.contents[1].contents[0].attrs['href']
        price = ad.contents[2].contents[0].text
        ad_request = requests.get(link_to_ad, headers=HEADER)
        soap = BS(ad_request.content, 'html.parser')

        user_names = soap.findAll('a')
        часные_ли_объявы = soap.find('div', class_='seller-info/label')
        user_namez = soap.find('a', class_='button-size-s-3-rn6')
        user_namex = soap.find('a', class_='button-default-mSfac')
        user_namce = soap.find('a', class_='width-width-12-2VZLz')
        user_name = soap.find('div', class_='seller-info-name').contents[1].text
        user_link = soap.find('div', class_='seller-info-name').contents[1].attrs['href']
        ad_request = requests.get(user_link)
        souup = BS(ad_request.content, 'html.parser')
        span = souup.find('span', class_='public-profile-tab(active)')

        user = User(link_to_ad, price, user_name, count_ads)
        print(user)


def parser_for_youla(youla_category_url):
    main_request = requests.get(youla_category_url)
    main_html = BS(main_request.content, 'html.parser')
    for el in main_html.select('#app .product_section .product_item'):
        link_to_ad = 'https://youla.ru' + el.contents[0].attrs['href']
        request_to_ad = requests.get(youla_category_url)
        soup = BS(request_to_ad.content, 'html.parser')
        ads = soup.find('span', class_='sc-psedN')
        safe_deal = el.contents[0].attrs['href']
        business_account = el.select('.subcategories-list clr')
        number = el.select('.subcategories-list clr')
        User(safe_deal, ads, business_account, number, link_to_ad)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)