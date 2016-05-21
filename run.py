import json
import re

"""
* -[x] Go through the sqlite database
* -[x] If the message has one or more attachments
* -[x] Iterate through each attachment in the attachments
* -[x] Check to see whether "google.com" is in the link url
* -[x] If docs\.google\.com is present save the message to csv
"""


class SlackAttachmentCheck:
    def __init__():
        pass

    def iterate_through_json_obj(query):
        """
        This pulls out a messages array from a JSON file where there are attachments
        """
        return [(row, json.loads(row['data'])) for row in query.dicts() if 'hidden' not in row['data'] and json.loads(row['data']).get('attachments') or json.loads(row['data']).get('subtype') == 'file_share']

    def check_urls_in_attachments(pattern, rows):
        """
        This checks for a pattern in a messages array to see if there is a match
        """
        results = []
        for msg, attachment in rows:
            if 'attachments' in attachment:
                file_type = 'attachment'
                url = attachment['attachments'][0].get('from_url')
            else:
                file_type = 'file_share'
                if attachment.get('file'):  # Apparently, there's an edge case with uploaded null files. /shrug
                    url = attachment['file']['url_private']
            if url and re.search(pattern, url):
                results.append((msg['id'], url, msg['channel'], msg['channel_date'], attachment['user'], file_type))
        return results


if __name__ == "__main__":
    from models import Slack
    import csv

    query = (Slack.select())
    rows = SlackAttachmentCheck.iterate_through_json_obj(query)

    pattern = "docs\.google\.com"
    results = SlackAttachmentCheck.check_urls_in_attachments(pattern, rows)

    with open('results.csv', 'w') as csvfile:
        slackwriter = csv.writer(csvfile)
        for res in results:
            slackwriter.writerow(res)
