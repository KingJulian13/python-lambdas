#from miner import Project
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
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from matplotlib.pyplot import figure
from matplotlib.dates import drange, num2date
from dateutil.relativedelta import relativedelta
from collections import Counter

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


# Helper
def getWeekOf(source, dates):

    return [source.get(d.date(), 0) + source.get(d.date() + timedelta(1), 0)
            + source.get(d.date() + timedelta(2), 0)
            + source.get(d.date() + timedelta(3), 0)
            + source.get(d.date() + timedelta(4), 0)
            + source.get(d.date() + timedelta(5), 0)
            + source.get(d.date() + timedelta(6), 0)
            for d in dates]


def totalLambdasByWeek():
    cursor.execute("SELECT commits.date,count(lambda.id),lambda.kind from repository JOIN commits ON commits.repository_id == repository.id JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id GROUP BY commits.date,lambda.kind HAVING lambda.kind == 1 OR lambda.kind == 2")
    dateCountType = cursor.fetchall()

    dates = list(map(lambda x:  datetime.fromisoformat(x[0]), dateCountType))
    counts = list(map(lambda x:  x[1], dateCountType))
    types = list(map(lambda x:  x[2], dateCountType))

    added_dict = {}
    removed_dict = {}
    sum_dict = {}
    for i in range(len(dates)):
        changeType = types[i]
        date = dates[i].date()
        count = counts[i]
        if changeType == 1:
            added_dict[date] = count
            sum_dict[date] = sum_dict.get(date, 0) + count
        else:
            removed_dict[date] = -count
            sum_dict[date] = sum_dict.get(date, 0) - count

    dates = num2date(drange(min(dates).date(), max(
        dates).date() + timedelta(1), timedelta(1)))
    dates = dates[0::7]
    adds = numpy.asarray(getWeekOf(added_dict, dates))
    removes = numpy.asarray(getWeekOf(removed_dict, dates))

    N1 = 20
    adds1 = numpy.convolve(adds, numpy.ones(N1)/N1, mode='valid')
    removes1 = numpy.convolve(removes, numpy.ones(N1)/N1, mode='valid')
    dates1 = dates[int(N1/2)-1:-int(N1/2)]

    plt.figure(figsize=(7, 5))
    fig, ax = plt.subplots()
    plt.fill_between(dates, adds, step="pre", linewidth=1,
                     alpha=0.4, label="Hinzugefügte Lambdas")
    plt.fill_between(dates, removes, step="pre", linewidth=1,
                     alpha=0.4, label="Entfernte Lambdas")
    plt.plot(dates, adds, drawstyle="steps")
    plt.plot(dates, removes, drawstyle="steps")

    plt.plot(dates1, adds1, drawstyle="steps", label="Gemittelt N=" + str(N1))
    plt.fill_between(dates1, adds1, step="pre", linewidth=1, alpha=0.4)
    plt.plot(dates1, removes1, drawstyle="steps",
             label="Gemittelt N=" + str(N1))
    plt.fill_between(dates1, removes1, step="pre", linewidth=1, alpha=0.4)

    plt.yticks([-140,-100,-60,-45,-30,-15,0,15,30,45,60,100,140])
    plt.legend(title='Aktivität')
    plt.grid(True)
    ax.set_ylim([-150,150])
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Anzahl Lambdas', fontsize=16)
    plt.savefig("plots/4-history/totalLambdasByWeek.png", dpi=500, pad_inches=0)



def totalLambdasByWeekSum(): 
    cursor.execute("SELECT commits.date,count(lambda.id),lambda.kind from repository JOIN commits ON commits.repository_id == repository.id JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id GROUP BY commits.date,lambda.kind HAVING lambda.kind == 1 OR lambda.kind == 2")
    dateCountType = cursor.fetchall()

    dates = list(map(lambda x:  datetime.fromisoformat(x[0]), dateCountType))
    counts = list(map(lambda x:  x[1], dateCountType))
    types = list(map(lambda x:  x[2], dateCountType))

    added_dict = {}
    removed_dict = {}
    sum_dict = {}
    for i in range(len(dates)):
        changeType = types[i]
        date = dates[i].date()
        count = counts[i]
        if changeType == 1:
            added_dict[date] = count
            sum_dict[date] = sum_dict.get(date, 0) + count
        else:
            removed_dict[date] = -count
            sum_dict[date] = sum_dict.get(date, 0) - count

    dates = num2date(drange(min(dates).date(), max(
        dates).date() + timedelta(1), timedelta(1)))
    dates = dates[0::7]
    adds = numpy.asarray(getWeekOf(added_dict, dates))
    removes = numpy.asarray(getWeekOf(removed_dict, dates))
    sums = numpy.asarray(getWeekOf(sum_dict, dates))

    N1 = 20
    sums1 = numpy.convolve(sums, numpy.ones(N1)/N1, mode='valid')
    dates1 = dates[int(N1/2)-1:-int(N1/2)]

    plt.figure(figsize=(7, 5))
    fig, ax = plt.subplots()
    plt.plot(dates, sums, drawstyle="steps", label="Lambdas")
    plt.fill_between(dates, sums, step="pre", linewidth=1, alpha=0.4)
    plt.plot(dates1, sums1, drawstyle="steps", label="Gemittelt N=" + str(N1))
    plt.fill_between(dates1, sums1, step="pre", linewidth=1, alpha=0.4)

    plt.yticks([-140,-100,-60,-45,-30,-15,0,15,30,45,60,100,140])
    plt.legend(title='Aktivität')
    plt.grid(True)
    ax.set_ylim([-150,150])
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Anzahl Lambdas', fontsize=16)
    plt.savefig("plots/4-history/totalLambdasByWeekSum.png", dpi=500, pad_inches=0)


