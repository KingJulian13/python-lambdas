import numpy
import sqlite3
import os
import matplotlib.dates
import matplotlib.pyplot as plt
import random
import numpy
import copy
import pandas
import matplotlib.ticker as plticker
import operator
import itertools
import copy
import re
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from matplotlib.pyplot import figure
from matplotlib.dates import drange, num2date
from dateutil.relativedelta import relativedelta
from pandas.plotting import table
from matplotlib.ticker import MaxNLocator

import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
numpy.set_printoptions(threshold=sys.maxsize)

current_directory = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))
conn = sqlite3.connect(current_directory + "/results.db")
cursor = conn.cursor()

font = {'size': 12}
matplotlib.rc('font', **font)


def executionsAndTypesPFile():
    cursor.execute("""
    SELECT transformed_lambda.file_path,executed_lambda_arg.type, COUNT(executed_lambda_arg.id) FROM transformed_lambda 
    JOIN executed_lambda_arg ON executed_lambda_arg.lambda_id = transformed_lambda.id

    GROUP BY transformed_lambda.file_path, executed_lambda_arg.type, transformed_lambda.internal_id
    ORDER BY COUNT(executed_lambda_arg.id) DESC
    LIMIT 50
    """)
    fileTypeCount = cursor.fetchall()
    efile = list(map(lambda x:  x[0], fileTypeCount))
    etype = list(map(lambda x: x[1], fileTypeCount))
    ecount = list(map(lambda x: x[2], fileTypeCount))   

    f = []
    for a,b in zip(efile,etype):
        result = re.search('(?s:.*)/(.*)', a)
        result2 = re.search('<(.*)>', b)
        filename = result2.group(1)
        if  "." in filename:
            filename = "..." + filename.split('.')[-1]

        f.append(result.group(1) + "   "+  filename)

    fig, ax = plt.subplots()
    ax.bar(f, ecount,color="#7fbde9")
    fig.set_size_inches(14, 5)
    plt.yscale('log')
    ax.tick_params(axis="x",direction="in", pad=-250)
    plt.xticks(rotation=90)
    plt.grid(True,axis='y')
    plt.xlabel('Lambdas', fontsize=16)
    plt.ylabel('Anzahl Ausführungen', fontsize=16)
    plt.savefig("plots/6-dynamic/dyn-executionsAndTypesPFile.png",dpi=500)


def topTypes(): 
    cursor.execute("SELECT transformed_lambda.file_path, transformed_lambda.internal_id, executed_lambda_arg.type FROM repository JOIN transformed_file ON repository.name == transformed_file.repository_name JOIN transformed_lambda ON transformed_file.file_path == transformed_lambda.file_path JOIN executed_lambda_arg ON executed_lambda_arg.lambda_id == transformed_lambda.id GROUP BY transformed_lambda.id, executed_lambda_arg.type")
    fileLambdaTypes = cursor.fetchall()
    results = {}
    lambdas = {}
    for (f, l, t) in fileLambdaTypes:
        results[t] = results.get(t, 0) + 1
        lambdas[str(f) + str(l)] = lambdas.get(str(f) + str(l), 0) + 1

    values = list(results.values())
    labels = list(results.keys())
    labels = list(map(lambda x: x[8:-2].replace('.', '.\n'), labels))
    values, labels = zip(*sorted(zip(values, labels), reverse=True))

    top5PyLabels, top5PyValues = zip(
        *((label, value) for label, value in zip(labels, values) if label.find(".") == -1))
    top5PyLabels = top5PyLabels[:5]
    top5PyValues = top5PyValues[:5]
    top5ExtLabels, top5ExtValues = zip(
        *((label, value) for label, value in zip(labels, values) if label.find(".") != -1))
    top5ExtLabels = top5ExtLabels[:5]
    top5ExtValues = top5ExtValues[:5]
    top5MockLabels, top5MockValues = zip(
        *((label, value) for label, value in zip(labels, values) if label.lower().find("mock") != -1))
    top5MockLabels = top5MockLabels[:5]
    top5MockValues = top5MockValues[:5]

    fig, ax = plt.subplots(1, 3)
    fig.set_size_inches(14, 5)
    fig.tight_layout()
    ax[0].bar(top5PyLabels, top5PyValues, color="C0")
    ax[1].bar(top5ExtLabels, top5ExtValues, color="C1")
    ax[2].bar(top5MockLabels, top5MockValues, color="C2")
    ax[1].yaxis.set_major_locator(MaxNLocator(integer=True))
    ax[0].set_title('Primitive Typen')
    ax[1].set_title('Externe Typen')
    ax[2].set_title('Mocking Typen')
    ax[0].yaxis.grid(True)
    ax[1].yaxis.grid(True)
    ax[2].yaxis.grid(True)
    fig.subplots_adjust(bottom=0.2)
    plt.savefig("plots/6-dynamic/dyn-toptypes.png",dpi=500)


