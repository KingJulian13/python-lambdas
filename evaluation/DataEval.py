###
### Static data in tables & graphics from chapter 3
### 
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
import plotly
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from matplotlib.pyplot import figure
from matplotlib.dates import drange, num2date
from dateutil.relativedelta import relativedelta
from collections import Counter
from pandas.plotting import table
import peakutils

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


# Commits per month from chapter 3
def commitsPMonth(): 
    font = {'size': 18}
    matplotlib.rc('font', **font)
    cursor.execute("SELECT commits.date FROM commits")
    rows = cursor.fetchall()

    rowStrings = list(map(lambda x: x[0], rows))
    rowDates = list(map(lambda x: datetime.fromisoformat(x), rowStrings))
    rowDatesOnly = list(map(lambda x: str(x.year) + "." +
                            str(x.month).zfill(2), rowDates))
    rowYears = list(map(lambda x: str(x.year), rowDates))
    A = pandas.DataFrame(columns=["Date"], data=rowDatesOnly)  # DataFrame
    data = A.groupby("Date").size()  # Series
    data.xticks = rowYears
    data = data.sort_index()
    plot = data.plot()  # AxesSubplot

    plt.xlabel('Zeit in Monaten', fontsize=16)
    plt.ylabel('Anzahl Commits', fontsize=16)

    plot.grid(True, linestyle='-.')
    fig = plot.get_figure()
    fig.set_size_inches(17, 5)
    fig.subplots_adjust(bottom=0.15, left=0.1, right=0.95)
    fig.savefig("plots/3-data/commitsPMonth.png", dpi=500)


# LOC and Repositories from chapter 3
def locKumulativPRepo(filename="locKumulativPRepo"): 
    cursor.execute("SELECT commits.date,SUM(modification.loc_variation) from repository JOIN commits ON commits.repository_id == repository.id JOIN modification ON modification.commit_id == commits.id GROUP BY commits.date")
    dateLocvar = cursor.fetchall()
    dates = list(map(lambda x:  datetime.fromisoformat(x[0]), dateLocvar))

    cursor.execute("SELECT creation from repository")
    repoDates = cursor.fetchall()
    repoDates = list(
        map(lambda x: datetime.fromisoformat(x[0]).date(), repoDates))

    locVar = list(map(lambda x:  x[1], dateLocvar))

    loc_dict = {}
    for i in range(len(dates)):
        date = dates[i].date()
        count = locVar[i]
        loc_dict[date] = loc_dict.get(date, 0) + count

    dates = num2date(drange(min(dates).date(), max(
        dates).date() + timedelta(1), timedelta(1)))
    locs = numpy.asarray(
        [loc_dict.get(d.date(), 0) for d in dates]).cumsum()

    for i in range(len(locs)):
        loc = locs[i]
        date = dates[i].date()
        locs[i] = loc / sum(1 for i in repoDates if i <= date)

    plt.step(dates, locs, alpha=0.8, label="LOC pro Projekt", linewidth=2)
    plt.grid(True, linestyle='-.')
    plt.legend(title='Legende')
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Codezeilen pro Repository', fontsize=16)
    plt.savefig("plots/3-data/" + filename + ".png", dpi=500)



# Basic table with raw data from static analysis & metadata (graphic not in thesis) 
def basedataTable(): 
    cursor.execute("SELECT SUM(stars), AVG(stars) from repository")
    stars = cursor.fetchall()
    cursor.execute("SELECT SUM(watchers), AVG(watchers) from repository")
    watchers = cursor.fetchall()
    cursor.execute("SELECT SUM(forks), AVG(forks) from repository")
    forks = cursor.fetchall()
    cursor.execute("SELECT SUM(subscribers), AVG(subscribers) from repository")
    subscribers = cursor.fetchall()
    cursor.execute("SELECT SUM(issues), AVG(issues) from repository")
    issues = cursor.fetchall()
    cursor.execute("SELECT COUNT(commits.id),AVG(commits.id) from repository JOIN commits ON commits.repository_id == repository.id JOIN modification ON modification.commit_id == commits.id GROUP BY repository.id")
    commitsPRepo = cursor.fetchall()

    df = pandas.DataFrame(data={
        'Stars': list(stars[0]),
        'Watchers': list(watchers[0]),
        'Forks': list(forks[0]),
        'Subscribers': list(subscribers[0]),
        'Open Issues': list(issues[0])
    }, index=["SUM", "AVG"])

    ax = plt.subplot(frame_on=False)  
    ax.xaxis.set_visible(False) 
    ax.yaxis.set_visible(False) 
    pandas.plotting.table(ax, df) 
    plt.savefig('plots/3-data/basedataTable.png', dpi=300)


