import pydriller
import logging
from miner import Miner
from miner import Lambda
import ast
from pydriller import RepositoryMining

class Modification():
    def __init__(self, modification, cursor = None):
        if cursor is not None:
            self.id = modification[0]
            self.filename = modification[2]
            self.locvariation = modification[3]
            self.complexity = modification[4]
            self.methods = modification[5]
            self.addedLambdas = self.getAddedLambdas(self.id,cursor)
            self.removedLambdas = self.getRemovedLambdas(self.id,cursor)
        else:
            self.addedLambdas = []
            self.removedLambdas = []
            self.filename = modification.filename
            self.locvariation = modification.added - modification.removed
            self.complexity = modification.complexity
            self.methods = len(modification.methods)
            self.loc = modification.nloc 
            
            new_lambdas = None
            old_lambdas = None
            if modification.source_code is not None: 
                try:
                    tree = ast.parse(modification.source_code)
                    logging.debug("AST Parsed "  + str(self.filename))
                except:
                    logging.warning("AST Could not parse " + str(self.filename))
                    logging.debug(modification.source_code)
                    return
                new_lambdas = Lambda.getLambdas(tree,modification.source_code)
                if (modification.source_code_before is None):
                    self.addedLambdas.extend(new_lambdas)
                    return
                else: 
                    try:
                        tree_old = ast.parse(modification.source_code_before)
                        old_lambdas = Lambda.getLambdas(tree_old,modification.source_code_before) #old tree?
                    except:
                        logging.warning("AST Could not parse " + str(self.filename))
                        logging.debug(modification.source_code_before)
                        return 

            else: 
                if modification.source_code_before is not None:
                    try:
                        tree = ast.parse(modification.source_code_before)
                        old_lambdas = Lambda.getLambdas(tree,modification.source_code_before)
                        self.removedLambdas.extend(old_lambdas)
                    except:
                        logging.warning("Error parsing source code of raw modification in " + self.filename )
                        logging.debug(modification.source_code_before)
                        pass
                    return 
                else:
                    logging.error("Error: No source code in modification id: " + str(modification.id)) 
                    return 
            
            addedTupels = modification.diff_parsed.get("added")
            deletedTupels = modification.diff_parsed.get("deleted")
            addedLines = list(map(lambda x: x[0],addedTupels))
            deletedLines = list(map(lambda x: x[0],deletedTupels))
            for old_lamb in old_lambdas:
                line = old_lamb.getLine()
                if line in deletedLines and line not in addedLines: 
                    self.removedLambdas.append(old_lamb)
            
            for new_lamb in new_lambdas:
                line = new_lamb.getLine()
                if line in addedLines and line not in deletedLines:
                    self.addedLambdas.append(new_lamb)

            if len(self.addedLambdas) > 0:
                logging.info("Found " + str(len(self.addedLambdas)) + " new Lambdas")
            if len(self.removedLambdas) > 0:
                logging.info("Found " + str(len(self.removedLambdas)) + " removed Lambdas")


    def getAddedLambdas(self,id,cursor): 
        cursor.execute("SELECT * FROM lambda WHERE modification_id == " + str(id) + " AND kind == 1" )
        rows = cursor.fetchall()
        addedLambdas = []
        for row in rows:
            addedLambdas.append(Lambda.Lambda(row,cursor))
        return addedLambdas


    def getRemovedLambdas(self,id,cursor): 
        cursor.execute("SELECT * FROM lambda WHERE modification_id == " + str(id) + " AND kind == 2" )
        rows = cursor.fetchall()
        removedLambdas = []
        for row in rows:
            removedLambdas.append(Lambda.Lambda(row,cursor))
        return removedLambdas


    def getValues(self,parent_id):
        s = "("
        s += str(parent_id) + ",'"
        s += self.filename + "',"
        s += str(self.locvariation) + ","
        if self.complexity is not None:
            s += str(self.complexity) + ","
        else:
            s += "-1,"
        s += str(self.methods) + ")"
        return s