def totalLambdasSCATTERBOX(): 
    cursor.execute("SELECT commits.date,count(lambda.id),lambda.kind from repository JOIN commits ON commits.repository_id == repository.id JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id GROUP BY repository.id,lambda.kind HAVING lambda.kind == 1 OR lambda.kind == 2")
    dateCountType = cursor.fetchall()

    dates = list(map(lambda x:  datetime.fromisoformat(x[0]), dateCountType))
    counts = list(map(lambda x:  x[1], dateCountType))
    types = list(map(lambda x:  x[2], dateCountType))

    added_dict = {}
    removed_dict = {}
    sum_dict = {}
    for i in range(len(dates)):
        changeType = types[i]
        date = dates[i].date()
        count = counts[i]
        if changeType == 1:
            added_dict[date] = count
            sum_dict[date] = sum_dict.get(date, 0) + count
        else:
            removed_dict[date] = -count
            sum_dict[date] = sum_dict.get(date, 0) - count

    keys, values = list(sum_dict.keys()), list(sum_dict.values())

    df = pandas.DataFrame(
        {'data': values, 'group': map(lambda x: x.year, keys)})

    group = 'group'
    column = 'data'
    grouped = df.groupby(group)
    names, vals, xs = [], [], []

    for i, (name, subdf) in enumerate(grouped):
        names.append(name)
        vals.append(subdf[column].tolist())
        xs.append(numpy.random.normal(i+1, 0.04, subdf.shape[0]))

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    fig.set_size_inches(14, 5)
    ax.boxplot(vals, labels=names)
    ngroup = len(vals)
    clevels = numpy.linspace(0., 1., ngroup)
    for x, val, clevel in zip(xs, vals, clevels):
        ax.scatter(x, val, c=matplotlib.cm.prism(clevel), alpha=0.4, s=1)

    plt.yscale('symlog')
    plt.axhline(y=0)
    major_ticks = numpy.arange(-1000, 1001, 100)
    minor_ticks = numpy.arange(-1000, 1001, 10)
    ax.set_ylim([-1000,1000])

    ax.grid(which='both')
    ax.set_yticks(major_ticks)
    ax.set_yticks(list(numpy.arange(-1000, 1001, 100)) + [-10,-1,0,1,10])
    ax.set_yticks(minor_ticks, minor=True)
    ax.grid(which='minor', alpha=0.2)
    ax.grid(which='major', alpha=0.5)
    plt.grid(b=True, axis="y")
    plt.xlabel('Zeit in Jahren', fontsize=16)
    plt.ylabel('Lambdas', fontsize=16)

    plt.savefig("plots/4-history/totalLambdasSCATTERBOX.png", dpi=500)


def totalLambdasWithBranchByWeek(): 
    cursor.execute(
        "SELECT commits.date FROM commits ORDER BY date ASC LIMIT 1")
    firstDate = list(map(lambda x: x[0], cursor.fetchall()))[0]
    firstDate = datetime.fromisoformat(firstDate)
    dates = [firstDate.date()]
    cursor.execute("SELECT commits.date,commits.branch,count(lambda.id),lambda.kind from repository JOIN commits ON commits.repository_id == repository.id JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id GROUP BY commits.date,lambda.kind HAVING lambda.kind == 1 OR lambda.kind == 2")
    dateCountType = cursor.fetchall()

    dates = list(map(lambda x:  datetime.fromisoformat(x[0]), dateCountType))
    branches = list(map(lambda x:  x[1], dateCountType))
    counts = list(map(lambda x:  x[2], dateCountType))
    types = list(map(lambda x:  x[3], dateCountType))
    added_dict = {}
    added_master = {}
    added_dev = {}
    added_other = {}
    removed_dict = {}
    removed_master = {}
    removed_dev = {}
    removed_other = {}
    sum_dict = {}
    sum_master = {}
    sum_dev = {}
    sum_other = {}
    for i in range(len(dates)):
        changeType = types[i]
        date = dates[i].date()
        count = counts[i]
        branch = branches[i]
        if changeType == 1:
            if branch == "master" or branch == "main":
                added_master[date] = count
                sum_master[date] = sum_master.get(date, 0) + count
            elif branch == "dev" or branch == "develop":
                added_dev[date] = count
                sum_dev[date] = sum_dev.get(date, 0) + count
            else:
                added_other[date] = count
                sum_other[date] = sum_other.get(date, 0) + count
            added_dict[date] = count
            sum_dict[date] = sum_dict.get(date, 0) + count
        else:
            if branch == "master" or branch == "main":
                removed_master[date] = -count
                sum_master[date] = sum_master.get(date, 0) - count
            elif branch == "dev" or branch == "develop":
                removed_dev[date] = -count
                sum_dev[date] = sum_dev.get(date, 0) - count
            else:
                removed_other[date] = -count
                sum_other[date] = sum_other.get(date, 0) - count
            removed_dict[date] = - count
            sum_dict[date] = sum_dict.get(date, 0) - count

    dates = num2date(drange(min(dates).date(), max(
        dates).date() + timedelta(1), timedelta(1)))
    dates = dates[0::7]

    adds_dev = numpy.asarray(getWeekOf(added_dev, dates))
    adds_master = numpy.asarray(getWeekOf(added_master, dates))
    adds_other = numpy.asarray(getWeekOf(added_other, dates))
    removes_dev = numpy.asarray(getWeekOf(removed_dev, dates))
    removes_master = numpy.asarray(getWeekOf(removed_master, dates))
    removes_other = numpy.asarray(getWeekOf(removed_other, dates))

    plt.figure(figsize=(14, 5))
    plt.step(dates, adds_master, linewidth=1, alpha=0.8,
             label="master", color="C0")
    plt.fill_between(dates, adds_master, step="pre",
                     linewidth=1, alpha=0.3, color="C0")
    plt.step(dates, adds_dev,  linewidth=1,  alpha=0.8,
             label="dev", color="C1")
    plt.fill_between(dates, adds_dev, step="pre",
                     linewidth=1, alpha=0.3, color="C1")
    plt.step(dates, adds_other, linewidth=1, alpha=0.8,
             label="andere", color="C2")
    plt.fill_between(dates, adds_other, step="pre",
                     linewidth=1, alpha=0.3, color="C2")

    plt.step(dates, removes_master, linewidth=1, alpha=0.8, color="C0")
    plt.fill_between(dates, removes_master, step="pre",
                     linewidth=1, alpha=0.3, color="C0")
    plt.step(dates, removes_dev,  linewidth=1, alpha=0.8, color="C1")
    plt.fill_between(dates, removes_dev, step="pre",
                     linewidth=1, alpha=0.3, color="C1")
    plt.step(dates, removes_other,  linewidth=1, alpha=0.8, color="C2")
    plt.fill_between(dates, removes_other, step="pre",
                     linewidth=1, alpha=0.3, color="C2")
    plt.legend(title='Branches')
    plt.autoscale(tight=True)
    plt.grid(True)
    plt.ylim([-100,100])
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Lambdas', fontsize=16)
    plt.savefig("plots/4-history/totalLambdasWithBranchByWeek.png", dpi=500)


