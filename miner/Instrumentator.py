import ast
import logging
from serializer import SQLiteSerializer
from pathlib import Path
from astor import to_source
from ast import NodeTransformer
from ast import Return
from ast import Call
from ast import Name
from ast import Load
from ast import FunctionDef
from ast import Expr
from ast import Attribute
from ast import Constant
from ast import Import
from ast import alias
from ast import Module
from ast import arg
from ast import arguments
from ast import keyword
from ast import Store
from ast import Assign
from ast import Dict
from ast import For
from ast import BinOp
from ast import Subscript
from ast import BinOp
from ast import Index
from ast import Add
from ast import Global

path_to_tracer = "PATH_TO.../python-lambdas/serializer"
 
lambdaID = 0

def transformRepo(path, reponame):
    files = list(Path(path).rglob("*.[pP][yY]"))
    for file in files:
            transformFile(file,reponame)


def transformFile(path, reponame):
    f = open(path)
    code = f.read()
    f.close()
    f = open(path, "w")
    try:
        logging.info("Starting transformation of " + str(path))
        transformed_code = transformCode(code, path, reponame)
        f.write(transformed_code)
        f.close()
        logging.info("Successfully transformed file " + str(path))
    except Exception as e:
       logging.warning("Could not transform file " + str(path))
       logging.warning(e)


def transformCode(code, filename, reponame):
    try:
        tree = None
        try:
            tree = ast.parse(code)
        except:
            return code
        SQLiteSerializer.serializeFileTransformation(reponame, filename)
        relocator = RelocateLambdas(filename)
        result = relocator.visit(tree)
        functions = relocator.getMethods()
        function_setter = FunctionSetter(functions, relocator.getGlobalVars())
        final_code = function_setter.visit(result)
    except:
        logging.warning("Could not transform file " + str(filename))
        return code
    return to_source(final_code)

# Helper
def getGlobalVariable(name):  # _lambda_0
    return Assign(
        targets=[
            Name(
                id=name + '_locals',
                ctx=Store()
            )
        ],
        value=Dict(keys=[], values=[]), type_comment=None)


# Helper
def getLocalsFunction(var_name):  # _lambda_0
    return FunctionDef(
        name=var_name,
        args=arguments(
            posonlyargs=[],
            args=[arg(arg='locls', annotation=None, type_comment=None)],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[]),
        body=[
            Global(names=[var_name + '_locals']),
            Assign(
                targets=[Name(id=var_name + '_locals', ctx=Store())],
                value=Name(id='locls', ctx=Load()),
                type_comment=None),
            Return(value=Name(id=var_name + '_return', ctx=Load()))
        ],
        decorator_list=[],
        returns=None,
        type_comment=None)


# Helper
def getLambdaMethod(methodname, body, args_node, file, id):  # methodname = _lambda_0
    global lambdaID
    fullbody = []
    fullbody.extend(getTracers(file, args_node, id))
    fullbody.append(getScopeTracer(file, methodname, id))
    fullbody.append(
        Return(
            value=Call(
                func=Name(id='eval', ctx=Load()),
                args=[
                    Constant(value=to_source(body), kind=None),
                    Call(
                        func=Name(id='locals', ctx=Load()),
                        args=[],
                        keywords=[]),
                    Name(id=methodname + '_locals', ctx=Load())],
                keywords=[]
            )
        )
    )
    return FunctionDef(
        name=methodname + '_return',
        args=args_node,
        body=fullbody,
        decorator_list=[],
        returns=None,
        type_comment=None)

# Helper
def getTracers(file, args_node, id):
    args = getArguments(args_node)
    tracers = []
    for arg in args:
        tracers.append(getTracer(file, arg, id))
    return tracers

# Helper
def getScopeTracer(file_name, method_name, id):  # name = _lamba_0
    return Expr(
        value=Call(
            func=Attribute(
                value=Name(id='Tracer', ctx=Load()),
                attr='traceScope', ctx=Load()
            ), args=[
                Constant(value=str(file_name), kind=None),
                Constant(value=str(id), kind=None),
                Name(id=method_name + '_locals', ctx=Load())
            ], keywords=[]
        )
    )


# Helper
def getTracer(file_name, arg_name, id):
    return Expr(
        value=Call(
            func=Attribute(
                value=Name(id='Tracer', ctx=Load()),
                attr='trace', ctx=Load()),
            args=[
                Constant(value=str(file_name), kind=None),
                Constant(value=str(id), kind=None),
                Constant(value=str(arg_name), kind=None),
                Name(id=arg_name, ctx=Load()),
                
            ],
            keywords=[]
        )
    )

# Helper
def getArguments(ao):
    arguments = []
    if hasattr(ao, "posonlyargs"):
        arguments.extend(ao.posonlyargs)
    if hasattr(ao, "args"):
        arguments.extend(ao.args)
    if hasattr(ao, "kwonlyargs"):
        arguments.extend(ao.kwonlyargs)
    if hasattr(ao, "vararg"):
        if ao.vararg != None:
            arguments.append(ao.vararg)
    if hasattr(ao, "kwarg"):
        if ao.kwarg != None:
            arguments.append(ao.kwarg)
    return list(map(lambda x: x.arg, arguments))


class RelocateLambdas(NodeTransformer):

    def __init__(self, filename):
        self.filename = filename
        self.methods = []
        self.globalvars = []
        self.id_counter = 0

    def visit_Lambda(self, node):
        try:
            logging.info("Transforming Lambda: " + to_source(node))
        except:
            logging.info("Transforming Lambda: " + ast.dump(node))
        method_name = "_lambda_" + str(self.id_counter)
        SQLiteSerializer.serializeLambdaTransformation(self.filename, self.id_counter, node.lineno)
        self.methods.append(getLocalsFunction(method_name))
        self.methods.append(getLambdaMethod(
            method_name, node.body, node.args, self.filename, self.id_counter))
        self.globalvars.append(getGlobalVariable(method_name))
        self.id_counter += 1
        return Call(
            func=Name(
                id=method_name, ctx=Load()),
            args=[
                Call(
                    func=Name(id='locals', ctx=Load()),
                    args=[],
                    keywords=[]
                )
            ],
            keywords=[]
        )

    def getMethods(self):
        return self.methods

    def getGlobalVars(self):
        return self.globalvars


class FunctionSetter(NodeTransformer):
    
    def __init__(self, methods, globalvars):
        self.methods = methods
        self.globalvars = globalvars

    def visit_Module(self, node):
        logging.info("Adding " + str(len(self.globalvars)) +
                     " global variables, " + str(len(self.methods)) + " methods")
        node_body = node.body
        node.body = []
        for n in node_body:
            if type(n) is ast.ImportFrom or type(n) is ast.Import:
                node.body.append(n)
                node_body.remove(n)

        node.body.append(
            Import(names=[alias(name='sys', asname=None)])
        )
        node.body.append(Expr(value=Call(func=Attribute(
            value=Attribute(value=Name(id='sys', ctx=Load()),
                            attr='path', ctx=Load()),
            attr='append',
            ctx=Load()),
            args=[Constant(value=path_to_tracer, kind=None)],
            keywords=[]))
        )
        node.body.append(Import(names=[alias(name='Tracer', asname=None)]))
        for globalvar in self.globalvars:
            node.body.append(globalvar)
        for method in self.methods:
            node.body.append(method)
        node.body.extend(node_body)
        return node
