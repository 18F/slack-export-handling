import argparse
import csv
import datetime
import re
import sys

from models import SlackMessage, SlackUser, SlackChannel

query = sys.argv[1]

parser = argparse.ArgumentParser(description='Process some queries.')
parser.add_argument(
    'queries', nargs='+',
    help='A query phrase to search for. Be sure to wrap multi-word phrases in quotes.',
)
parser.add_argument('--expand_to', default=20, type=int,
    help='Time to which you want to expand the search out, in minutes. Default: 20'
)

output_dir = 'search-output/'
args = parser.parse_args()
results = []
expanded_results = []


def build_initial_results(args):
    """
    Builds out the initial, non-expanded results for each query.
    We're appending to the `results` list to avoid duplicates
    if the same message is found by multiple queries.
    """

    for query in args.queries:
        print('Searching Slack DB for "%s"' % query)

        query_results = SlackMessage.select().where(SlackMessage.message.contains(query))
        for r in query_results:
            if r not in results:
                results.append(r)
    print('Found %s results for %s. Now expanding to %s minutes either direction...' % (len(results), args.queries, args.expand_to))
    return results


def build_expanded_results(initial_results):
    """
    Expand initial results set out to capture additional time
    as defined by `expand_to`.

    All this looping is a little inefficent, but performant enough given the results sizes.
    """

    if args.expand_to is 0:
        return initial_results
    else:
        for r in initial_results:
            minus_time = r.ts - datetime.timedelta(minutes=args.expand_to)
            plus_time = r.ts + datetime.timedelta(minutes=args.expand_to)

            r_expanded = SlackMessage.select().where(
                SlackMessage.ts > minus_time,
                SlackMessage.ts < plus_time,
                SlackMessage.channel_name == r.channel_name
            )
            for x in r_expanded:
                if x not in expanded_results:
                    expanded_results.append(x)
    print("Found %s results when expanding the query." % (len(expanded_results)))
    return expanded_results


def write_results(expanded_results):
    """
    Sort results by channel name and timestamp
    then write to file.
    """
    sorted_results = sorted(expanded_results, key=lambda x: (x.channel_name, x.ts))
    try:
        channel_name = sorted_results[0].channel_name
    except IndexError:
        print("No results found")
        return
    # Sanitize the given query to be safe for a filename.
    queries_string = '_'.join(args.queries)
    safequery = re.sub(r'\W+','', queries_string.replace(' ','_'))
    outputfile = output_dir + safequery + '_output.csv'

    with open(outputfile, 'w', encoding='utf8') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(['Channel', 'Date', 'Author', 'Message', 'Timestamp', 'Private Group'])
        for r in sorted_results:
            # get the related channel. We'll need this later.
            channel = SlackChannel.get(name=r.channel_name)
            # If the channel name has changed from what it was before,
            # then we'll want to insert a blank line in the csv.
            if r.channel_name != channel_name:
                writer.writerow([])
            channel_name = r.channel_name
            # Resolve any author name issues
            try:
                slackuser = SlackUser.get(user_id=r.user)
                author_name = slackuser.real_name
            except Exception:
                author_name = "Slackbot"
            writer.writerow([r.channel_name, r.date , author_name, r.message, r.ts, channel.private_group])
    print("Results have been written to `%s`" % outputfile)

if __name__ == "__main__":
    initial_results = build_initial_results(args)
    expanded_results = build_expanded_results(initial_results)
    write_results(expanded_results)