import csv

with open('mapped.csv', 'r') as csvfile:
    msgs = [msg for msg in csv.reader(csvfile)]

unique_urls = []
results = []
for msg in msgs:
    if msg[1] not in unique_urls:
        unique_urls.append(msg[1])
        results.append(msg)

with open('deduped.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for result in results:
        writer.writerow(result)
