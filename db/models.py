from peewee import *

db = MySQLDatabase('telegram_bot', user='root', passwd='1029384756')

class BaseModel(Model):
    id = PrimaryKeyField()

    class Meta:
        database = db
        order_by = 'id'

class Site(BaseModel):
    name = CharField()
    url = CharField()

    class Meta:
        db_table = 'site'

class Category(BaseModel):
    # url_site = ForeignKeyField(Site.url)
    site_id = ForeignKeyField(Site)
    name = CharField()

    class Meta:
        db_table = 'category'