def allTopTypes(): 
    cursor.execute("SELECT transformed_lambda.file_path, transformed_lambda.internal_id, executed_lambda_arg.type FROM repository JOIN transformed_file ON repository.name == transformed_file.repository_name JOIN transformed_lambda ON transformed_file.file_path == transformed_lambda.file_path JOIN executed_lambda_arg ON executed_lambda_arg.lambda_id == transformed_lambda.id GROUP BY transformed_lambda.id, executed_lambda_arg.type")
    fileLambdaTypes = cursor.fetchall()
    results = {}
    lambdas = {}
    for (f, l, t) in fileLambdaTypes:
        results[t] = results.get(t, 0) + 1
        lambdas[str(f) + str(l)] = lambdas.get(str(f) + str(l), 0) + 1

    values = list(results.values())
    labels = list(results.keys())
    labels = list(map(lambda x: x[8:-2].replace('.', '.\n'), labels))
    values, labels = zip(*sorted(zip(values, labels), reverse=True))
    colors = []
    for label in labels:
        if label.find(".") == -1:
            colors.append("C0")
        elif label.lower().find("mock") != -1:
            colors.append("C2")
        elif label.find(".") != -1:
            colors.append("C1")

    fig, ax = plt.subplots(1, 1)
    ax.bar(labels, values, color=colors, width=1.0)
    ax.yaxis.grid(True)
    plt.yscale('log')
    fig.set_size_inches(14, 5)
    ax.set_xticklabels([])
    fig.tight_layout()
    plt.xlabel('Typen', fontsize=16)
    plt.ylabel('Häufigkeit', fontsize=16)
    plt.savefig("plots/6-dynamic/dyn-allTopTypes.png", dpi=500, pad_inches=0)


# Helper
def getLambdaCoverageOfRepo(repository_name):
    cursor.execute("SELECT transformed_lambda.id, transformed_lambda.file_path FROM repository JOIN transformed_file ON repository.name == transformed_file.repository_name JOIN transformed_lambda ON transformed_file.file_path == transformed_lambda.file_path WHERE repository.name='" + str(repository_name) + "'")
    allLambdasList = cursor.fetchall()
    allLambdas = list(map(lambda x: x[0], allLambdasList))
    allTestLambdas = list(filter(lambda x: 'test' in x[1], allLambdasList))
    allTestLambdas = list(map(lambda x: x[0], allTestLambdas))
    allSrcLambdas = list(filter(lambda x: 'test' not in x[1], allLambdasList))
    allSrcLambdas = list(map(lambda x: x[0], allSrcLambdas))
    cursor.execute("SELECT transformed_lambda.id,transformed_lambda.file_path, COUNT(executed_lambda_scope.id) FROM repository JOIN transformed_file ON repository.name == transformed_file.repository_name JOIN transformed_lambda ON transformed_file.file_path == transformed_lambda.file_path JOIN executed_lambda_scope ON executed_lambda_scope.lambda_id == transformed_lambda.id WHERE repository.name ='" + str(repository_name) + "' GROUP BY transformed_lambda.id")
    lambdaExecutionsList = cursor.fetchall()
    lambdaExecutions = {}
    lambdaTestExecutions = {}
    lambdaSrcExecutions = {}
    for lid, file_path, executions in lambdaExecutionsList:
        lambdaExecutions[lid] = executions
        if 'test' in str(file_path):
            lambdaTestExecutions[lid] = executions
        else:
            lambdaSrcExecutions[lid] = executions

    results = {}
    for lamb in allLambdas:
        results[lamb] = lambdaExecutions.get(lamb, 0)
    srcResults = {}
    for lamb in allSrcLambdas:
        srcResults[lamb] = lambdaSrcExecutions.get(lamb, 0)
    testResults = {}
    for lamb in allTestLambdas:
        testResults[lamb] = lambdaTestExecutions.get(lamb, 0)

    notCovered = (list(filter(lambda x: x[1] == 0, results.items())))
    covered = list(filter(lambda x: x[1] > 0, results.items()))
    testNotCovered = (list(filter(lambda x: x[1] == 0, results.items())))
    testCovered = list(filter(lambda x: x[1] > 0, results.items()))
    srcNotCovered = (list(filter(lambda x: x[1] == 0, results.items())))
    srcCovered = list(filter(lambda x: x[1] > 0, results.items()))
    return [(notCovered, covered, allLambdas), (testNotCovered, testCovered, allTestLambdas), (srcNotCovered, srcCovered, allSrcLambdas)]


