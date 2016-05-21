import csv
import json

# Load the users data
with open('data-import/users.json', 'r') as fp:
    users = json.load(fp)

# Load the results data
with open('results.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    msgs = [msg for msg in reader]

# Function to replace the user_id with a Real Name in a message
def replace_user_id(msg):
    user_id = msg[4]
    if user_id != 'USLACKBOT':
        user_name = [[user['real_name'] if 'real_name' in user else user['name']] for user in users if user['id'] == user_id][0]
        msg[4] = user_name[0]
    return msg

results = [replace_user_id(msg) for msg in msgs]

with open('mapped.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for result in results:
        writer.writerow(result)
