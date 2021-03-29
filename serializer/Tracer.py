import os
import ast
import inspect
import random
from datetime import datetime
current_directory = os.path.dirname(
    os.path.dirname(os.path.realpath(__file__)))
trace_folder = current_directory + "/logs/traces/"
seed = random.randint(0, 9)
trace_filename = trace_folder + datetime.now().strftime("%H-%M-%S") + \
    "--" + str(seed) + '.trace'
trace_file = None
initialised = False


def init():
    global initialised
    global trace_file
    global trace_folder
    if not initialised:
        initialised = True
        if not os.path.isdir(trace_folder):
            os.mkdir(trace_folder)
        trace_file = open(trace_filename, "a")
        trace_file.write("Initialised" + os.linesep)
        trace_file.flush()
    return trace_file


def trace(file, id, arg_name, value):
    writer = init()
    try:
        writer.write(
            "#L ------------------Lambda--------------------" + os.linesep)
        writer.write(">1 File [" + str(file) + "]" + os.linesep)
        writer.write(">2 LambdaID: [" + str(id) + "]" + os.linesep)
        writer.write(">3 Arg_Name: [" + str(arg_name) + "]" + os.linesep)
        writer.write(">4 Type: [" + str(type(value)) + "]" + os.linesep)
    except Exception as e:
        writer.write("!ERR: " + str(e))
    writer.flush()


def traceScope(file, lambda_id, locls):
    writer = init()
    try:
        writer.write(
            "#S ------------------Scope---------------------" + os.linesep)
        writer.write(">1 File [" + str(file) + "]" + os.linesep)
        writer.write(">2 LambdaID [" + str(lambda_id) + "]" + os.linesep)
        writer.write(">3 Locals: " + os.linesep)
        for loc in locls.items():
            writer.write(">4   [" + str(loc[0]) + "] = [" +
                         str(type(loc[1])) + "]" + os.linesep)

    except Exception as e:
        writer.write("!ERR: " + str(e))
    writer.flush()
