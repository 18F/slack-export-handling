from peewee import *


db = SqliteDatabase('slack.db')


class Slack(Model):
    channel = TextField()
    channel_date = TextField()
    data = TextField()

    class Meta:
        database = db
