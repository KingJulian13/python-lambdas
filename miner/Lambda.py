import ast
import logging
from colorama import Fore, Back, Style

expr = [ast.BoolOp,
        ast.NamedExpr,
        ast.BinOp,
        ast.UnaryOp,
        ast.Lambda,
        ast.IfExp,
        ast.Dict,
        ast.Set,
        ast.ListComp,
        ast.SetComp,
        ast.DictComp,
        ast.GeneratorExp,
        ast.Await,
        ast.Yield,
        ast.YieldFrom,
        ast.Compare,
        ast.Call,
        ast.FormattedValue,
        ast.JoinedStr,
        ast.Constant,
        ast.Attribute,
        ast.Subscript,
        ast.Starred,
        ast.Name,
        ast.List,
        ast.Tuple,
        ast.Slice]

def getLambdas(tree, code):
    all_nodes = dict()
    all_lambdas = []
    return_nodes = getReturnNodes(tree)
    call_nodes = getCallNodes(tree)
    return_call_nodes = []
    for node in return_nodes:
        return_call_nodes.extend(getCallNodes(node))

    for lambda_node in getLambdaNodes(tree):
        d = {lambda_node: "unknown"}
        all_nodes.update(d)

    for return_node in return_nodes:
        for return_lambda_node in getLambdaNodes(return_node):
            all_nodes.update({return_lambda_node: "return"})

    for call_node in call_nodes:
        for call_lambda_node in getLambdaNodes(call_node):
            all_nodes.update({call_lambda_node: "call"})

    for return_call_node in return_call_nodes:
        for return_call_lambda_node in getLambdaNodes(return_call_node):
            all_nodes.update({return_call_lambda_node: "return, call"})

    for pair in all_nodes.items():
        try:
            all_lambdas.append(Lambda(code, pair[0], pair[1]))
        except:
            logging.warning("Could not create Lambda for " + pair)
            logging.debug(code)
    return all_lambdas


def getReturnNodes(tree):
    return_analyzer = ReturnAnalyzer()
    return_analyzer.visit(tree)
    return return_analyzer.report()


def getCallNodes(tree):
    call_analyzer = CallAnalyzer()
    call_analyzer.visit(tree)
    return call_analyzer.report()


def getLambdaNodes(tree):
    lambda_analyzer = LambdaAnalyzer()
    lambda_analyzer.visit(tree)
    return lambda_analyzer.report()


class Lambda():
    def __init__(self, code, lamb, context = None): 
        if context is not None: 
            self.lamb = lamb
            self.context = context
            childs = ast.walk(lamb.body)
            num_expr = 0
            for child in childs:
                if (type(child) in expr):
                    num_expr += 1
            self.expressions = num_expr 
            self.linecontent = ast.get_source_segment(code,lamb)
        else:
            self.id = code[0]
            self.arguments = code[3]
            self.expressions = code[4]
            self.line = code[5]
            self.context = code[6]
            self.linecontent = code[7]

    def getNode(self):
        return self.lamb

    def getLineContent(self):
        return self.linecontent

    def getTupel(self):
        return (self.getLine(), self.getLineContent())

    def getLine(self):
        if hasattr(self, 'line'):
            return self.line
        return self.lamb.lineno

    def getArguments(self):
        if hasattr(self, 'arguments'):
            return self.arguments
        if hasattr(self.lamb, "args"):
            ao = self.lamb.args
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
        return []

    def getBody(self):
        return self.lamb.body

    def getContext(self):
        return self.context

    def getValues(self,parent_id,kind,pre_lambda = None):
        context_id = 1
        if self.context == "return":
            context_id = 2
        if self.context == "call":
            context_id = 3
        if self.context == "return, call":
            context_id = 4
            
        if pre_lambda is not None:
            parent_id = pre_lambda

        s = "("
        s += str(parent_id) + ","
        s += str(kind) + ",'"
        s += str(",".join(self.getArguments())) + "','"
        s += str(self.expressions) + "','"
        s += str(self.getLine()) + "','"
        s += str(context_id) + "','"
        s += self.linecontent.replace("'",'"') + "')"
        return s


    def __str__(self):
        string = f"Lambda: Line {Fore.GREEN}{self.getLine()}{Fore.WHITE}: Args={Fore.RED}{self.getArguments()}{Fore.WHITE} Context={self.getContext()}\n"
        string = string + \
            f"    {Fore.YELLOW}{self.getLineContent()}{Fore.WHITE}"
        return string


class LambdaAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.lambdas = []

    def visit_Lambda(self, node):
        self.lambdas.append(node)

    def report(self):
        return self.lambdas


class ReturnAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.returns = []

    def visit_Return(self, node):
        self.returns.append(node)

    def report(self):
        return self.returns


class CallAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.calls = []

    def visit_Call(self, node):
        self.calls.append(node)

    def report(self):
        return self.calls