def totalLambdasKumulativ(): 
    cursor.execute(
        "SELECT commits.date FROM commits ORDER BY date ASC LIMIT 1")
    firstDate = list(map(lambda x: x[0], cursor.fetchall()))[0]
    firstDate = datetime.fromisoformat(firstDate)
    dates = [firstDate.date()]
    cursor.execute("SELECT commits.date,count(lambda.id),lambda.kind from repository JOIN commits ON commits.repository_id == repository.id JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id GROUP BY commits.date,lambda.kind HAVING lambda.kind == 1 OR lambda.kind == 2")
    dateCountType = cursor.fetchall()

    dates = list(map(lambda x:  datetime.fromisoformat(x[0]), dateCountType))
    counts = list(map(lambda x:  x[1], dateCountType))
    types = list(map(lambda x:  x[2], dateCountType))

    sum_dict = {}
    for i in range(len(dates)):
        changeType = types[i]
        date = dates[i].date()
        count = counts[i]
        if changeType == 1:
            sum_dict[date] = sum_dict.get(date, 0) + count
        else:
            sum_dict[date] = sum_dict.get(date, 0) - count

    dates = num2date(drange(min(dates).date(), max(
        dates).date() + timedelta(1), timedelta(1)))
    sums = numpy.asarray([sum_dict.get(d.date(), 0) for d in dates]).cumsum()
    fig, ax = plt.subplots()
    plt.step(dates, sums, alpha=0.8, linewidth=1, label="Kummulative Lambdas")
    plt.savefig("plots/4-history/totalLambdasKumulativ.png", dpi=500)


def lambdasPRepoBox(): 
    cursor.execute(
        "SELECT commits.date FROM commits ORDER BY date ASC LIMIT 1")
    firstDate = list(map(lambda x: x[0], cursor.fetchall()))[0]
    firstDate = datetime.fromisoformat(firstDate)
    firstDate = datetime(firstDate.year, 1, 1)
    present = datetime.now()
    dates = [firstDate.date()]
    years_plot = {}

    cursor.execute("SELECT repository.id from repository")
    repos = cursor.fetchall()
    repos = list(map(lambda x: x[0], repos))
    repos = dict.fromkeys(repos, 0)

    while firstDate.date() < present.date():
        nextDate = firstDate + relativedelta(months=+12) 
        dates.append(nextDate)
        minorDateString = firstDate.strftime("%Y-%m-%d")
        majorDateString = nextDate.strftime("%Y-%m-%d")
        cursor.execute("SELECT repository.id,COUNT(lambda.id),lambda.kind FROM lambda JOIN modification ON lambda.modification_id == modification.id  JOIN commits ON modification.commit_id == commits.id JOIN repository on commits.repository_id == repository.id WHERE commits.date BETWEEN '" +
                       minorDateString + "' AND '" + majorDateString + "' GROUP by lambda.kind,repository.name")
        change = list(cursor.fetchall())
        for id, value, kind in change:
            if kind == 1:
                repos[id] = repos[id] + value
            else:
                repos[id] = repos[id] - value

        years_plot[str(nextDate.year)] = copy.deepcopy(repos)

        firstDate = nextDate
    labels = list(years_plot.keys())
    year_dicts = years_plot.values()
    result_list = []
    for year in labels:
        l = list(years_plot[year].values())
        l = list(filter(lambda x: x != 0, l))
        result_list.append(l)
    
    fig, ax = plt.subplots()
    result_list = list(filter(lambda x: len(x) > 0, result_list))
    plt.boxplot(result_list)
    plt.grid(True)
    plt.xticks(range(1, len(labels) + 1), labels)
    plt.yscale('log')

    fig.set_size_inches(14, 5)
    plt.xlabel('Zeit in Jahren', fontsize=16)
    plt.ylabel('Lambdas pro Repository', fontsize=16)
    plt.savefig("plots/4-history/lambdasPRepoBox.png", dpi=500)


def locKumulativ(scaleFactor=1, filename="locKumulativ"):
    cursor.execute(
        "SELECT commits.date FROM commits ORDER BY date ASC LIMIT 1")
    firstDate = list(map(lambda x: x[0], cursor.fetchall()))[0]
    firstDate = datetime.fromisoformat(firstDate)
    dates = [firstDate.date()]
    cursor.execute("SELECT commits.date,SUM(modification.loc_variation) from repository JOIN commits ON commits.repository_id == repository.id JOIN modification ON modification.commit_id == commits.id  GROUP BY commits.date")
    dateLocvar = cursor.fetchall()
    dates = list(map(lambda x:  datetime.fromisoformat(x[0]), dateLocvar))
    locVar = list(map(lambda x:  x[1], dateLocvar))

    sum_dict = {}
    for i in range(len(dates)):
        date = dates[i].date()
        count = locVar[i]
        sum_dict[date] = sum_dict.get(date, 0) + count

    dates = num2date(drange(min(dates).date(), max(
        dates).date() + timedelta(1), timedelta(1)))
    sums = numpy.asarray(
        [sum_dict.get(d.date(), 0)/scaleFactor for d in dates]).cumsum()

    plt.step(dates, sums, alpha=1, label="LOC", linewidth=2)
    plt.grid(True)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Lambdas / LOC', fontsize=16)
    plt.legend(title='Legende')
    plt.savefig("plots/4-history/" + filename + ".png", dpi=500,pad_inches=0)


def activeContributersStacked(): 
    cursor.execute("SELECT repository.name,commits.repository_id,count(DISTINCT(commits.author)) from commits JOIN repository ON repository.id == commits.repository_id GROUP BY commits.repository_id")
    allRepoAuthors = cursor.fetchall()
    cursor.execute("SELECT repository.name,commits.repository_id,count(DISTINCT(commits.author)),count(lambda.id) from commits JOIN repository ON repository.id == commits.repository_id JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id GROUP BY commits.repository_id HAVING COUNT(lambda.id) > 0")
    onlyLambdaCommits = cursor.fetchall()
    allRepoNames = list(map(lambda x: x[0], allRepoAuthors))
    resultLabels = []
    resultValues1 = []
    resultValues2 = []
    resultValues3 = []
    totalValues = []

    for name, id, authors, in allRepoAuthors:
        lambdaAuthors = list(filter(lambda x: x[1] == id, onlyLambdaCommits))
        resultLabels.append(name)
        if len(lambdaAuthors) == 0:
            resultValues1.append(0)
            resultValues2.append(0)
            resultValues3.append(0)
            totalValues.append(0)
        if len(lambdaAuthors) == 1:
            cursor.execute("SELECT commits.author,COUNT(lambda.id) from commits JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id WHERE commits.repository_id == " +
                           str(id) + " GROUP BY commits.author HAVING COUNT(lambda.id) > 0")
            authorsWithAmountOfLambdas = cursor.fetchall()
            amountOfLambdaAuthors = lambdaAuthors[0][2]
            amountOfTotalAuthors = authors
            amountLambdaChangesOfRepo = lambdaAuthors[0][3]

            totalValues.append(amountOfLambdaAuthors/amountOfTotalAuthors)

            p10 = 0
            p50 = 0
            p90 = 0
            for author, lambdas in authorsWithAmountOfLambdas:
                if lambdas / amountLambdaChangesOfRepo < 0.25:
                    p10 = p10 + 1
                elif lambdas / amountLambdaChangesOfRepo >= 0.25 and lambdas / amountLambdaChangesOfRepo < 0.75:
                    p50 = p50 + 1
                elif lambdas / amountLambdaChangesOfRepo >= 0.75:
                    p90 = p90 + 1
                else:
                    print("ERR:", lambdas / amountLambdaChangesOfRepo)

            p50 = p50 + p10
            p90 = p90 + p50
            p10 = p10 / amountOfTotalAuthors
            p50 = p50 / amountOfTotalAuthors
            p90 = p90 / amountOfTotalAuthors

            resultValues1.append(p10)
            resultValues2.append(p50)
            resultValues3.append(p90)
        if len(lambdaAuthors) > 1:
            print("Error: This should not be possible")

    totalValues, resultValues3, resultValues2, resultValues1 = (list(t) for t in zip(
        *sorted(zip(totalValues, resultValues3, resultValues2, resultValues1))))

    resultValues1, resultValues2, resultValues3 = zip(*((resultValues1, resultValues2, resultValues3) for resultValues1, resultValues2, resultValues3 in zip(resultValues1, resultValues2, resultValues3) if resultValues1 > 0 or resultValues2 > 0 or resultValues3 > 0))
    df = pandas.DataFrame(dict(
        LOW=resultValues1,
        REGULAR=resultValues2,
        HIGH=resultValues3
    ))

    fig = df.diff(axis=1).fillna(df).astype(
        df.dtypes).plot.bar(stacked=True,width=1.0).get_figure()
    fig.set_size_inches(14, 5)
    fig.tight_layout()
    ax1 = plt.axes()
    x_axis = ax1.axes.get_xaxis()
    x_axis.set_visible(False)
    fig.savefig('plots/4-history/activeContributersStacked.png',dpi=500)


