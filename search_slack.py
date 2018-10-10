import csv
import datetime
import sys

from models import SlackMessage, SlackUser

query = sys.argv[1]

output_dir = 'search-output/'

# see if minutes were passed as an arg. If not, we'll just set it.
try:
    expanded_minutes = int(sys.argv[2])
except IndexError:
    expanded_minutes = 20
expanded_results = []

print('Searching Slack DB for "%s"' % query)

results = SlackMessage.select().where(SlackMessage.message.contains(query))

# All this looping is wildly inefficent, but 
# I don't see an efficient way to combine querysets in peewee
# and itertools chain wouldn't, as far as I know, check if the records
# are already in the collection. Luckily, the results set should be pretty small, 
# So it shouldn't be a problem...

if expanded_minutes is 0:
    expanded_results = results
else:
    for r in results:
        
        minus_time = r.ts - datetime.timedelta(minutes=expanded_minutes)
        plus_time = r.ts + datetime.timedelta(minutes=expanded_minutes)
        
        # TODO: fix where this may pull in stray DMs because channel_name is just "dm", undifferentiated
        r_expanded = SlackMessage.select().where(
            SlackMessage.ts > minus_time,
            SlackMessage.ts < plus_time,
            SlackMessage.channel_name == r.channel_name
        )
        for x in r_expanded:
            if x not in expanded_results:
                expanded_results.append(x)

print("Found %s results that match exactly and %s results when expanding the query." % (results.count(), len(expanded_results)))

# Results are currently sorted by channel name and then timestamp, 
# in order to better group and capture late replies.
sorted_results = sorted(expanded_results, key=lambda x: (x.channel_name, x.ts))
channel_name = sorted_results[0].channel_name
outputfile = output_dir + query.replace(' ', '_') + '_output.csv'

with open(outputfile, 'w') as csvfile:
    writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(['Channel', 'Date', 'Author', 'Message', 'Timestamp'])
    for r in sorted_results:
        # If the channel name has changed from what it was before,
        # then we'll want to insert a blank line
        if r.channel_name != channel_name:
            writer.writerow([])
        channel_name = r.channel_name
        # Resolve any author name issues
        try:
            slackuser = SlackUser.get(user_id=r.user)
            author_name = slackuser.real_name.encode('utf8')
        except Exception:
            author_name = "Slackbot"
        # Now go head and output the row.
        writer.writerow([r.channel_name.encode('utf8'), r.date , author_name, r.message.encode('utf8'), r.ts])
print("Results have been written to `%s`" % outputfile)