# Outliers from chapter 3
def starDistrubution(): 
    cursor.execute(
        "SELECT repository.stars,repository.name from repository WHERE repository.stars IS NOT NULL ORDER BY repository.stars")
    res = cursor.fetchall()
    stars = list(map(lambda x: x[0], res))
    names = list(map(lambda x: x[1], res))
    stars, names = zip(*sorted(zip(stars, names)))

    df = pandas.DataFrame({'Stars': stars, 'Repository': names})

    fig, ax = plt.subplots()
    fig.set_size_inches(7, 5)
    ax = df.plot(drawstyle="steps", grid=True,
                 x='Repository', y='Stars', rot=90)
    plt.fill_between(df["Repository"], df["Stars"], step="pre", alpha=1)
    
    plt.tick_params(
        axis='x',        
        which='both',    
        bottom=False,     
        top=False,         
        labelbottom=False)
    plt.xlabel('Repository', fontsize=16)
    plt.ylabel('Stars', fontsize=16)
    plt.tight_layout()
    plt.savefig('plots/3-data/starDistrubution.png',dpi=500)
    plt.clf()


# Outliers from chapter 3 logarithmic
def starDistrubutionLog():
    cursor.execute(
        "SELECT repository.stars,repository.name from repository WHERE repository.stars IS NOT NULL ORDER BY repository.stars")
    res = cursor.fetchall()
    stars = list(map(lambda x: x[0], res))
    names = list(map(lambda x: x[1], res))
    stars, names = zip(*sorted(zip(stars, names)))

    df = pandas.DataFrame({'Stars': stars, 'Repository': names})

    fig, ax = plt.subplots()
    fig.set_size_inches(7, 5)
    ax = df.plot(drawstyle="steps", grid=True,
                 x='Repository', y='Stars', rot=90, logy=True)
    plt.fill_between(df["Repository"], df["Stars"], step="pre", alpha=1)
    plt.tick_params(
        axis='x',          
        which='both',     
        bottom=False,      
        top=False,         
        labelbottom=False)
    plt.xlabel('Zeit', fontsize=16)
    plt.ylabel('Stars', fontsize=16)
    plt.tight_layout()
    plt.savefig('plots/3-data/starDistrubutionLog.png',dpi=500)
    plt.clf()