def contexts(): 
    cursor.execute("SELECT commits.date,lambda.kind,lambda.context,count(lambda.id) FROM commits JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id GROUP BY commits.date,lambda.kind,lambda.context")
    dateKindContextAmount = cursor.fetchall()
    dates_dict = list(
        map(lambda x:  datetime.fromisoformat(x[0]), dateKindContextAmount))

    other_dict = {}
    return_dict = {}
    call_dict = {}
    returncall_dict = {}

    for date, kind, context, value in dateKindContextAmount:
        date = datetime.fromisoformat(date).date()
        if kind == 2:
            value = -value
        if context == 1:
            other_dict[date] = other_dict.get(date, 0) + value
        if context == 2:
            return_dict[date] = return_dict.get(date, 0) + value
        if context == 3:
            call_dict[date] = call_dict.get(date, 0) + value
        if context == 4:
            returncall_dict[date] = returncall_dict.get(date, 0) + value

    dates = num2date(drange(min(dates_dict).date(), max(
        dates_dict).date() + timedelta(1), timedelta(1)))
    others = numpy.asarray([other_dict.get(d.date(), 0)
                            for d in dates]).cumsum()
    returns = numpy.asarray([return_dict.get(d.date(), 0)
                             for d in dates]).cumsum()
    calls = numpy.asarray([call_dict.get(d.date(), 0) for d in dates]).cumsum()
    returncalls = numpy.asarray(
        [returncall_dict.get(d.date(), 0) for d in dates]).cumsum()

    fig, ax = plt.subplots()
    plt.step(dates, others, linewidth=2, label='Andere')
    plt.step(dates, returns, linewidth=2, label='Return')
    plt.step(dates, calls, linewidth=2, label='Call')
    plt.step(dates, returncalls,  linewidth=2, label='Return Call')
    plt.grid(True)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Lambdas', fontsize=16)
    plt.legend(title='Kontexte', borderaxespad=0.)
    plt.savefig("plots/5-context/contexts.png", dpi=500)


def contextsRelative(filename="contextsRelative"): 
    cursor.execute("SELECT commits.date,lambda.kind,lambda.context,count(lambda.id) FROM commits JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id GROUP BY commits.date,lambda.kind,lambda.context")
    dateKindContextAmount = cursor.fetchall()

    dates_dict = list(
        map(lambda x:  datetime.fromisoformat(x[0]), dateKindContextAmount))

    other_dict = {}
    return_dict = {}
    call_dict = {}
    returncall_dict = {}

    for date, kind, context, value in dateKindContextAmount:
        date = datetime.fromisoformat(date).date()
        if kind == 2:
            value = -value
        if context == 1:
            other_dict[date] = other_dict.get(date, 0) + value
        if context == 2:
            return_dict[date] = return_dict.get(date, 0) + value
        if context == 3:
            call_dict[date] = call_dict.get(date, 0) + value
        if context == 4:
            returncall_dict[date] = returncall_dict.get(date, 0) + value

    dates = num2date(drange(min(dates_dict).date(), max(
        dates_dict).date() + timedelta(1), timedelta(1)))

    others = numpy.asarray([other_dict.get(d.date(), 0)
                            for d in dates]).cumsum()
    returns = numpy.asarray([return_dict.get(d.date(), 0)
                             for d in dates]).cumsum()
    calls = numpy.asarray([call_dict.get(d.date(), 0) for d in dates]).cumsum()
    returncalls = numpy.asarray(
        [returncall_dict.get(d.date(), 0) for d in dates]).cumsum()

    lambdas = returncalls + others + returns + calls

    others = [i / j for i, j in zip(others, lambdas)] 
    returns = [i / j for i, j in zip(returns, lambdas)] 
    calls = [i / j for i, j in zip(calls, lambdas)] 
    returncalls = [i / j for i, j in zip(returncalls, lambdas)] 

    fig, ax = plt.subplots()
    plt.step(dates, others, linewidth=2, label='Andere')
    plt.step(dates, returns, linewidth=2, label='Return')
    plt.step(dates, calls, linewidth=2, label='Call')
    plt.step(dates, returncalls, linewidth=2, label='Return Call')
    plt.grid(True)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Anteil Lambdas', fontsize=16)
    plt.legend(title='Kontexte', borderaxespad=0.)
    plt.savefig("plots/5-context/" + filename + ".png", dpi=500)


