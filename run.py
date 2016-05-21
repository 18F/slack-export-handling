import json
import re

"""
* -[ ] Go through the sqlite database
* -[x] If the message has one or more attachments
* -[x] Iterate through each attachment in the attachments
* -[ ] Check to see whether "google.com" is in the link url
* -[ ] If google.com is present save the message to sqlite3
"""

class SlackAttachmentCheck:
    def __init__():
        pass

    def iterate_through_json_obj(messages):
        """
        This pulls out a messages array from a JSON file where there are attachments
        """
        results = [msg for msg in messages if "hidden" not in msg and "attachments" in msg]
        return results


    def check_urls_in_attachments(pattern, messages):
        """
        This checks for a pattern in a messages array to see if there is a match
        """
        results = []
        for msg in messages:
            matches = [attachment for attachment in msg["attachments"] if re.search(pattern, attachment.get("from_url"))]
            if matches:
                results.append(msg)
        return results


if __name__ == "__main__":
    pass
