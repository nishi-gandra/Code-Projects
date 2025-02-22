"""
6.101 Lab:
LISP Interpreter Part 1
"""

#!/usr/bin/env python3

import sys

sys.setrecursionlimit(20_000)

# NO ADDITIONAL IMPORTS!

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    new_list = source.split('\n')
    final_list = []
    for line in new_list:
        line = line.split(';')[0]
        for i in line.split():
            number_string = ''
            for j in i:
                if j == '(':
                    if number_string:
                        final_list.append(number_string)
                        number_string = ''
                    final_list.append(str(j))
                elif j == ')':
                    if number_string:
                        final_list.append(number_string)
                        number_string = ''
                    final_list.append(str(j))
                else:
                    number_string = number_string + j
            if ')' not in i:
                final_list.append(number_string)
    return final_list


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """

    def parse_expression(index):
        token = tokens[index]
        if token == '(':
            new_list = []
            index += 1
            while index < len(tokens) and tokens[index] != ')':
                item, index = parse_expression(index)
                new_list.append(item)
            return new_list, index + 1
        elif token == ')':
            raise SchemeSyntaxError
        return number_or_symbol(token), index + 1

    parsed_expression, next_index = parse_expression(0)
    if next_index != len(tokens):
        raise SchemeSyntaxError
    return parsed_expression


###################
# Defined Classes #
###################

class Frame:
    """
    hi
    """
    def __init__(self, bindings=None, parent=None):
        if bindings is None:
            self.bindings = {}
        else:
            self.bindings = bindings
        self.parent = parent

    def set_name_and_value(self, name, value):
        self.bindings[name] = value

    def get_value(self, name):
        if name in self.bindings:
            return self.bindings[name]
        elif self.parent:
            return self.parent.get_value(name)
        else:
            raise SchemeNameError


class Functions:
    """
    a class to represent user-defined functions. stores
    the code representing the body of the function (which, for
    now, is restricted to a single expression representing the return value)
    the names of the function's parameters a pointer to the frame in which
    the function was defined (the function's enclosing frame)
    """
    def __init__(self, parameters, body, bindings, enclosing_frame):
        self.parameters = parameters
        self.body = body
        self.bindings = bindings
        self.enclosing_frame = enclosing_frame

    def __call__(self, args):
        if len(args) != len(self.parameters):
            raise SchemeEvaluationError
        new_frame = Frame(bindings=None, parent=self.enclosing_frame)
        for i, j in enumerate(args):
            new_frame.set_name_and_value(self.parameters[i], j)
        return evaluate(self.body, new_frame)


######################
# Built-in Functions #
######################


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": lambda args: args[0] if len(args) == 1 else (args[0] *
                                                      scheme_builtins['*'](args[1:])),
    "/": lambda args: args[0] if len(args) == 1 else (args[0] /
                                                      scheme_builtins['*'](args[1:])),
}


##############
# Evaluation #
##############

def make_initial_frame():
    return Frame(parent=Frame(scheme_builtins))


def evaluate(tree, current_frame=None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if current_frame is None:
        current_frame = make_initial_frame()

    if isinstance(tree, (int, float)):
        return tree
    elif isinstance(tree, str):
        try:
            return current_frame.get_value(tree)
        except SchemeNameError:
            raise SchemeNameError
    elif isinstance(tree, list):
        if tree[0] == 'define':
            if isinstance(tree[1], list):
                name = tree[1][0]
                parameters = tree[1][1:]
                body = tree[2]
                function_object = Functions(parameters,
                                            body, {}, current_frame)
                current_frame.set_name_and_value(name, function_object)
                return function_object
            value = evaluate(tree[2], current_frame)
            current_frame.set_name_and_value(tree[1], value)
            return value
        if tree[0] == 'lambda':
            parameters = tree[1]
            body = tree[2]
            function_object = Functions(parameters, body,
                                        {}, current_frame)
            return function_object
        else:
            first = evaluate(tree[0], current_frame)
            if not callable(first):
                raise SchemeEvaluationError
            new_list = []
            for element in tree[1:]:
                new_list.append(evaluate(element, current_frame))
            return first(new_list)









if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # print(tokenize('(spam(dog))'))
    # print(parse(tokenize('(spam(dog))')))

    # print(evaluate(['define', 'spam', 'x']))


    import os
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl
    schemerepl.SchemeREPL(use_frames=True, verbose=True).cmdloop()
