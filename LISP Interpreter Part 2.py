"""
6.101 Lab:
LISP Interpreter Part 2
"""

#!/usr/bin/env python3
import sys

sys.setrecursionlimit(20_000)

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
    new_list = source.split("\n")
    final_list = []
    for line in new_list:
        line = line.split(";")[0]
        for i in line.split():
            number_string = ""
            for j in i:
                if j == "(":
                    if number_string:
                        final_list.append(number_string)
                        number_string = ""
                    final_list.append(str(j))
                elif j == ")":
                    if number_string:
                        final_list.append(number_string)
                        number_string = ""
                    final_list.append(str(j))
                else:
                    number_string = number_string + j
            if ")" not in i:
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
        if token == "(":
            new_list = []
            index += 1
            while index < len(tokens) and tokens[index] != ")":
                item, index = parse_expression(index)
                new_list.append(item)
            if index == len(tokens) and tokens[-1] != ")":
                raise SchemeSyntaxError
            return new_list, index + 1
        elif token == ")":
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
    a class to represent the structure of frames given bindings
    within the frame as well as a parent fra,e. default parent
    is a frame with scheme-builtins as bindings.
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
            raise SchemeNameError(name)

    def get_frame(self, name):
        if name in self.bindings:
            return self
        elif self.parent:
            return self.parent.get_frame(name)
        else:
            raise SchemeNameError(name)


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
            raise SchemeEvaluationError("length doesn't match")
        new_frame = Frame(bindings=None, parent=self.enclosing_frame)
        for i, j in enumerate(args):
            new_frame.set_name_and_value(self.parameters[i], j)
        return evaluate(self.body, new_frame)


class Pair:
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr


######################
# Built-in Functions #
######################


def equal(args):
    for arg in args:
        if arg != args[0]:
            return False
    return True


def greater_than(args):
    for i in range(len(args) - 1):
        if args[i] <= args[i + 1]:
            return False
    return True


def greater_than_or_equal(args):
    for i in range(len(args) - 1):
        if args[i] < args[i + 1]:
            return False
    return True


def less_than(args):
    for i in range(len(args) - 1):
        if args[i] >= args[i + 1]:
            return False
    return True


def less_than_or_equal(args):
    for i in range(len(args) - 1):
        if args[i] > args[i + 1]:
            return False
    return True


def true_or_false(value):
    if value == "#t":
        return True
    else:
        return False


def check_and(args, current_frame):
    for arg in args:
        if evaluate(arg, current_frame) is False:
            return False
    return True


def check_or(args, current_frame):
    for arg in args:
        if evaluate(arg, current_frame) is True:
            return True
    return False


def check_not(args):
    if args == []:
        raise SchemeEvaluationError("check_not 1")
    elif len(args) > 1:
        raise SchemeEvaluationError("check_not 2")
    return not args[0]


def check_car(args):
    if len(args) == 1 and isinstance(args[0], Pair):
        return args[0].car
    else:
        raise SchemeEvaluationError("check_car")


def check_cdr(args):
    if len(args) == 1 and isinstance(args[0], Pair):
        return args[0].cdr
    else:
        raise SchemeEvaluationError("check_cdr")


def check_cons(args):
    if args == []:
        raise SchemeEvaluationError("check_cons1")
    elif len(args) != 2:
        raise SchemeEvaluationError("check_cons2")
    return Pair(args[0], args[1])


def check_list(args):
    if len(args) == 0:
        return ""
    elif args[0] == "list":
        args.remove("list")
    elif len(args) == 1:
        return check_cons([args[0], ""])
    else:
        return check_cons([args[0], check_list(args[1:])])


def is_list(args):
    if len(args) == 1:
        return is_list_helper(args[0])
    raise SchemeEvaluationError("is_list")


def is_list_helper(linked_list):
    if linked_list == "":
        return True
    elif not isinstance(linked_list, Pair):
        return False
    else:
        return is_list_helper(linked_list.cdr)


def list_length(args):
    length = 0
    if len(args) == 1:
        return list_length_helper(args[0], length)
    raise SchemeEvaluationError("list length")


def list_length_helper(linked_list, length):
    if linked_list == "":
        return length
    elif not isinstance(linked_list, Pair):
        raise SchemeEvaluationError("list length helper")
    else:
        return list_length_helper(linked_list.cdr, length + 1)


