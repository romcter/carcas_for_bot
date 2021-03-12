from models import *

with db:
    db.create_tables([Site, Category])

with db:
    site = Site(name="Ula", url='https://youla.ru/').save()
    site1 = Site(name="Avito", url='https://www.avito.ru/rossiya').save()
    site2 = Site(name="OLX", url='https://www.olx.ua/').save()
    site3 = Category(name="Транспорт", site_id=3).save()

print('DONE')