def coverageVSSrcLambdaCoverage(): 
    cursor.execute(
        "SELECT repository.name,repository.coverage FROM repository")
    repoCoverage = cursor.fetchall()
    repos = {}
    counter = 0
    for reponame, coverage in repoCoverage:
        print("Getting Lambda Coverage of ",reponame," ",counter,"/",len(repoCoverage))
        counter += 1
        notCovered, covered, allLambdas = getLambdaCoverageOfRepo(reponame)[2]
        if (len(allLambdas) > 0) and coverage is not None and len(covered) / len(allLambdas) <= 1:
            repos[reponame] = {
                'coverage': coverage,
                'lambdaCoverage': len(covered) / len(allLambdas),
            }
    
    x = []
    y = []
    for repo in repos.values():
        x.append(repo["coverage"])
        y.append(repo["lambdaCoverage"])
    x, y = (list(t) for t in zip(
        *sorted(zip(x, y))))
    fig, ax = plt.subplots()

    plt.scatter(x, y,alpha=0.3)
    plt.xlabel('Test Coverage', fontsize=16)
    plt.ylabel('Lambda Coverage', fontsize=16)
    plt.savefig('plots/6-dynamic/dyn-coverageVSSrcLambdaCoverage.png',dpi=500)


def coverageVSTestLambdaCoverage(): ###
    cursor.execute(
        "SELECT repository.name,repository.coverage FROM repository")
    repoCoverage = cursor.fetchall()
    repos = {}
    counter = 0
    for reponame, coverage in repoCoverage:
        print("Getting Lambda Coverage of ",reponame," ",counter,"/",len(repoCoverage))
        counter += 1
        notCovered, covered, allLambdas = getLambdaCoverageOfRepo(reponame)[1]
        if (len(allLambdas) > 0) and coverage is not None and len(covered) / len(allLambdas) <= 1:
            repos[reponame] = {
                'coverage': coverage,
                'lambdaCoverage': len(covered) / len(allLambdas),
            }
    x = []
    y = []

    for repo in repos.values():
        x.append(repo["coverage"])
        y.append(repo["lambdaCoverage"])
    x, y = (list(t) for t in zip(
        *sorted(zip(x, y))))
    fig, ax = plt.subplots()

    plt.scatter(x, y,alpha=0.3)
    plt.xlabel('Test Coverage', fontsize=16)
    plt.ylabel('Lambda Coverage', fontsize=16)
    plt.savefig('plots/6-dynamic/dyn-coverageVSTestLambdaCoverage.png',dpi=500)


def run():
    allTopTypes()
    plt.clf()

    coverageVSSrcLambdaCoverage()
    plt.clf()

    coverageVSTestLambdaCoverage()
    plt.clf()

    executionsAndTypesPFile()
    plt.clf()

    topTypes()
    plt.clf()
