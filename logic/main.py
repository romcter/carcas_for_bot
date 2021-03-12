import telebot
import requests
from config import TELEGRAM_TOKEN
from bs4 import BeautifulSoup as BS

bot = telebot.TeleBot(TELEGRAM_TOKEN)


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

class Mamont:
    safe_deal = False,
    ads = 0,
    business_account = False
    number = '',
    link_to_ad = ''

    def __init__(self, safe_deal, ads, business_account, number, link_to_ad):
        self.safe_deal = safe_deal
        self.ads = ads
        self.business_account = business_account
        self.number = number
        self.link_to_ad = link_to_ad

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
    if call.data == "https://www.olx.ua/":
        create_markup(call, category_for_olx)
    elif call.data == "https://www.avito.ru/rossiya":
        create_markup(call, category_for_avito)
    elif call.data == "https://youla.ru/":
        create_markup(call, category_for_youla)
    elif 'https://youla.ru/' in call.data:
        parser_for_youla(call.data)
    else:
        pass


def create_markup(call, category):
    markup = telebot.types.InlineKeyboardMarkup()
    for el in category:
        markup.add(telebot.types.InlineKeyboardButton(text=el.name, callback_data=el.url))
    bot.send_message(call.from_user.id, text="Выбери рубрику:", reply_markup=markup)


def parser_for_olx(olx_category_url):
    pass


def parser_for_avito(avito_category_url):
    pass


def parser_for_youla(youla_category_url):
    main_request = requests.get(youla_category_url)
    main_html = BS(main_request.content, 'html.parser')
    for el in main_html.select('#app .product_section .product_item'):
        link_to_ad = 'https://youla.ru' + el.contents[0].attrs['href']
        request_to_ad = requests.get(youla_category_url)
        soup = BS(request_to_ad.content, 'html.parser')
        ads = soup.select('#app.sc-psedN.dyhZUV')
        # for element in ad_html.select('#app .sc-pAYia.ceKQHP'):
        #     ads = element
        safe_deal = el.contents[0].attrs['href']
        business_account = el.select('.subcategories-list clr')
        number = el.select('.subcategories-list clr')
        Mamont(safe_deal, ads, business_account, number, link_to_ad)

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