# Basic table with raw data from dynamic analysis (graphic not in thesis)
def dynBasedataTable(): 
    cursor.execute("SELECT COUNT(*) FROM transformed_lambda")
    transformed_lambdas = cursor.fetchall()[0]
    cursor.execute("SELECT COUNT(*) FROM transformed_file")
    transformed_files = cursor.fetchall()[0]
    cursor.execute("SELECT COUNT(DISTINCT file_path) FROM transformed_lambda")
    transformed_files_with_lambdas = cursor.fetchall()[0]
    cursor.execute("SELECT COUNT(*) FROM transformed_lambda WHERE file_path LIKE '%test%'")
    transformed_test_lambdas = cursor.fetchall()[0]
    cursor.execute("SELECT COUNT(*) FROM transformed_lambda WHERE file_path NOT LIKE '%test%'")
    transformed_nontest_lambdas = cursor.fetchall()[0]
    cursor.execute("SELECT COUNT(*) FROM executed_lambda_scope")
    executed_lambdas_duplicate = cursor.fetchall()[0]
    cursor.execute("SELECT COUNT(DISTINCT lambda_id) FROM executed_lambda_scope")
    executed_lambdas = cursor.fetchall()[0]
    cursor.execute("SELECT COUNT(transformed_lambda.id) FROM transformed_lambda JOIN executed_lambda_scope ON executed_lambda_scope.lambda_id == transformed_lambda.id WHERE transformed_lambda.file_path LIKE '%test%'")
    executed_test_lambdas_duplicate = cursor.fetchall()[0]
    cursor.execute("SELECT COUNT(DISTINCT executed_lambda_scope.lambda_id) FROM transformed_lambda JOIN executed_lambda_scope ON executed_lambda_scope.lambda_id == transformed_lambda.id WHERE transformed_lambda.file_path LIKE '%test%'")
    executed_test_lambdas = cursor.fetchall()[0]
    cursor.execute("SELECT COUNT(DISTINCT executed_lambda_scope.lambda_id) FROM transformed_lambda JOIN executed_lambda_scope ON executed_lambda_scope.lambda_id == transformed_lambda.id WHERE transformed_lambda.file_path NOT LIKE '%test%'")
    executed_nontest_lambdas = cursor.fetchall()[0]
    cursor.execute("SELECT COUNT(*) FROM executed_lambda_arg")
    executed_lambda_args = cursor.fetchall()[0]
    cursor.execute("SELECT COUNT(*) FROM executed_lambda_scope_var")
    scope_vars = cursor.fetchall()[0]
    cursor.execute("SELECT COUNT(DISTINCT type) FROM executed_lambda_arg")
    different_types = cursor.fetchall()[0]
    df = pandas.DataFrame(data={
        'transformed_lambdas': list(transformed_lambdas),
        'transformed_files': list(transformed_files),
        'transformed_files_with_lambdas': list(transformed_files_with_lambdas),
        'transformed_test_lambdas': list(transformed_test_lambdas),
        'transformed_nontest_lambdas': list(transformed_nontest_lambdas),
        'executed_lambdas': list(executed_lambdas),
        'executed_lambdas_duplicate': list(executed_lambdas_duplicate),
        'executed_test_lambdas': list(executed_test_lambdas),
        'executed_test_lambdas_duplicate': list(executed_test_lambdas_duplicate),
        'executed_nontest_lambdas': list(executed_nontest_lambdas),
        'executed_lambda_args': list(executed_lambda_args),
        'traced_scope_vars': list(scope_vars),
        'different_types': list(different_types)
    }, index=["TOTAL"])
    
    fig, ax = plt.subplots() 
    fig.set_size_inches(17, 5)
    ax.axis('off')
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)  
    pandas.plotting.table(ax, df)  
    
    plt.savefig('plots/3-data/dynBasedataTable.png', dpi=300)


# Subfunction for "repos-vs-locs"
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
    plt.savefig("plots/3-data/" + filename + ".png", dpi=300)


# Subfunction for "repos-vs-locs"
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
    plt.savefig("plots/3-data/" + filename + ".png", dpi=500,pad_inches=0)

def run():
    commitsPMonth()
    plt.clf()

    starDistrubution()
    plt.clf()

    starDistrubutionLog()
    plt.clf()

    dynBasedataTable()
    plt.clf()

    basedataTable()
    plt.clf()

    fig, ax = plt.subplots()
    ax.axvspan(datetime(2001, 6, 13), datetime(2014, 1, 1), alpha=0.2, color='C2')
    ax.axvspan(datetime(2019, 1, 1), datetime.now(), alpha=0.2, color='C3')
    locKumulativPRepo()
    plt.clf()

    fig, ax = plt.subplots()
    ax.axvspan(datetime(2001, 6, 13), datetime(2014, 1, 1), alpha=0.2, color='C2')
    ax.axvspan(datetime(2019, 1, 1), datetime.now(), alpha=0.2, color='C3')
    reposPTime()
    locKumulativ(5000, "repos-vs-locs")
    plt.clf()
