from miner import Commit
import logging
from pydriller import RepositoryMining


def createProjects(repos):
    projects = []
    for name, path in repos:
        try:
            projects.append(Project(path, name))
        except:
            logging.warning("Could not create Project for " +
                            name + " in " + path)
    return projects


def createProject(path, name):
    return Project(path, name)


class Project():
    def __init__(self, repo_path, name, fromSerializer=None): 
        if fromSerializer is not None:
            name.execute(
                "SELECT * FROM repository WHERE ID == " + str(repo_path))
            rows = cursor.fetchall()
            row = rows[0]
            self.id = row[0]
            self.path = row[1]
            self.name = row[2]
            self.creation = row[3]
            self.commits = self.getCommits(repo_path, cursor)
        else:
            self.path = repo_path
            self.name = name
            self.commits = []
            try:
                self.creation = next(RepositoryMining(
                    repo_path).traverse_commits()).committer_date
            except:
                logging.warning(
                    "Could not get committer date for " + name + " in " + repo_path)
            for commit in RepositoryMining(repo_path).traverse_commits():
                try:
                    self.commits.append(Commit.Commit(commit))
                except:
                    logging.warning(
                        "Could not create commit with hash " + commit.hash)

    def getCommits(self, id, cursor):
        cursor.execute(
            "SELECT * FROM commits WHERE repository_id == " + str(id))
        rows = cursor.fetchall()
        commits = []
        for row in rows:
            commits.append(Commit.Commit(row, cursor))
        return commits

    def getValues(self):
        s = "('"
        s += self.path + "','"
        s += self.name + "','"
        s += str(self.creation) + "')"
        return s
