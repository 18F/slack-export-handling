#! /usr/bin/env python

"""
slackToDB.py
* -[ ] Establish database connection
* -[ ] Iterate through all of the folders
* -[ ] Iterate through each file in the folder
* -[ ] Iterate through each object in the JSON file
* -[ ] Save the objects into the sqlite database
"""

import sqlite3
conn = sqlite3.connect('slack.db')
