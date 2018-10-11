#! /usr/bin/env python

"""
slackToDB.py
* -[x] Establish database connection
* -[x] Iterate through all of the folders
* -[x] Iterate through each file in the folder
* -[x] Iterate through each object in the JSON file
* -[x] Save the objects into the sqlite database

To-Do: Improve error handling
"""

import json
import os
import sys
import time
from decimal import Decimal

from models import db, Slack, SlackChannel, SlackMessage, SlackUser

# This is where the Slack exported files were put.
# It should contain a big mess o' directories (one for each channel)
# plus a few stray json files, most notably `channels.json` and `users.json`
SLACK_FILES_DIR = 'data-import'

def legacy_import():
    """
    This fulfills the legacy needs from slackToDB.py
    """
    try:
        db.create_tables([Slack])
    except Exception as e:
        # Most likely table already exists, but we'll print the error to confirm.
        print('%s' % e)
    for root, dirs, files in os.walk(SLACK_FILES_DIR):
        if root == SLACK_FILES_DIR:
            continue
        
        for fname in files:
            dir_name = root.split(SLACK_FILES_DIR+'/')[1]
            channel_date, ftype = fname.rsplit('.')

            # Guard against .ds_store and other stray files. 
            # We only want to read json files.

            if ftype == 'json':
                jsonfile = '%s/%s/%s' % (SLACK_FILES_DIR, dir_name, fname)

                with open(jsonfile, 'r') as fp:
                    data = json.load(fp)
                for d in data:
                    # in the case of bot posts, there will be no user.
                    try:
                        Slack.get(
                            Slack.channel == dir_name,
                            Slack.channel_date == channel_date,
                            Slack.data == json.dumps(d)
                        )
                    except Slack.DoesNotExist:
                        Slack.create(
                            channel = dir_name,
                            channel_date = channel_date,
                            data=json.dumps(d)
                        )


def import_channels():
    print("Beginning Slack channel import...")
    try:
        db.create_tables([SlackChannel])
    except Exception as e:
        # Most likely table already exists, but we'll print the error to confirm.
        print('%s' % e)
    with open(SLACK_FILES_DIR + '/channels.json', "r") as channels_file:
        channels_data = json.load(channels_file)
    for c in channels_data:
        # Because we may create channels by name when importing messages
        # if we see unexpected channel info, we have to get by name here. 
        # In a better world, we should probably throw out unexpected channels,
        # which shouldn't really happen at all.
        try:
            SlackChannel.get(SlackChannel.name == c['name'])
        except SlackChannel.DoesNotExist:
            SlackChannel.create(
                channel_id = c['id'],
                name = c['name']
            )
    print('...continuing with private group channels...')
    # Now load up the private (group) channels
    with open(SLACK_FILES_DIR + '/groups.json', "r") as channels_file:
        channels_data = json.load(channels_file)
    for c in channels_data:
        try:
            SlackChannel.get(SlackChannel.channel_id == c['id'])
        except SlackChannel.DoesNotExist:
            SlackChannel.create(
            channel_id = c['id'],
            name = c['name'],
            private_group = True
        )
    print('...and finally private messaging channels...')
    # Now load up the private (dm) channels too
    with open(SLACK_FILES_DIR + '/dms.json', "r") as channels_file:
        channels_data = json.load(channels_file)
    for c in channels_data:
        try:
            SlackChannel.get(SlackChannel.channel_id == c['id'])
        except SlackChannel.DoesNotExist:
            SlackChannel.create(
            channel_id = c['id'],
            name = c['id'],
            private_messages = True
        )
    print("...finished")


def import_users():
    print('Beginning Slack user import....')
    try:
        db.create_tables([SlackUser])
    except Exception as e:
        # Most likely table already exists, but we'll print the error to confirm.
        print('%s' % e)
    with open(SLACK_FILES_DIR + '/users.json', "r") as f:
        data = json.load(f)
    for d in data:
        
        # There's some key error on real_name.
        # probably related to older schema when real name was only in profile.
        try:
            real_name = d['real_name']
        except:
            real_name = d['profile']['real_name']
        
        try:
            SlackUser.get(SlackUser.user_id == d['id'])
        except SlackUser.DoesNotExist:
            SlackUser.create(
            user_id = d['id'],
            name = d['name'],
            real_name = real_name
        )
    print("...finished")


def import_messages():
    print('Beginning Slack Message import...')
    try:
        db.create_tables([SlackMessage])
    except Exception as e:
        # Most likely table already exists, but we'll print the error to confirm.
        print('%s' % e)
    file_count = len(os.listdir(SLACK_FILES_DIR))
    print("... processing %s message files" % file_count)
    for root, dirs, files in os.walk(SLACK_FILES_DIR):
        if root == SLACK_FILES_DIR:
            continue
        file_count -= 1
        if file_count % 1000 == 0 and file_count != 0:
            print('... %s remaining...' % file_count)
        for fname in files:
            dir_name = root.split('data-import/')[1]
            # Resolve channel name
            try:
                channel = SlackChannel.get(SlackChannel.name == dir_name)
                channel_name = channel.name
            except SlackChannel.DoesNotExist:
                print("Unexpected channel data encounted! Could not find existing Slack channel `%s` in database." % dir_name )
                print("Creating new channel, but proceed with caution.")
                channel = SlackChannel.create(
                    channel_id = dir_name,
                    name = dir_name
                )
            channel_date, ftype = fname.rsplit('.')
            
            # Guard against .ds_store and other stray files. 
            # We only want to read json files.

            if ftype == 'json':
                jsonfile = '%s/%s/%s' % (SLACK_FILES_DIR, dir_name, fname)

                with open(jsonfile, 'r') as fp:
                    data = json.load(fp)
                for d in data:
                    # in the case of bot posts, there will be no user.
                    if 'user' in d:
                        #ts = Decimal(d['ts'])
                        ts = float(d['ts'])
                        try:
                            SlackMessage.get(
                                SlackMessage.channel_name == channel_name,
                                SlackMessage.date == channel_date,
                                SlackMessage.ts == ts
                            )
                        except SlackMessage.DoesNotExist:
                            SlackMessage.create(
                                channel_name = channel_name,
                                user = d['user'],
                                message = d['text'],
                                date = channel_date,
                                ts = ts
                            )
    print("...finished")

try:
    legacy = sys.argv[1]
except IndexError:
    legacy = None

if __name__ == "__main__":
    # execute only if run as a script
    import_channels()
    import_users()
    import_messages()
    if legacy and legacy == 'legacy':
        legacy_import()
    db.close()
