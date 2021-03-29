import os
import ast
import sqlite3
import inspect
import glob
import logging
import re
from serializer import SQLiteSerializer
from datetime import datetime
current_directory = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))
trace_folder = current_directory + "/logs/traces/"
conn = None
cursor = None
scopeCounter = 0


def dbsetup():
    global current_directory
    global conn
    global cursor
    logging.info("SQLite: Generating Database")
    prefix = "CREATE TABLE IF NOT EXISTS"
    current_directory = os.path.dirname(
        os.path.dirname(os.path.realpath(__file__)))
    conn = sqlite3.connect(current_directory + "/traces.db")
    cursor = conn.cursor()

    logging.info("SQLite: Creating tables")
    cursor.execute(
        prefix + ' "lambda" ("lid" TEXT NOT NULL, "line" INTEGER NOT NULL, "file" TEXT NOT NULL, "name" TEXT NOT NULL, "repository" TEXT NOT NULL, "lambdaID" INTEGER NOT NULL, PRIMARY KEY (lid, line));')
    cursor.execute(prefix + ' "lambdaexecution" ("id" INTEGER PRIMARY KEY AUTOINCREMENT,"lambdaID" INTEGER NOT NULL, "lid" TEXT NOT NULL,"type" TEXT NOT NULL,CONSTRAINT "0" FOREIGN KEY ("lid") REFERENCES "lambda" ("lid") ON UPDATE NO ACTION ON DELETE NO ACTION, CONSTRAINT "1" FOREIGN KEY ("lambdaID") REFERENCES "lambda" ("lambdaID") ON UPDATE NO ACTION ON DELETE NO ACTION);')
    cursor.execute(prefix + ' "scopeexecution" ("id" INTEGER PRIMARY KEY AUTOINCREMENT,"lid" TEXT NOT NULL, "variable" TEXT NOT NULL, "type" TEXT NOT NULL, "exec" INTEGER NOT NULL,CONSTRAINT "0" FOREIGN KEY ("lid") REFERENCES lambda ("lid") ON UPDATE NO ACTION ON DELETE NO ACTION);')
    conn.commit()
    logging.info("SQLite: Database initialised")


def execute():
    SQLiteSerializer.setup()
    files = glob.glob(trace_folder + "/*.trace")

    for file in files:
        data = open(file, "r")
        init = data.readline().strip()
        if init != "Initialised":
            print("WRONG FILE START", init)
        else:
            line = data.readline()
            while line:
                if line.startswith("#L"):
                    line = parseLambda(data)
                elif line.startswith("#S"):
                    line = parseScope(data)
                else:
                    print(line)
                    line = data.readline()
    SQLiteSerializer.close()


def parseLambda(data):
    line = data.readline()
    lfile = None
    lid = None
    lname = None
    ltype = None
    while line.startswith(">"):
        value = line[line.find("[")+1:line.find("]")]
        if line.startswith(">1"):
            lfile = value
        if line.startswith(">2"):
            lid = value
        if line.startswith(">3"):
            lname = value
        if line.startswith(">4"):
            ltype = value
        line = data.readline()

    SQLiteSerializer.serializeLambdaExecution(lfile, lid, lname, ltype)
    return line


def parseScope(data):
    global scopeCounter
    line = data.readline()
    lfile = None
    lline = None
    lid = None
    llocals = []
    while line.startswith(">"):
        if line.startswith(">4"):
            parts = line.split("=")
            rawname = parts[0]
            rawtype = parts[1]
            lname = rawname[rawname.find("[")+1:rawname.find("]")]
            ltype = rawtype[rawtype.find("[")+1:rawtype.find("]")]
            llocals.append((lname, ltype))
        else:
            value = line[line.find("[")+1:line.find("]")]
            if line.startswith(">1"):
                lfile = value
            if line.startswith(">2"):
                lid = value
        line = data.readline()

    SQLiteSerializer.serializeScopeExecution(lfile, lid, llocals)
    scopeCounter = scopeCounter + 1
    return line


def close():
    conn.close()
