from peewee import *


db = SqliteDatabase('slack.db')


class BaseModel(Model):
    """
    Just lets us not repeat ourselves too much.
    """
    class Meta:
        database = db


class Slack(BaseModel):
    channel = TextField()
    channel_date = TextField()
    data = TextField()


class SlackChannel(BaseModel):
    """
    Stores key info on Slack channels.
    There is more info available in channels.json
    but for our purposes, most likely only the ID
    and name are needed.
    """
    channel_id = CharField()
    name = CharField()


class SlackUser(BaseModel):
    """
    Stores key info on Slack users.
    There is more info available in users.json
    but for our purposes, most likely only the ID,
    name and real_name are needed.
    """
    user_id = CharField(primary_key=True)
    name = CharField()
    real_name = CharField()


class SlackMessage(BaseModel):
    """
    Stores key info from Slack messages.
    Note we are not storing all info that may be attached to a message.
    """
    channel_name = CharField()
    user = ForeignKeyField(SlackUser, backref='messages')
    message = TextField()
    date = DateField()
    ts = DecimalField()