def arguments(): 
    cursor.execute("SELECT commits.date,lambda.kind,lambda.arguments FROM commits JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id")
    dateKindArguents = cursor.fetchall()
    dates_dict = list(
        map(lambda x:  datetime.fromisoformat(x[0]), dateKindArguents))

    all_dicts = {}
    for date, kind, arguments in dateKindArguents:
        date = datetime.fromisoformat(date).date()
        value = len(list(filter(None, arguments.split(','))))
        add = 1
        if kind == 2:
            add = -add
        d = all_dicts.get(value, {})
        d[date] = d.get(date, 0) + add
        all_dicts[value] = d

    dates = num2date(drange(min(dates_dict).date(), max(
        dates_dict).date() + timedelta(1), timedelta(1)))

    all_result_dicts = {}
    for i, k in all_dicts.items():
        d = all_result_dicts.get(i, {})
        d[i] = numpy.asarray([k.get(dat.date(), 0) for dat in dates]).cumsum()
        all_result_dicts[i] = d

    plt.clf()
    skipped = []
    fig, ax = plt.subplots()
    for i, k in all_result_dicts.items():
        if max(k[i]) > 10:
            plt.step(dates, k[i], linewidth=2, label=i)
        else:
            skipped.append([i])
    plt.grid(True)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Lambdas', fontsize=16)
    plt.legend(title='Anzahl Argumente', borderaxespad=0.)
    plt.savefig("plots/5-context/arguments.png", dpi=500)

def argumentsRelative(): 
    cursor.execute("SELECT commits.date,lambda.kind,lambda.arguments FROM commits JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id")
    dateKindArguents = cursor.fetchall()
    dates_dict = list(
        map(lambda x:  datetime.fromisoformat(x[0]), dateKindArguents))

    all_dicts = {}
    for date, kind, arguments in dateKindArguents:
        date = datetime.fromisoformat(date).date()
        value = len(list(filter(None, arguments.split(','))))
        add = 1
        if kind == 2:
            add = -add
        d = all_dicts.get(value, {})
        d[date] = d.get(date, 0) + add
        all_dicts[value] = d

    dates = num2date(drange(min(dates_dict).date(), max(
        dates_dict).date() + timedelta(1), timedelta(1)))

    all_result_dicts = {}
    for i, k in all_dicts.items():
        all_result_dicts[i] = numpy.asarray([k.get(dat.date(), 0) for dat in dates]).cumsum()

    cumsum = [0]*len(list(all_result_dicts.values())[0])
    for x in all_result_dicts.values():
        cumsum = cumsum + x

    for k,v in all_result_dicts.items():
        all_result_dicts[k] = [i / j for i, j in zip(v, cumsum)]

    plt.clf()
    skipped = []
    fig, ax = plt.subplots()
    for i, k in all_result_dicts.items():
        if max(k) > 0:
            plt.step(dates, k, linewidth=2, label=i)
        else:
            skipped.append([i])
    plt.grid(True)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Antail Lambdas', fontsize=16)
    plt.legend(title='Anzahl Argumente', borderaxespad=0.)
    plt.savefig("plots/5-context/argumentsRelative.png", dpi=500)


def expressions(filename="expressions"): 
    cursor.execute("SELECT commits.date,lambda.kind,lambda.expressions FROM commits JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id")

    dateKindArguents = cursor.fetchall()
    dates_dict = list(
        map(lambda x:  datetime.fromisoformat(x[0]), dateKindArguents))

    all_dicts = {}

    for date, kind, expressions in dateKindArguents:
        date = datetime.fromisoformat(date).date()
        add = 1
        if kind == 2:
            add = -add
        d = all_dicts.get(expressions, {})
        d[date] = d.get(date, 0) + add
        all_dicts[expressions] = d

    dates = num2date(drange(min(dates_dict).date(), max(
        dates_dict).date() + timedelta(1), timedelta(1)))

    all_result_dicts = {}
    for i, k in all_dicts.items():
        d = all_result_dicts.get(i, {})
        d[i] = numpy.asarray([k.get(dat.date(), 0) for dat in dates]).cumsum()
        all_result_dicts[i] = d

    skipped = []
    fig, ax = plt.subplots()
    for i, k in all_result_dicts.items():
        if max(k[i]) > 100:
            plt.step(dates, k[i], alpha=0.8, linewidth=2, label=i)
        else:
            skipped.append([i])
    plt.legend(title='Expressions:', bbox_to_anchor=(
        0.05, 0.95), loc=2, borderaxespad=0.)
    plt.grid(True)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Lambdas', fontsize=16)
    plt.savefig("plots/5-context/" + filename + ".png", dpi=500)


def expressionsRelative(filename="expressionsRelative"): 
    cursor.execute("SELECT commits.date,lambda.kind,lambda.expressions FROM commits JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id")
    dateKindArguents = cursor.fetchall()
    dates_dict = list(
        map(lambda x:  datetime.fromisoformat(x[0]), dateKindArguents))

    all_dicts = {}
    for date, kind, expressions in dateKindArguents:
        date = datetime.fromisoformat(date).date()
        add = 1
        if kind == 2:
            add = -add
        d = all_dicts.get(expressions, {})
        d[date] = d.get(date, 0) + add
        all_dicts[expressions] = d

    dates = num2date(drange(min(dates_dict).date(), max(
        dates_dict).date() + timedelta(1), timedelta(1)))

    all_result_dicts = {}
    for i, k in all_dicts.items():
        d = numpy.asarray([k.get(dat.date(), 0) for dat in dates]).cumsum()
        all_result_dicts[i] = d

    skipped = []
    filteredResults = {}
    for i, k in all_result_dicts.items():
        if max(k) > 100:
            filteredResults[i] = k
        else:
            skipped.append(i)
    lambdaAmounts = []
    for i in range(len(list(filteredResults.values())[0])):
        lambdas = 0
        for expressions, amounts in filteredResults.items():
            amount = amounts[i]
            lambdas = lambdas + amount
        lambdaAmounts.append(lambdas)

    for expressions, amounts in filteredResults.items():
        filteredResults[expressions] = [
            x / total for x, total in zip(amounts, lambdaAmounts)]

    fig, ax = plt.subplots()
    for i, k in filteredResults.items():
        plt.step(dates, k, alpha=0.8, linewidth=2, label=i)

    plt.legend(title='Durchnittliche\n Expressions', bbox_to_anchor=(
        0.05, 0.95), loc=2, borderaxespad=0.)
    plt.grid(True)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Anteil Lambdas', fontsize=16)
    plt.savefig("plots/5-context/" + filename + ".png", dpi=500)


def expressionsScatter(filename="expressionsScatter"):
    cursor.execute("SELECT commits.date,lambda.kind,lambda.expressions,COUNT(commits.id) FROM commits JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id GROUP BY commits.date,lambda.kind,lambda.expressions")
    dateKindArguents = cursor.fetchall()

    all_dicts = {}

    x = []
    y = []
    s = []
    c = []
    for date, kind, expressions,count in dateKindArguents:
        date = datetime.fromisoformat(date)
        c.append("C" + str(expressions))
        if kind == 2:
            expressions = -expressions
        x.append(date)
        y.append(expressions)
        f = (date, expressions)
        s.append(count)
        
    fig, ax = plt.subplots()

    plt.scatter(x, y, s=s, c=c, alpha=0.4, edgecolors="none")
    ax.set_ylim([-50,50])
    ax.axhline(0,0,1,c="black")
    plt.grid(True)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Expressions', fontsize=16)
    plt.savefig("plots/5-context/" + filename + ".png", dpi=500)


