from peewee import *

db = MySQLDatabase('telegram_bot', user='root', passwd='1029384756')

class User(Model):
    telegram_id = IntegerField()
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    username = CharField(null=True)
    score = DoubleField(default=0.0)
    procent = IntegerField(default=10)
    role = CharField()

    class Meta:
        database = db
        db_table = 'user'
        order_by = 'id'