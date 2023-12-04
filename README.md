# Toolfinder (working title)
A utility to search and evaluate tools for bioinformatics workflows. 

## Configuration
The configuration of the toolfinder is stored in the `toolfinder.ini` ([supported ini file structure](https://docs.python.org/3/library/configparser.html#supported-ini-file-structure)).
Each configuration value can either be changed manually in the file, or by using the `config` command (see [configure](#configure))

## Usage
1. Initialize the database
2. Load definitions
3. TBD

### Configure


### Database initialization
The command `python toolfinder.py db-init` initializes the database with the required tables.
If the database is already populated, this command will fail. If you intend to start with a fresh database, 
either configure a different database file to be used (see [Configuration](#configuration)) or use the `--reset` option.

#### Initialization with reset
The command `python toolfinder.py db-init --reset` will ask for confirmation before proceeding to erase the database.
This can be switched off by passing the flag `--noconfirm` to the command.

After all tables have been dropped, the tables will be recreated. 

### Load Definitions
In order to operate, the tool requires data to be stored in the database.
The data is currently retrieved from
* http://edamontology.org
* https://bio.tools/api/t

The command `python toolfinder.py load --all` will download all available information from all known repositories and ontologies and store the data in the database.
If you wish to only pull information from a specific repository, you can do so by omitting the `--all` flag and 
specifying the name of the repository.
For example: 
```shell
python toolfinder.py load EDAM
python toolfinder.py load biotools
```
A list of supported repository names can be obtained by running `python toolfinder.py load -h`.
