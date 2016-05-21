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

Now, run `python slackToDB.py`.