def avgExpressions(filename="avgExpressions",detail = True): 
    cursor.execute("SELECT commits.date,lambda.kind,lambda.expressions FROM commits JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id")

    dateKindArguents = cursor.fetchall()
    dates_dict = list(
        map(lambda x:  datetime.fromisoformat(x[0]), dateKindArguents))
    all_dicts = {}

    for date, kind, expressions in dateKindArguents:
        date = datetime.fromisoformat(date).date()
        add = 1
        if kind == 2:
            add = -add
        d = all_dicts.get(expressions, {})
        d[date] = d.get(date, 0) + add
        all_dicts[expressions] = d

    dates = num2date(drange(min(dates_dict).date(), max(
        dates_dict).date() + timedelta(1), timedelta(1)))

    all_result_dicts = {}
    for i, k in all_dicts.items():
        d = all_result_dicts.get(i)
        d = numpy.asarray([k.get(dat.date(), 0) for dat in dates]).cumsum()
        all_result_dicts[i] = d

    results = []
    for i in range(len(list(all_result_dicts.values())[0])):
        values = 0
        lambdas = 0
        for expressions, amounts in all_result_dicts.items():
            amount = amounts[i]
            values = values + (expressions * amount)
            lambdas = lambdas + amount
        results.append(values/lambdas)

    alpha = 1
    if detail: 
        alpha = 0.5
        N = 100
        results1 = numpy.convolve(results, numpy.ones(N)/N, mode='valid')

        dates1 = dates[int(N/2)-1:-int(N/2)]
        plt.step(dates1, results1,  linewidth=2,
                label="Expressions Gemittelt N=" + str(N))

    
    plt.step(dates, results, alpha=alpha,linewidth=2, label="Durchschnitt")
    plt.grid(True)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Durchschnitt', fontsize=16)
    plt.legend(title='Durchnittliche Expressions', bbox_to_anchor=(
        0.05, 0.95), loc=2, borderaxespad=0.)
    plt.savefig("plots/5-context/" + filename + ".png", dpi=500)


def complexity(filename="complexity", factor = 1): 
    cursor.execute(
        "SELECT commits.date, modification.complexity FROM commits JOIN modification ON modification.commit_id == commits.id")
    dateComplexity = cursor.fetchall()
    dates = list(map(lambda x:  datetime.fromisoformat(x[0]), dateComplexity))
    avgComplexity = list(map(lambda x:  x[1], dateComplexity))
    sum_dict = {}

    for i in range(len(dates)):
        date = dates[i].date()
        count = avgComplexity[i]
        arr = sum_dict.get(date, [])
        arr.append(count)
        sum_dict[date] = arr
    for k, v in sum_dict.items():
        sum_dict[k] = sum(v) / len(v)

    dates = num2date(drange(min(dates).date(), max(
        dates).date() + timedelta(1), timedelta(1)))
    sums = numpy.asarray(
        [sum_dict.get(d.date(), 0) for d in dates])  


    if factor != 1:
        sums = list(map(lambda x: x*factor,sums))

    N1 = 100
    sums1 = numpy.convolve(sums, numpy.ones(N1)/N1, mode='valid')
    N2 = 10
    sums2 = numpy.convolve(sums, numpy.ones(N2)/N2, mode='valid')

    dates1 = dates[int(N1/2)-1:-int(N1/2)]
    dates2 = dates[int(N2/2)-1:-int(N2/2)]
    
    plt.step(dates2, sums2, alpha=0.5,
             label="Durchschnittliche Komplexität", linewidth=0.5)
    plt.step(dates1, sums1, 
             label="Komplexität gemittelt N=" + str(N1))
    plt.legend(title='Legende')
    plt.savefig("plots/5-context/" + str(filename) + ".png", dpi=500)


def lambdasByLoc(scaleFactor=1, filename="lambdasByLoc"): 
    cursor.execute("SELECT commits.date,SUM(modification.loc_variation) from repository JOIN commits ON commits.repository_id == repository.id JOIN modification ON modification.commit_id == commits.id  GROUP BY commits.date")
    dateLocvar = cursor.fetchall()
    cursor.execute(
        "SELECT creation FROM repository ORDER BY creation ASC LIMIT 1")
    firstDate = list(map(lambda x: x[0], cursor.fetchall()))[0]
    dates = list(map(lambda x:  datetime.fromisoformat(x[0]), dateLocvar))
    
    locVar = list(map(lambda x:  x[1], dateLocvar))

    loc_dict = {}
    for i in range(len(dates)):
        date = dates[i].date()
        count = locVar[i]
        loc_dict[date] = loc_dict.get(date, 0) + count

    # LAMBDAS KUMuLATIV
    cursor.execute("SELECT commits.date,count(lambda.id),lambda.kind from repository JOIN commits ON commits.repository_id == repository.id JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id GROUP BY commits.date,lambda.kind HAVING lambda.kind == 1 OR lambda.kind == 2")
    dateCountType = cursor.fetchall()

    dates = list(map(lambda x:  datetime.fromisoformat(x[0]), dateCountType))
    counts = list(map(lambda x:  x[1], dateCountType))
    types = list(map(lambda x:  x[2], dateCountType))

    lambda_dict = {}
    for i in range(len(dates)):
        changeType = types[i]
        date = dates[i].date()
        count = counts[i]
        if changeType == 1:
            lambda_dict[date] = lambda_dict.get(date, 0) + count
        else:
            lambda_dict[date] = lambda_dict.get(date, 0) - count

    dates = num2date(drange(min(dates).date(), max(
        dates).date() + timedelta(1), timedelta(1)))
    lambdas = numpy.asarray([lambda_dict.get(d.date(), 0)
                             for d in dates]).cumsum()
    # END OF LAMBDAS KUMULATIV

    locs = numpy.asarray(
        [loc_dict.get(d.date(), 0)/scaleFactor for d in dates]).cumsum()

    result = []
    for la, loc in zip(lambdas, locs):
        result.append(la/(loc/1000))

    plt.figure(figsize=(7, 5))
    fig, ax = plt.subplots()
    plt.grid(True)
    dates.insert(0,datetime.fromisoformat(firstDate))
    result.insert(0,0)
    plt.step(dates, result, alpha=0.8, label="Lambdas pro LOC",where="post")
    plt.legend(title='Legende', bbox_to_anchor=(
        0.05, 0.95), loc=2, borderaxespad=0.)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Anteil Lambdas / Durchschnitt', fontsize=16)
    plt.savefig("plots/4-history" + filename + ".png", dpi=500)


