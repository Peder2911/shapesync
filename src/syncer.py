#!/usr/bin/env python3 

import subprocess
import os
import sys
import watchgod
import yaml
import pickle
import logging

logger = logging.getLogger(__name__)

CHANGENAMES = [
    "created",
    "updated",
    "deleted"
]

ENVVALUES= ["host","port","user","password","db"]

if all([os.getenv(v.upper()) is not None for v in ENVVALUES]):
    CONFIG = {v:os.getenv(v.upper()) for v in ENVVALUES}
elif os.getenv("CONFIG_FILE") is not None:
    with open(os.getenv("CONFIG_FILE")) as f:
        CONFIG = yaml.safe_load(f)
else:
    raise Exception("No config information set!!")

if os.getenv("WATCH") is None:
    raise Exception("Need to set WATCH")

def toTableName(path):
    _,fname = os.path.split(path)
    fname,_ = os.path.splitext(fname)
    return fname

def userstring(config):
    """
    Adds password if applicable
    """

    user = [config["user"]]
    if config["password"] != "":
        user += [config["password"]]
    user = ":".join(user)
    return user 

def dbUrl(config):
    config["userstring"] = userstring(config)
    template = "postgresql://{userstring}@{host}:{port}/{db}"
    return template.format(**config)

def createData(url,filepath,transArgs = ["-W=\"LATIN1\""]):
    """
    Create a new table with a name corresponding to the filename
    """
    tableName = toTableName(filepath)

    transform = subprocess.Popen(["shp2pgsql","-d"] + transArgs +[ filepath,tableName], 
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE) 

    t_out,t_err = transform.communicate()

    if transform.returncode != 0:
        raise Exception("\x1b[31m"+t_err.decode()+"\x1b[0m")
    else:
        logger.info("Transform {} OK!".format(tableName))

    push = subprocess.Popen(["psql",url],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)

    p_out,p_err = push.communicate(t_out)

    if push.returncode != 0:
        raise Exception("\x1b[31m"+p_err.decode()+"\x1b[0m")
    else:
        logger.info("Push {} OK!".format(tableName))

def deleteData(url,filepath):
    """
    Drop table with the name corresponding to the filename
    """
    tableName = toTableName(filepath)

    command = "DROP TABLE {};".format(tableName)
    remove = subprocess.Popen(["psql",url],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
    out,err = remove.communicate(command.encode())
    if remove.returncode != 0:
        raise Exception("\x1b[31m"+err.decode()+"\x1b[0m")
    else:
        logger.info("Delete {} OK!".format(tableName))

def handleChange(url,change,filepath):
    """
    Casing function, figuring out what to do when
    a file changes in a certain way. 
    """
    if change == "deleted":
        logger.info("Deleting data associated with {}".format(filepath))
        deleteData(url,filepath)
    else: 
        logger.info("Updating data associated with {}".format(filepath))
        createData(url,filepath)

if __name__ == "__main__":

    dest = os.getenv("WATCH") or "/app/data"

    logging.basicConfig(
            level = os.getenv("LOGLEVEL") or logging.INFO,
            format = "%(asctime)s %(levelname)s %(name)s %(message)s"
        )

    logger.info("Watching {} for file changes".format(dest))
    url = dbUrl(CONFIG) 
    for c in watchgod.watch(dest):
        for change, filepath in c:
            change = CHANGENAMES[change-1]
            if os.path.splitext(filepath)[1] == ".shp":
                handleChange(url, change, filepath)
