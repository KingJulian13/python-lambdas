import os
import logging
from evaluation import DataEval
from evaluation import DynamicEval
from evaluation import StaticEval
from datetime import datetime
from miner import Instrumentator
from miner import Miner
from miner import Project
from serializer import SQLiteSerializer
from serializer import TraceToDB
from pathlib import Path

import testrunner

Miner.createFolders()

max_num_of_repos = 2000

current_directory = os.path.dirname(os.path.realpath(__file__))
log_folder = current_directory + "/logs/"
log_filename = log_folder + datetime.now().strftime("%H-%M-%S") + '.log'
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
logging.basicConfig(filename=log_filename, level=logging.WARNING)
logging.getLogger().addHandler(consoleHandler)

database_repos = Miner.getRepos(
    max_num_of_repos, current_directory + '/pydefects.db')
repo_name_path = Miner.downloadRepos(database_repos)

Use this for only pre-downloaded repos. Ignoring Database
repo_name_path = Miner.getOfflineRepos()


def executeMining():
    SQLiteSerializer.setup()
    projects = []

    # Static analysis
    failed = []
    for name, path in repo_name_path:
        try:
            project = Project.createProject(path, name)
            projects.append(project)
            logging.info("Serializing Project " + name)
            SQLiteSerializer.serializeProject(project)
        except:
            failed.append(name)
            logging.warning("Could not create Project for " +
                            name + " in " + path)
    SQLiteSerializer.close()
    logging.info("Serialization of " + str(len(failed)) +
                 " Repositories failed.")
    logging.info(str(failed))


def hydrateData():  # Hydrate data from GitHub API into Database
    if not SQLiteSerializer.isSetup:
        SQLiteSerializer.setup()
    skipped = []
    for path, name in database_repos:
        data = Miner.getRepodataUrl(path)
        if data == False:
            logging.info("Skipping Repodata hydrating for " + name)
            skipped.append(name)
        elif type(data) == dict:
            logging.info("Hydrating " + name)
            SQLiteSerializer.serializeRepoData(name, data)
    logging.info("Skipped total hydration of " +
                 str(len(skipped)) + " Repositories.")
    logging.info(str(skipped))


def transformCode():  # Code Transformation
    SQLiteSerializer.setup()
    for repo in repo_name_path:
        try:
            logging.info("Transforming " + repo[0] + " ...")
            Instrumentator.transformRepo(repo[1], repo[0])
            SQLiteSerializer.commit()
        except Exception as e:
            logging.error("Could not transform: " +
                          str(repo[0]) + "\n" + str(e))
    SQLiteSerializer.close()


def executeTests():  # Test Execution
    SQLiteSerializer.setup()
    for repo in repo_name_path:
        logging.info("Testing " + repo[0])
        try:
            runner = testrunner.Runner(repo[0], repo[1], time_limit=60)
        except Exception as e:
            logging.warning("Error while building Runner:")
            logging.error(str(e))
        try:
            result = runner.run()
        except Exception as e:
            logging.warning("Error while executing tests:")
            logging.error(str(e))
        logging.debug(result[0])
        try:
            result = runner.get_run_result(result[0])
            logging.info(result)
            logging.error("Serializing Test Execution of " + str(repo[0]))
            SQLiteSerializer.serializeCoverage(repo[0], result.coverage)

        except Exception as e:
            logging.error("Error while getting test results:")
            logging.error(str(e))
    SQLiteSerializer.close()


executeMining()
hydrateData()
transformCode()
executeTests()
TraceToDB.execute()
DataEval.run()
StaticEval.run()
DynamicEval.run()
