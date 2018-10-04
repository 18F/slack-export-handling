import datetime
import sys

from models import SlackMessage, SlackUser

query = sys.argv[1]

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

for r in sorted(expanded_results, key=lambda x: x.ts):
    author = SlackUser.get(user_id=r.user)
    print('%s wrote... "%s"' % (author.real_name, r.message))