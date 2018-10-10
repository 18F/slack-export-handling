from peewee import *


db = SqliteDatabase('slack.db')


class BaseModel(Model):
    """
    Just lets us not repeat ourselves too much.
    """
    class Meta:
        database = db


class Slack(BaseModel):
    """
    Used solely for legacy slack-urls compatibility.
    """
    channel = TextField()
    channel_date = TextField()
    data = TextField()


class SlackChannel(BaseModel):
    """
    Stores key info on Slack channels.
    There is more info available in channels.json but for our purposes, 
    most likely only the ID and name are needed.

    Having channel_id null isn't a great idea, but so long as we're finding channels 
    that aren't in channels.json I'm not sure what we can do about it. 
    To compensate somewhat, we'll index name and use it as a sort-of key.
    """
    channel_id = CharField(null=True)
    name = CharField(unique=True, index=True)
    private_group = BooleanField(default=False)
    private_messages = BooleanField(default=False)


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

    We also do not currently resolve internal link references to users, channels, etc.
    To do so, we'll need to hunt and translate the <#C02A80ZHG> type references.

    Also note that Peewee's TimestampField implementation strips milliseconds by default, 
    but there's a workaround: https://github.com/coleifer/peewee/issues/1747
    """
    channel_name = CharField()
    user = ForeignKeyField(SlackUser, backref='messages')
    message = TextField()
    date = DateField()
    ts = TimestampField(resolution=1e6)