def avgLambdasByRepo(scaleFactor=1, filename="avgLambdasByRepo"): 
    cursor.execute("SELECT repository.creation from repository")
    dateCreation = cursor.fetchall()

    dates = list(map(lambda x:  datetime.fromisoformat(x[0]), dateCreation))

    loc_dict = {}
    for i in range(len(dates)):
        date = dates[i].date()
        loc_dict[date] = loc_dict.get(date, 0) + 1

    # LAMBDAS KUMULATIV
    cursor.execute("SELECT commits.date,count(lambda.id),lambda.kind from repository JOIN commits ON commits.repository_id == repository.id JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id GROUP BY commits.date,lambda.kind HAVING lambda.kind == 1 OR lambda.kind == 2")
    dateCountType = cursor.fetchall()

    dates = list(map(lambda x:  datetime.fromisoformat(x[0]), dateCountType))
    counts = list(map(lambda x:  x[1], dateCountType))
    types = list(map(lambda x:  x[2], dateCountType))

    lambda_dict = {}
    for i in range(len(dates)):
        changeType = types[i]
        date = dates[i].date()
        count = counts[i]
        if changeType == 1:
            lambda_dict[date] = lambda_dict.get(date, 0) + count
        else:
            lambda_dict[date] = lambda_dict.get(date, 0) - count

    dates = num2date(drange(min(dates).date(), max(
        dates).date() + timedelta(1), timedelta(1)))
    lambdas = numpy.asarray([lambda_dict.get(d.date(), 0)
                             for d in dates]).cumsum()
    # END OF LAMBDAS KUMULATIV

    locs = numpy.asarray(
        [loc_dict.get(d.date(), 0)/scaleFactor for d in dates]).cumsum()

    result = []
    for la, repos in zip(lambdas, locs):
        result.append(la/repos)
    plt.figure(figsize=(7, 5))
    plt.step(dates, result,
             label="Lambda pro Repository")
    plt.legend(title='Relativ', bbox_to_anchor=(
        0.05, 0.95), loc=2)
    plt.grid(True)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Lambdas', fontsize=16)
    plt.savefig("plots/4-history/" + filename + ".png", dpi=500)

def reposPTime(filename="reposPTime"):
    cursor.execute("SELECT commits.date from commits")
    commitDates = cursor.fetchall()
    commitDates = list(
        map(lambda x:  datetime.fromisoformat(x[0]), commitDates))
    cursor.execute("SELECT repository.creation from repository")
    repoDates = cursor.fetchall()
    repoDates = list(
        map(lambda x:  datetime.fromisoformat(x[0]).date(), repoDates))

    dates = num2date(drange(min(commitDates).date(), max(
        commitDates).date() + timedelta(1), timedelta(1)))

    repo_dict = {}
    for i in range(len(dates)):
        date = dates[i].date()

        repo_dict[date] = len(list(filter(lambda x: x < date, repoDates)))

    repos = numpy.asarray([repo_dict.get(d.date(), 0)
                           for d in dates])


    plt.step(dates, repos, label="Anzahl Repositories")
    plt.legend(title='Anzahl Repositories', bbox_to_anchor=(
        0.05, 0.95), loc=2, borderaxespad=0.)
    plt.savefig("plots/" + filename + ".png", dpi=300)


def lambdasAndReposOverTime(filename="lambdasAndReposOverTime"): 
    cursor.execute("SELECT commits.date from commits")
    commitDates = cursor.fetchall()
    commitDates = list(
        map(lambda x:  datetime.fromisoformat(x[0]), commitDates))
    cursor.execute("SELECT repository.creation from repository")
    repoDates = cursor.fetchall()
    repoDates = list(
        map(lambda x:  datetime.fromisoformat(x[0]).date(), repoDates))

    dates = num2date(drange(min(commitDates).date(), max(
        commitDates).date() + timedelta(1), timedelta(1)))

    repo_dict = {}
    for i in range(len(dates)):
        date = dates[i].date()

        repo_dict[date] = len(list(filter(lambda x: x < date, repoDates)))

    repos = numpy.asarray([repo_dict.get(d.date(), 0)
                           for d in dates])

    plt.figure(figsize=(7, 5))
    plt.step(dates, repos, label="Gesamt", linewidth=2)

    cursor.execute("SELECT repository.name, MIN(commits.date) from repository JOIN commits ON commits.repository_id == repository.id JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id GROUP BY repository.name")
    nameDates = cursor.fetchall()
    list_of_dates = list(
        map(lambda x: datetime.fromisoformat(x[1]), nameDates))
    date_dict = dict((d, len(list(g)))
                     for d, g in itertools.groupby(list_of_dates, lambda k: k.date()))
    dates = num2date(drange(min(list_of_dates).date(), max(
        list_of_dates).date() + timedelta(1), timedelta(1)))
    counts = numpy.asarray([date_dict.get(d.date(), 0)
                            for d in dates]).cumsum()
    plt.step(dates, counts, label="Mit Lambdas", linewidth=2)
    plt.legend(title='Repositories')
    plt.grid(True)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Repositories', fontsize=16)
    plt.savefig("plots/4-history/" + filename,dpi=500)


def lambdasAndReposOverTimeRelative(filename="lambdasAndReposOverTimeRelative"): 
    cursor.execute("SELECT commits.date from commits")
    commitDates = cursor.fetchall()
    commitDates = list(
        map(lambda x:  datetime.fromisoformat(x[0]), commitDates))
    cursor.execute("SELECT repository.creation from repository")
    repoDates = cursor.fetchall()
    repoDates = list(
        map(lambda x:  datetime.fromisoformat(x[0]).date(), repoDates))

    dates = num2date(drange(min(commitDates).date(), max(
        commitDates).date() + timedelta(1), timedelta(1)))

    repo_dict = {}
    for i in range(len(dates)):
        date = dates[i].date()

        repo_dict[date] = len(list(filter(lambda x: x < date, repoDates)))

    repos = numpy.asarray([repo_dict.get(d.date(), 0)
                           for d in dates])

    cursor.execute("SELECT repository.name, MIN(commits.date) from repository JOIN commits ON commits.repository_id == repository.id JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id GROUP BY repository.name")
    nameDates = cursor.fetchall()
    list_of_dates = list(
        map(lambda x: datetime.fromisoformat(x[1]), nameDates))
    date_dict = dict((d, len(list(g)))
                     for d, g in itertools.groupby(list_of_dates, lambda k: k.date()))
    dates = num2date(drange(min(list_of_dates).date(), max(
        list_of_dates).date() + timedelta(1), timedelta(1)))
    counts = numpy.asarray([date_dict.get(d.date(), 0)
                            for d in dates]).cumsum()

    result = []
    repos = repos[::-1]
    counts = counts[::-1]
    for total,lamb in zip(repos,counts):
        result.append(lamb/total)
    result = result[::-1]
    plt.figure(figsize=(7, 5))
    fig,ax = plt.subplots()
    plt.step(dates, result, label="Relativ", linewidth=2)
    ax.axhline(0.38,0,1,c="C3")
    plt.ylim((0,1))
    plt.legend(title='Repositories')
    plt.grid(True)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Repository Anteil', fontsize=16)
    plt.savefig("plots/4-history/" + filename, dpi=500)


