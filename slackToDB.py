#! /usr/bin/env python

"""
slackToDB.py
* -[x] Establish database connection
* -[x] Iterate through all of the folders
* -[x] Iterate through each file in the folder
* -[x] Iterate through each object in the JSON file
* -[x] Save the objects into the sqlite database
"""

from peewee import *
import json
import os

db = SqliteDatabase('slack.db')

class Slack(Model):
    channel = TextField()
    channel_date = TextField()
    data = TextField()

    class Meta:
        database = db

Slack.create_table()

for root, dirs, files in os.walk('data-import'):
    if root == 'data-import':
        continue
    for fname in files:
        channel = root.split('data-import/')[1]
        channel_date = fname.split('.json')[0]
        jsonfile = 'data-import/%s/%s' % (channel, fname)

        with open(jsonfile, 'r') as fp:
            data = json.load(fp)

        with db.atomic():
            for entry_json in data:
                Slack.create(channel=channel, channel_date=channel_date, data=json.dumps(entry_json))
