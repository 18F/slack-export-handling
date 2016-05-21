import json
import re

"""
* -[x] Go through the sqlite database
* -[x] If the message has one or more attachments
* -[x] Iterate through each attachment in the attachments
* -[x] Check to see whether "google.com" is in the link url
* -[x] If (drive|docs).google.com is present save the message to csv
"""


class SlackAttachmentCheck:
    def __init__():
        pass

    def iterate_through_json_obj(query):
        """
        This pulls out a messages array from a JSON file where there are attachments
        """
        return [(row, json.loads(row['data'])) for row in query.dicts() if 'hidden' not in row['data'] and json.loads(row['data']).get('attachments')]

    def check_urls_in_attachments(pattern, rows):
        """
        This checks for a pattern in a messages array to see if there is a match
        """
        results = []
        for msg, attachment in rows:
            url = attachment['attachments'][0].get("from_url")

            if url and re.search(pattern, url):
                results.append((msg['id'], url, msg['channel'], msg['channel_date'], attachment['user']))
        return results


if __name__ == "__main__":
    from models import Slack
    import csv

    query = (Slack.select())
    rows = SlackAttachmentCheck.iterate_through_json_obj(query)

    pattern = "(docs|drive).google.com"
    results = SlackAttachmentCheck.check_urls_in_attachments(pattern, rows)

    print(results)
    # with open('results.csv', 'w') as csvfile:
    #     slackwriter = csv.writer(csvfile)
    #     for res in results:
    #         slackwriter.writerow(res)
