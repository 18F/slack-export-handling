## slack-export-handling

Sometimes there are occasions when a Slack export needs to be searched. For example, there might be need to find a record of a conversation between former employees.

Slack already includes a way to export all records, but there's no way to search those exports. In order to make a search process quick (and to avoid people having to manually read more records than needed), we created this tool.

## Set up

### Setting up the repository

* Pull down the repository.
* Set up a virtual environment.
* Run `pip install -r requirements.txt`.

### Creating the database from slack export

Take the slack export in `.zip` form and save it as `data-import/data.zip`. Then:

```
cd data-import
unzip data.zip
cd ..
```

You should now have `/data-import` full of the channel directories and a handful of `json` files from your export.

You can now create a sqlite database and import your Slack data by running `python import_slack.py`

Note that if you wish to use the legacy slack-url commands, you'll need to pass a `legacy` argument to the importer.
Otherwise the database table will not be created -- it takes a while.

`python import_slack.py legacy`

For more information, see [Legacy commands](#legacy-commands) below.


### Searching the database

You can search the sqlite database from the command line by running `search_slack.py` and passing your search term to it:

`python search_slack.py "my search term"`

You can also pass multiple terms, which will combine the results, removing duplicates. So, for example, if you wanted to search for 
"Hello world" and "My first blog post", you would pass in:

`python search_slack.py "Hello world" "My first blog post"`

Which would find any references to either of those phrases. Remember, multi-word phrases will need to be wrapped in quotes. 
Single words do not, but it's still not a bad habit to get into.


#### Expanding or contracting the search

By default, the search will get matching results for your terms, then expand the search within the same channel by 20 minutes 
before and after the initial result to provide extra context. You can control that context expansion with the `--expand_to` argument
and by passing the number of minutes you'd like to expand out to `search_slack.py`:

`python search_slack.py 'my search term' --expand_to=30`

Alternately, if you'd like to only pull exact matches, pass 0 and no expansion will happen:

`python search_slack.py 'my search term' --expand_to=0`


### Working directly with the database
When the Slack data is imported, models are created in `models.py` using the [PeeWee ORM](http://docs.peewee-orm.com/en/latest/index.html), 
which allows lightweight database querying with a syntax that should look pretty familiar to Django's ORM. 
For details, see [the PeeWee docs](http://docs.peewee-orm.com/en/latest/peewee/quickstart.html#retrieving-data).


### Legacy commands

Legacy slack-url commands can still be run as before:

```
python run.py
python map-users.py
python dedupe.py
```

This will generate a file called `deduped.csv`. This is your final document.
