#! /usr/bin/env python

import json
import os
import sys
import time

from models import db, Slack, SlackChannel, SlackMessage, SlackUser

# This is where the Slack exported files were put.
# It should contain a big mess o' directories (one for each channel)
# plus a few stray json files, most notably `channels.json` and `users.json`
SLACK_FILES_DIR = 'data-import'


def json_data(filename):
    """
    Simple helper to read and load the json
    """
    filepath = '%s/%s' % (SLACK_FILES_DIR, filename)
    with open(filepath, "r", encoding="utf8") as json_file:
        return json.load(json_file)


def legacy_import():
    """
    This fulfills the legacy needs from slackToDB.py from the deprecated
    `slack-urls` repo and is only called if a `--legacy` argument is passed to the importer.
    For details see the legacy commands documentation:
    ../README.md#legacy-commands
    """
    try:
        db.create_tables([Slack])
    except Exception as e:
        # Most likely table already exists, but we'll print the error to confirm.
        print('%s' % e)
    for root, dirs, files in os.walk(SLACK_FILES_DIR):
        if root != SLACK_FILES_DIR:
            print("You don't appear to be in the correct directory. Please double-check")
            break
        
        for fname in files:
            dir_name = root.split(SLACK_FILES_DIR+'/')[1]
            channel_date, ftype = fname.rsplit('.')

            # Guard against .ds_store and other stray files. 
            # We only want to read json files.

            if ftype == 'json':
                jsonfile = '%s/%s' % (dir_name, fname)
                for d in json_data(jsonfile):
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
    for c in json_data('channels.json'):
        # Because we may create channels by name when importing messages
        # if we see unexpected channel info, we have to get by name here. 
        # In a better world, we should probably throw out unexpected channels.
        # There *shouldn't* be any channels that aren't represented in channels.json
        try:
            SlackChannel.get(SlackChannel.name == c['name'])
        except SlackChannel.DoesNotExist:
            SlackChannel.create(
                channel_id = c['id'],
                name = c['name']
            )
    print('...continuing with private group channels...')
    for c in json_data('groups.json'):
        try:
            SlackChannel.get(SlackChannel.channel_id == c['id'])
        except SlackChannel.DoesNotExist:
            SlackChannel.create(
            channel_id = c['id'],
            name = c['name'],
            private_group = True
        )
    print('...and finally private messaging channels...')
    for c in json_data('dms.json'):
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
    print("Beginning Slack user import....")
    try:
        db.create_tables([SlackUser])
    except Exception as e:
        # Most likely table already exists, but we'll print the error to confirm.
        print('%s' % e)
    for d in json_data('users.json'):
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
            dir_name = root.split('data-import')[1]
            dir_name = ''.join(dir_name.split('/', 1))
            dir_name = ''.join(dir_name.split('\\', 1))
            channel_date, ftype = fname.rsplit('.')
            # Guard against .ds_store and other stray files. 
            # We only want to read json files.
            if ftype == 'json':
                # Resolve channel name
                try:
                    channel = SlackChannel.get(SlackChannel.name == dir_name)
                    channel_name = channel.name
                except SlackChannel.DoesNotExist:
                    print("Unexpected channel data encountered! Could not find Slack channel `%s` in database." % dir_name )
                    print("Creating new channel, but proceed with caution.")
                    # Note that because the channel is unexpected we have no ID and have to fake it.
                    channel = SlackChannel.create(
                        channel_id = dir_name,
                        name = dir_name
                    )

                jsonfile = '%s/%s' % (dir_name, fname)
                for d in json_data(jsonfile):
                    # in the case of bot posts, there will be no user.
                    if 'user' in d:
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

if __name__ == "__main__":
    # execute only if run as a script
    import_channels()
    import_users()
    import_messages()
    # check if the `--legacy` argument was passed.
    # if so, do that import too.
    if len(sys.argv) == 2 and sys.argv[1] == 'legacy':
        legacy_import()
    db.close()
