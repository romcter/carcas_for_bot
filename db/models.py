from peewee import *

db = MySQLDatabase('telegram_bot', user='root', passwd='1029384756')

class BaseModel(Model):
    id = PrimaryKeyField()

    class Meta:
        database = db
        order_by = 'id'

class Site(BaseModel):
    name = CharField(max_length=100)
    url = CharField(max_length=255)

    class Meta:
        db_table = 'site'

class Category(BaseModel):
    site_id = ForeignKeyField(Site)
    name = CharField(max_length=100)
    url = CharField(max_length=100)

    class Meta:
        db_table = 'category'
