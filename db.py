from peewee import *

db = MySQLDatabase('telegram_bot', user='root', passwd='1029384756')

class User(Model):
    telegram_id = IntegerField(unique=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    username = CharField(null=True)
    score = FloatField(default=0.0)
    percent = IntegerField(default=10)
    filter_by_type_ads = CharField(null=True, default='Бизнес')
    filter_by_all_ads = IntegerField(null=True, default=5)
    role = CharField()

    class Meta:
        database = db
        db_table = 'user'
        order_by = 'id'