def list_ref(args):
    """
    function to get value from list given index
    """
    if len(args) != 2:
        raise SchemeEvaluationError("list ref")
    linked_list = args[0]
    index = args[1]
    if not isinstance(index, int):
        raise SchemeEvaluationError("list ref 2")
    elif is_list([linked_list]):
        return list_ref_helper(linked_list, index)
    elif isinstance(linked_list, Pair):
        if index == 0:
            return linked_list.car
    raise SchemeEvaluationError("list ref 3")


def list_ref_helper(linked_list, index):
    if not isinstance(linked_list, Pair):
        raise SchemeEvaluationError("list ref helper")
    elif index == 0:
        return linked_list.car
    else:
        return list_ref_helper(linked_list.cdr, index - 1)


def list_append(args):
    """
    function to append multiple lists to one another
    """
    if args == []:
        return ""

    if len(args) == 1:
        return list_append_helper_2(args[0])

    else:
        head = list_append_helper_2(args[0])
        flattened = head
        if flattened == "":
            return list_append(args[1:])
        while flattened.cdr != "":
            flattened = flattened.cdr
        flattened.cdr = list_append(args[1:])
        return head


def list_append_helper_2(linked_list):
    if linked_list == "":
        return ""
    elif isinstance(linked_list, Pair):
        return Pair(linked_list.car, list_append_helper_2(linked_list.cdr))
    else:
        raise SchemeEvaluationError


def evaluate_file(name, current_frame=None):
    if current_frame is None:
        current_frame = make_initial_frame()
    return evaluate(parse(tokenize(open(name, "r").read())), current_frame)


scheme_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": lambda args: args[0]
    if len(args) == 1
    else (args[0] * scheme_builtins["*"](args[1:])),
    "/": lambda args: args[0]
    if len(args) == 1
    else (args[0] / scheme_builtins["*"](args[1:])),
    "equal?": equal,
    ">": greater_than,
    ">=": greater_than_or_equal,
    "<": less_than,
    "<=": less_than_or_equal,
    "not": check_not,
    "car": check_car,
    "cdr": check_cdr,
    "cons": check_cons,
    "list": check_list,
    "list?": is_list,
    "length": list_length,
    "list-ref": list_ref,
    "append": list_append,
    "begin": lambda args: args[-1],
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
        if tree in ("#t", "#f"):
            return true_or_false(tree)
        return current_frame.get_value(tree)
    elif isinstance(tree, list):
        if tree == []:
            return ""
        elif tree[0] == "define":
            if isinstance(tree[1], list):
                name = tree[1][0]
                parameters = tree[1][1:]
                body = tree[2]
                function_object = Functions(parameters, body, {}, current_frame)
                current_frame.set_name_and_value(name, function_object)
                return function_object
            value = evaluate(tree[2], current_frame)
            current_frame.set_name_and_value(tree[1], value)
            return value
        elif tree[0] == "lambda":
            parameters = tree[1]
            body = tree[2]
            function_object = Functions(parameters, body, {}, current_frame)
            return function_object
        elif tree[0] == "if":
            conditional = evaluate(tree[1], current_frame)
            if conditional is True:
                return evaluate(tree[2], current_frame)
            else:
                return evaluate(tree[3], current_frame)
        else:
            if tree[0] == "and":
                return check_and(tree[1:], current_frame)
            elif tree[0] == "or":
                return check_or(tree[1:], current_frame)
            elif tree[0] == "del":
                if tree[1] in current_frame.bindings:
                    value = current_frame.bindings[tree[1]]
                    current_frame.bindings.pop(tree[1])
                else:
                    raise SchemeNameError
                return value
            elif tree[0] == "let":
                new_frame = Frame(parent=current_frame)
                for expression in tree[1]:
                    new_frame.set_name_and_value(
                        expression[0], evaluate(expression[1], current_frame)
                    )
                return evaluate(tree[2], new_frame)
            elif tree[0] == "set!":
                value = evaluate(tree[2], current_frame)
                wanted_frame = current_frame.get_frame(tree[1])
                wanted_frame.set_name_and_value(tree[1], value)
                return value
            else:
                first = evaluate(tree[0], current_frame)
                if not callable(first):
                    raise SchemeEvaluationError("not callable")
                new_list = []
                for element in tree[1:]:
                    new_list.append(evaluate(element, current_frame))
                return first(new_list)


if __name__ == "__main__":
    # NOTE THERE HAVE BEEN CHANGES TO THE REPL, KEEP THIS CODE BLOCK AS WELL
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    my_frame = make_initial_frame()

    for filename in sys.argv[1:]:
        evaluate_file(filename, my_frame)

    import os

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl

    schemerepl.SchemeREPL(
        sys.modules[__name__], use_frames=True, verbose=True, global_frame=my_frame
    ).cmdloop()
