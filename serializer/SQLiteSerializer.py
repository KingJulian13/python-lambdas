import sqlite3
import os
import logging

current_directory = None
conn = None
cursor = None
isSetup = False


def setup():

    global current_directory
    global conn
    global cursor
    global isSetup
    if isSetup:
        return True
    isSetup = True

    logging.info("SQLite: Generating Database")
    prefix = "CREATE TABLE IF NOT EXISTS"
    current_directory = os.path.dirname(
        os.path.dirname(os.path.realpath(__file__)))
    conn = sqlite3.connect(current_directory + "/results.db")
    cursor = conn.cursor()

    logging.info("SQLite: Creating tables")
    cursor.execute(prefix + ' "repository" ("id" INTEGER PRIMARY KEY AUTOINCREMENT,"path" TEXT NOT NULL,"name" TEXT NOT NULL,"creation" DATETIME NOT NULL,"stars" INTEGER,"watchers" INTEGER,"forks" INTEGER, "subscribers" REAL, "issues" REAL, "found_lambdas" INTEGER, "coverage" REAL);')
    cursor.execute(prefix + ' "commits" ("id" INTEGER PRIMARY KEY AUTOINCREMENT,"repository_id" INTEGER NOT NULL,"branch" TEXT NOT NULL,"author" TEXT NOT NULL,"commitMessage" TEXT NOT NULL,"date" DATETIME NOT NULL,"isMerge" INTEGER NOT NULL,CONSTRAINT "0" FOREIGN KEY ("repository_id") REFERENCES "repository" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION);')
    cursor.execute(prefix + ' "modification" ("id" INTEGER PRIMARY KEY AUTOINCREMENT,"commit_id" INTEGER NOT NULL,"filename" TEXT NOT NULL,"loc_variation" INTEGER NOT NULL,"complexity" REAL NOT NULL,"methods" INTEGER NOT NULL,CONSTRAINT "0" FOREIGN KEY ("commit_id") REFERENCES "commits" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION);')
    cursor.execute(
        prefix + ' "lambda_context" ("id" INTEGER PRIMARY KEY AUTOINCREMENT,"name" TEXT NOT NULL);')
    cursor.execute(
        prefix + ' "lambda_kind" ("id" INTEGER PRIMARY KEY AUTOINCREMENT,"name" TEXT NOT NULL);')
    cursor.execute(prefix + ' "lambda" ("id" INTEGER PRIMARY KEY AUTOINCREMENT,"modification_id" INTEGER NOT NULL,"kind" INTEGER NOT NULL,"arguments" INTEGER NOT NULL,"expressions" INTEGER NOT NULL,"line" INTEGER NOT NULL,"context" INTEGER NOT NULL,"content" TEXT NOT NULL,CONSTRAINT "0" FOREIGN KEY ("context") REFERENCES "lambda_context" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,CONSTRAINT "1" FOREIGN KEY ("kind") REFERENCES "lambda_kind" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION,CONSTRAINT "2" FOREIGN KEY ("modification_id") REFERENCES "modification" ("id") ON UPDATE NO ACTION ON DELETE NO ACTION);')

    cursor.execute(prefix + ' "transformed_file" ("id" INTEGER PRIMARY KEY AUTOINCREMENT,"repository_name" INTEGER NOT NULL,"file_path" INTEGER NOT NULL, "file_coverage" REAL, CONSTRAINT "0" FOREIGN KEY ("repository_name") REFERENCES "repository" ("name"));')
    cursor.execute(prefix + ' "transformed_lambda" ("id" INTEGER PRIMARY KEY AUTOINCREMENT,"file_path" TEXT NOT NULL,"internal_id" INTEGER NOT NULL, "line" INTEGER NOT NULL, CONSTRAINT "0" FOREIGN KEY ("file_path") REFERENCES "transformed_file" ("file_path"));')
    cursor.execute(prefix + ' "executed_lambda_arg" ("id" INTEGER PRIMARY KEY AUTOINCREMENT,"lambda_id" INTEGER NOT NULL, "name" TEXT NOT NULL, "type" TEXT NOT NULL, CONSTRAINT "0" FOREIGN KEY ("lambda_id") REFERENCES "transformed_lambda" ("id"));')
    cursor.execute(prefix + ' "executed_lambda_scope" ("id" INTEGER PRIMARY KEY AUTOINCREMENT,"lambda_id" INTEGER NOT NULL, CONSTRAINT "0" FOREIGN KEY ("lambda_id") REFERENCES "transformed_lambda" ("id"));')
    cursor.execute(prefix + ' "executed_lambda_scope_var" ("id" INTEGER PRIMARY KEY AUTOINCREMENT,"scope_id" INTEGER NOT NULL,"name" TEXT NOT NULL, "type" TEXT NOT NULL, CONSTRAINT "0" FOREIGN KEY ("scope_id") REFERENCES "executed_lambda_scope" ("id") );')

    logging.info("SQLite: Adding basevalues")
    cursor.execute(
        "INSERT INTO 'lambda_kind'(name) SELECT 'added' WHERE NOT EXISTS(SELECT 1 FROM 'lambda_kind' WHERE name = 'added');")
    cursor.execute(
        "INSERT INTO 'lambda_kind'(name) SELECT 'removed' WHERE NOT EXISTS(SELECT 1 FROM 'lambda_kind' WHERE name = 'removed');")
    cursor.execute(
        "INSERT INTO 'lambda_context'(name) SELECT 'other' WHERE NOT EXISTS(SELECT 1 FROM 'lambda_context' WHERE name = 'other');")
    cursor.execute(
        "INSERT INTO 'lambda_context'(name) SELECT 'return' WHERE NOT EXISTS(SELECT 1 FROM 'lambda_context' WHERE name = 'return');")
    cursor.execute(
        "INSERT INTO 'lambda_context'(name) SELECT 'call' WHERE NOT EXISTS(SELECT 1 FROM 'lambda_context' WHERE name = 'call');")
    cursor.execute(
        "INSERT INTO 'lambda_context'(name) SELECT 'returncall' WHERE NOT EXISTS(SELECT 1 FROM 'lambda_context' WHERE name = 'returncall');")
    conn.commit()
    logging.info("SQLite: Database initialised")


