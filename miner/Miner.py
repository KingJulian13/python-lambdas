import sqlite3
import os
import logging
import requests
import sys
import json
from git import Repo
from git import GitCommandError
current_directory = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))
log_folder = current_directory + "/logs/"
repo_folder = current_directory + "/repositories/"
encodings = ["utf-8", "utf-16", "iso-8859-15", "cp437"]


def getAuthToken(): 
    tokenfile = open(current_directory + "/github.token","r")
    token = tokenfile.readline()
    tokenfile.close()
    return token


def createFolders():
    if not os.path.isdir(log_folder):
        try:
            logging.info(
                "Logging directory not found - Creating new folder at " + log_folder)
            os.mkdir(log_folder)
        except:
            logging.error("Could not create Logging directory!")
            sys.exit
    if not os.path.isdir(log_folder):
        try:
            logging.info(
                "Repository directory not found - Creating new folder at " + repo_folder)
            os.mkdir(repo_folder)
        except:
            logging.error("Could not create Repository directory!")
            sys.exit


def downloadRepos(repos):
    logging.info("Updating Repos...")
    downloads = 0
    paths = []
    for repo, folder in repos:
        getRepodataUrl(repo)
        path = repo_folder + folder
        paths.append((folder, path))

        if not os.path.isdir(path):
            downloads += 1

            try:

                Repo.clone_from(repo, path)
                logging.info("Cloned repo " + repo + " successfully")
            except GitCommandError:
                "Could not find repository " + repo + " at location " + path
    if downloads == 0:
        logging.info("No new repositorys to download")
    else:
        logging.info("Finished downloading " +
                     str(downloads) + " repositorys.")
    return paths


def getOfflineRepos():
    repos = next(os.walk(repo_folder))
    return list(map(lambda x: (x, repos[0] + x), repos[1]))


def getRepos(limit, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # != 30 against AD20 outlier
    cursor.execute(
        "SELECT homepage,name FROM repository WHERE id != 30 LIMIT " + str(limit))
    return cursor.fetchall()


def getRepo(id, db_path): 
    conn = sqlite3.connect(db_path)
    return conn.execute("SELECT homepage,name FROM repository WHERE id == " + str(id))


def getCodeFromFile(path):
    script_dir = os.path.dirname(__file__)
    abs_file_path = os.path.join(script_dir, path)
    file = open(abs_file_path, "r")
    return file.read()


def getRepodataUrl(repoUrl):
    try:
        repoUrl = repoUrl.replace(
            "https://github.com/", "http://api.github.com/repos/")
        repoUrl = repoUrl.replace(
            "http://github.com/", "http://api.github.com/repos/")
        repoUrl = repoUrl.replace(
            "https://www.github.com/", "http://api.github.com/repos/")
        repoUrl = repoUrl.replace(
            "http://www.github.com/", "http://api.github.com/repos/")
        header = {"Authorization": "token " + getAuthToken()}
        resp = requests.get(repoUrl, headers = header)
        status_code = resp.status_code
        if status_code == 403:
            print("Please add a github auth token to 'github.token' for increased rate limit!")
            return False
        if status_code != 200:
            print("Could not fetch ", repoUrl ,"from Github: ", resp.reason)
            return False
        r = resp.json()
        stars = r.get("stargazers_count","NULL")
        forks = r.get("forks_count","NULL")
        watchers = r.get("watchers_count","NULL")
        subscribers = r.get("subscribers_count","NULL")
        issues = r.get("open_issues_count", "NULL")
        return {
            "stars": stars,
            "forks": forks,
            "watchers": watchers, 
            "subscribers": subscribers,
            "issues": issues,
        }
    except Exception as e:
        print("Error getting API Data of ", repoUrl)
        print(e)
        return False
