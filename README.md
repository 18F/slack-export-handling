## Set up

### Setting up the repository

* Pull down the repository.
* Set up a virtual environment
* Run `pip install -r requirements`

### Creating the database from slack export

Take the slack export in `.zip` form and save it as `data-import/data.zip`. Then:

```
cd data-import
unzip data.zip
cd ..
```

Now, run `python slackToDB.py`. This will create a sqlite database called `slack.db`.

### Running the commands

Now that you have a db, all that's needed is to run the following commands:

```
python run.py
python map-users.py
```

This will generate a file called `mapped.csv`. This is your final document.