def lambdasPAuthorByActivity(filename="lambdasPAuthorByActivity"): 
    cursor.execute("SELECT commits.author from commits GROUP BY commits.author ORDER BY COUNT(commits.id)")
    authors = cursor.fetchall()
    x = []
    y = []
    s = []
    c = []

    cursor.execute("SELECT commits.author, COUNT(commits.id) from commits GROUP BY commits.author ORDER BY COUNT(commits.id)")
    ordered = cursor.fetchall()
    cursor.execute(
        "SELECT creation FROM repository ORDER BY creation ASC LIMIT 1")
    firstDate = list(map(lambda x: x[0], cursor.fetchall()))[0]
    for author,count in ordered:
        x.append(datetime.fromisoformat(firstDate))
        y.append(author)
        s.append(count)
        c.append('#ffffff')

    cursor.execute("SELECT commits.author, date(date), COUNT(commits.id) from commits GROUP BY commits.author, date(date) ORDER BY COUNT(commits.id)")
    allCommits = cursor.fetchall()
    for author,date,count in allCommits:
        x.append(datetime.fromisoformat(date))
        y.append(author)
        s.append(count)
        c.append('#bbbbff')
        

    authors = list(map(lambda x: x[0], authors))
    authorChanges = {}
    counter = 0
    for author in authors:
        if counter % 500 == 0:
            print("Iterating Authors: ", counter,"/",len(authors))
        counter += 1
        
        cursor.execute("SELECT commits.date, COUNT(lambda.id), lambda.kind from commits JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id WHERE commits.author = '" + author.replace("'",'"') + "' GROUP BY commits.date, lambda.kind")
        dateCountType = cursor.fetchall()
        result = []
        for date,count,typ in dateCountType:
            date = datetime.fromisoformat(date)
            
            if typ == 2:
                count = -count
            if count < -100 or count > 100:
                print("High changes: ", count ," by ", author,". ")
            result.append((date,count))
        authorChanges[author] = result

    authorChanges = {k: v for k, v in sorted(authorChanges.items(), key=lambda item: len(item[1]))}

    for author, changes in authorChanges.items():
       
        for change in changes:
            x.append(change[0])
            y.append(author)
            s.append(abs(change[1]))
            c.append('red' if change[1] < 0 else 'green')
    fig,ax = plt.subplots(figsize=(14, 5))
    plt.scatter(x, y, s=s, c=c, alpha=0.2, edgecolors="none")  
    ax.set_yticklabels([])
    ax.xaxis.grid()
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Autoren', fontsize=16)
    plt.savefig("plots/4-history/" + filename,dpi=800)


def lambdasPAuthorByTime(filename="lambdasPAuthorByTime"): 
    cursor.execute("SELECT DISTINCT commits.author from commits")
    authors = cursor.fetchall()
    x = []
    y = []
    s = []
    c = []

    cursor.execute("SELECT commits.author, date(date), COUNT(commits.id) from commits GROUP BY commits.author, date(date) ORDER BY date")
    allCommits = cursor.fetchall()
    for author,date,count in allCommits:
        x.append(datetime.fromisoformat(date))
        y.append(author)
        s.append(count)
        c.append('#bbbbff')
        

    authors = list(map(lambda x: x[0], authors))
    authorChanges = {}
    counter = 0
    for author in authors:
        if counter % 500 == 0:
            print("Iterating Authors: ", counter,"/",len(authors))
        counter += 1
        
        cursor.execute("SELECT commits.date, COUNT(lambda.id), lambda.kind from commits JOIN modification ON modification.commit_id == commits.id JOIN lambda ON lambda.modification_id == modification.id WHERE commits.author = '" + author.replace("'",'"') + "' GROUP BY commits.date, lambda.kind")
        dateCountType = cursor.fetchall()
        result = []
        for date,count,typ in dateCountType:
            date = datetime.fromisoformat(date)
            
            if typ == 2:
                count = -count
            if count < -100 or count > 100:
                print("High changes: ", count ," by ", author,". ")
            result.append((date,count))
        authorChanges[author] = result

    authorChanges = {k: v for k, v in sorted(authorChanges.items(), key=lambda item: len(item[1]))}

    for author, changes in authorChanges.items():
       
        for change in changes:
            x.append(change[0])
            y.append(author)
            s.append(abs(change[1]))
            c.append('red' if change[1] < 0 else 'green')
    fig,ax = plt.subplots(figsize=(14, 5))
    plt.scatter(x, y, s=s, c=c, alpha=0.2, edgecolors="none")  
    ax.set_yticklabels([])
    ax.xaxis.grid()
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Autoren', fontsize=16)
    plt.savefig("plots/4-history/" + filename,dpi=800)

def run():
    # Plots for RQ 1
    activeContributersStacked()
    plt.clf()

    avgLambdasByRepo()
    plt.clf()

    lambdasAndReposOverTime()
    plt.clf()

    lambdasAndReposOverTimeRelative()
    plt.clf()

    lambdasByLoc()
    plt.clf()

    lambdasPAuthorByActivity()
    plt.clf()

    lambdasPAuthorByTime()
    plt.clf()

    lambdasPRepoBox()
    plt.clf()

    totalLambdasByWeek()
    plt.clf()

    totalLambdasByWeekSum()
    plt.clf()

    totalLambdasSCATTERBOX()
    plt.clf()

    totalLambdasWithBranchByWeek()
    plt.clf()

    totalLambdasKumulativ()
    locKumulativ(1000, "comb-totalLambKum-LOCKum")
    plt.clf()


    # Plots for RQ 2
    arguments()
    plt.clf()

    argumentsRelative()
    plt.clf()

    avgExpressions()
    plt.clf()

    avgExpressions(detail=False)
    complexity("complexityExpressions",0.1)
    plt.clf

    lambdasByLoc()
    complexity("complexityLambdaByLoc",0.01)

    contexts()
    plt.clf()

    contextsRelative()
    plt.clf()

    expressions()
    plt.clf()

    expressionsRelative()
    plt.clf()

    expressionsScatter()
    plt.clf()