def close():
    global isSetup
    isSetup = False
    conn.commit()
    conn.close()


def commit():
    if isSetup:
        conn.commit()


def serializeFileTransformation(reponame, filepath):
    reponame = str(reponame)
    filepath = str(filepath)
    logging.debug("INSERT INTO 'transformed_file' (repository_name, file_path) VALUES ('" +
                  reponame + "','" + filepath + "');")
    cursor.execute("INSERT INTO 'transformed_file' (repository_name, file_path) VALUES ('" +
                   reponame + "','" + filepath + "');")


def serializeLambdaTransformation(filepath, lambda_id, line):
    filepath = str(filepath)
    lambda_id = str(lambda_id)
    line = str(line)
    logging.debug("INSERT INTO 'transformed_lambda' (file_path, internal_id, line) VALUES ('" +
                  filepath + "','" + lambda_id + "','" + line + "');")
    cursor.execute("INSERT INTO 'transformed_lambda' (file_path, internal_id, line) VALUES ('" +
                   filepath + "','" + lambda_id + "','" + line + "');")


def serializeLambdaExecution(file_path, internal_lambda_id, name, ltype):
    file_path = str(file_path)
    internal_lambda_id = str(internal_lambda_id)
    name = str(name)
    ltype = str(ltype)
    logging.debug("SELECT id FROM 'transformed_lambda' WHERE internal_id = '" +
                  internal_lambda_id + "' AND file_path = '" + file_path + "'")
    cursor.execute("SELECT id FROM 'transformed_lambda' WHERE internal_id = '" +
                   internal_lambda_id + "' AND file_path = '" + file_path + "'")
    try:
        lambda_id = cursor.fetchall()[0][0]
        lambda_id = str(lambda_id)
        logging.debug("INSERT INTO 'executed_lambda_arg' (lambda_id, name, type) VALUES ('" +
                      lambda_id + "','" + name.replace("'", '"') + "','" + ltype.replace("'", '"') + "');")
        cursor.execute("INSERT INTO 'executed_lambda_arg' (lambda_id, name, type) VALUES ('" +
                       lambda_id + "','" + name.replace("'", '"') + "','" + ltype.replace("'", '"') + "');")
    except Exception as e:
        logging.warning(
            "Could not find lambda transformation for ARG execution:")
        logging.debug("  file_path: " + file_path +
                      ", internal_lambda_id: " + internal_lambda_id)
        logging.debug("  name: " + name + ", ltype: " + ltype)
        logging.debug(e)


def serializeScopeExecution(file_path, internal_lambda_id, data):
    file_path = str(file_path)
    internal_lambda_id = str(internal_lambda_id)
    logging.debug("SELECT id FROM 'transformed_lambda' WHERE internal_id = '" +
                  internal_lambda_id + "' AND file_path = '" + file_path + "'")
    cursor.execute("SELECT id FROM 'transformed_lambda' WHERE internal_id = '" +
                   internal_lambda_id + "' AND file_path = '" + file_path + "'")
    try:
        lambda_id = cursor.fetchall()[0][0]
        lambda_id = str(lambda_id)
        logging.debug(
            "INSERT INTO 'executed_lambda_scope' (lambda_id) VALUES ('" + lambda_id + "');")
        cursor.execute(
            "INSERT INTO 'executed_lambda_scope' (lambda_id) VALUES ('" + lambda_id + "');")
        last_id = cursor.lastrowid
        for name, stype in data:
            serializeScopeAttribute(last_id, name, stype)
    except Exception as e:
        logging.warning(
            "Could not find lambda transformation for SCOPE execution:")
        logging.debug("  file_path: " + file_path +
                      ", internal_lambda_id: " + internal_lambda_id)
        logging.debug("  " + str(data))


