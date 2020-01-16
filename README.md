
# Syncer

This tool allows you to sync collections of shapesfiles to a postgis server easily.
Comes with a dockerfile for portability. Set the following environment variables:

WATCH = _path to the root of your data folder_ 

and

CONFIG_FILE = _location of your configuration file (see defaults/config.yaml for format)_

or

HOST
PORT
USER
PASSWORD
DB

Corresponding to how you would call psql (with host, port, username, password
and the target database).

Not formally tested! Only battle tested. (Until i have the time). 
