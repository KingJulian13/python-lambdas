import pydriller
import logging
from miner import Modification


class Commit():
    def __init__(self, driller_commmit, cursor=None): 
        if cursor is not None:
            self.id = driller_commmit[0]
            self.branches = driller_commmit[2]
            self.author = driller_commmit[3]
            self.message = driller_commmit[4]
            self.date = driller_commmit[5]
            self.isMerge = driller_commmit[6]
            self.modifications = self.getModifications(self.id, cursor)
        else:
            self.branches = driller_commmit.branches
            self.author = driller_commmit.author
            self.message = driller_commmit.msg
            self.date = driller_commmit.author_date
            self.isMerge = driller_commmit.merge
            self.modifications = []
            for modification in driller_commmit.modifications:
                if modification.filename.endswith(".py"):
                    try:
                        self.modifications.append(
                            Modification.Modification(modification))
                    except:
                        logging.warning(
                            "Could not create modification object for file " + modification.filename)

    def getModifications(self, id, cursor):
        cursor.execute(
            "SELECT * FROM modification WHERE commit_id == " + str(id))
        rows = cursor.fetchall()
        modifications = []
        for row in rows:
            modifications.append(Modification.Modification(row, cursor))
        return modifications

    def getValues(self, parent_id):
        s = "('"
        s += str(parent_id) + "','"
        s += str(self.branches).replace("{'", "").replace("'}", "") + "','"
        s += str(self.author.name) + "','"
        s += str(self.message.replace("'", '"')) + "','"
        s += str(self.date) + "','"
        s += str(self.isMerge) + "')"
        return s