def serializeScopeAttribute(execition_db_id, name, stype):
    execition_db_id = str(execition_db_id)
    name = str(name)
    stype = str(stype)
    logging.debug("INSERT INTO 'executed_lambda_scope_var' (scope_id, name, type) VALUES ('" +
                  execition_db_id + "','" + name.replace("'", '"') + "','" + stype.replace("'", '"') + "');")
    cursor.execute("INSERT INTO 'executed_lambda_scope_var' (scope_id, name, type) VALUES ('" +
                   execition_db_id + "','" + name.replace("'", '"') + "','" + stype.replace("'", '"') + "');")


def serializeProject(project):
    logging.debug(
        "INSERT INTO 'repository' (path,name,creation) VALUES " + project.getValues())
    cursor.execute(
        "INSERT INTO 'repository' (path,name,creation) VALUES " + project.getValues())
    last_id = cursor.lastrowid
    for commit in project.commits:
        serializeCommit(commit, last_id)
    conn.commit()


def serializeCommit(commit, parent_id):
    logging.debug("INSERT INTO 'commits' (repository_id,branch,author,commitMessage,date,isMerge) VALUES " +
                  commit.getValues(parent_id))
    cursor.execute(
        "INSERT INTO 'commits' (repository_id,branch,author,commitMessage,date,isMerge) VALUES " + commit.getValues(parent_id))
    last_id = cursor.lastrowid
    for modification in commit.modifications:
        serializeModification(modification, last_id)


def serializeModification(modification, parent_id):
    logging.debug("INSERT INTO 'modification' (commit_id,filename,loc_variation,complexity,methods) VALUES " +
                  modification.getValues(parent_id))
    cursor.execute("INSERT INTO 'modification' (commit_id,filename,loc_variation,complexity,methods) VALUES " +
                   modification.getValues(parent_id))
    last_id = cursor.lastrowid
    for added in modification.addedLambdas:
        serializeLambda(added, last_id, 1)
    for removed in modification.removedLambdas:
        serializeLambda(removed, last_id, 2)


def serializeLambda(lamb, parent_id, kind):
    if type(lamb) is tuple:
        logging.debug("INSERT INTO 'lambda' (modification_id,kind,arguments,expressions,line,context,content) VALUES " +
                      lamb[1].getValues(parent_id, kind))
        cursor.execute("INSERT INTO 'lambda' (modification_id,kind,arguments,expressions,line,context,content) VALUES " +
                       lamb[1].getValues(parent_id, kind))
        prior = cursor.lastrowid
        logging.debug("INSERT INTO 'lambda_pre_modification' (prior_lambda_id,kind,arguments,expressions,line,context,content) VALUES " +
                      lamb[0].getValues(0, kind, prior))
        cursor.execute("INSERT INTO 'lambda_pre_modification' (prior_lambda_id,kind,arguments,expressions,line,context,content) VALUES " +
                       lamb[0].getValues(0, kind, prior))
    else:
        logging.debug("INSERT INTO 'lambda' (modification_id,kind,arguments,expressions,line,context,content) VALUES " +
                      lamb.getValues(parent_id, kind))
        cursor.execute("INSERT INTO 'lambda' (modification_id,kind,arguments,expressions,line,context,content) VALUES " +
                       lamb.getValues(parent_id, kind))


def serializeRepoData(name, data):
    setup()
    stars = data["stars"]
    watchers = data["watchers"]
    forks = data["forks"]
    subscribers = data["subscribers"]
    issues = data["issues"]
    cursor.execute("UPDATE 'repository' SET stars = " + str(stars) + ", watchers = " + str(watchers) + ", forks = " + str(forks) +
                   ", subscribers = " + str(subscribers) + ", issues = " + str(issues) + " WHERE repository.name = '" + str(name) + "'")
    conn.commit()


def serializeCoverage(name, coverage):
    setup()
    cursor.execute("UPDATE 'repository' SET coverage = " +
                   str(coverage) + " WHERE repository.name = '" + str(name) + "'")
    conn.commit()


def serializeTransformations(name, amount):
    setup()
    cursor.execute("UPDATE 'repository' SET transformations = " +
                   str(amount) + " WHERE repository.name = '" + str(name) + "'")
    conn.commit()


def getProjects():
    cursor.execute("SELECT id,name FROM repository")
    return cursor.fetchall()
