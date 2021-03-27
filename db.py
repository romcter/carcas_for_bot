from peewee import *

db = MySQLDatabase('telegram_bot', user='root', passwd='1029384756')

class User(Model):
    telegram_id = IntegerField(unique=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    username = CharField(null=True)
    score = FloatField(default=0.0)
    filter_by_type_ads = TextField(default='Бизнес')
    filter_by_all_ads = IntegerField(default=5)
    filter_by_year_registration = CharField(default='2021')
    filter_by_safe_add = BooleanField(default=True)
    subscribe = BooleanField(default=False)
    role = CharField(default='USER')

    class Meta:
        database = db
        db_table = 'user'
        order_by = 'id'