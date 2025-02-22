"""
6.101 Lab:
Symbolic Algebra
"""

import doctest

class Symbol:
    def __repr__(self):
        return f"{self.__class__.__name__}()"

    def __str__(self):
        return self.__repr__()

    def key(self):
        return repr(self)

    def __eq__(self, other):
        return repr(self) == repr(other)

class Var(Symbol):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Var('{self.name}')"

    def __str__(self):
        return self.name

    def key(self):
        return self.name

    def deriv(self, variable):
        if variable == self.name:
            return Num(1)
        else:
            return Num(0)

class Num(Symbol):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Num({self.value})"

    def __str__(self):
        return str(self.value)

    def key(self):
        return self.value

    def deriv(self, variable):
        return Num(0)

class BinOp(Symbol):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def key(self):
        return (self.left, self.right)

    def simplify(self):
        self.left = self.left.simplify() if isinstance(self.left, Symbol) else self.left
        self.right = self.right.simplify() if isinstance(self.right, Symbol) else self.right
        return self.simplify_rule()

class Add(BinOp):
    precedence = 1
    operand = '+'
    wrap_right_at_same_precedence = False

    def compute(self, left_val, right_val):
        return left_val + right_val

    def simplify_rule(self):
        left, right = self.left, self.right
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.value + right.value)
        elif isinstance(left, Num) and left.value == 0:
            return right
        elif isinstance(right, Num) and right.value == 0:
            return left
        else:
            return Add(left, right)

class Sub(BinOp):
    precedence = 1
    operand = '-'
    wrap_right_at_same_precedence = False

    def compute(self, left_val, right_val):
        return left_val - right_val

    def simplify_rule(self):
        left, right = self.left, self.right
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.value - right.value)
        elif isinstance(right, Num) and right.value == 0:
            return left
        else:
            return Sub(left, right)

class Mul(BinOp):
    precedence = 2
    operand = '*'
    wrap_right_at_same_precedence = True

    def compute(self, left_val, right_val):
        return left_val * right_val

    def simplify_rule(self):
        left, right = self.left, self.right
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.value * right.value)
        elif isinstance(left, Num) and left.value == 0:
            return Num(0)
        elif isinstance(right, Num) and right.value == 0:
            return Num(0)
        elif isinstance(left, Num) and left.value == 1:
            return right
        elif isinstance(right, Num) and right.value == 1:
            return left
        else:
            return Mul(left, right)

class Div(BinOp):
    precedence = 2
    operand = '/'
    wrap_right_at_same_precedence = True

    def compute(self, left_val, right_val):
        return left_val / right_val

    def simplify_rule(self):
        left, right = self.left, self.right
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.value / right.value)
        elif isinstance(left, Num) and left.value == 0:
            return Num(0)
        elif isinstance(right, Num) and right.value == 1:
            return left
        else:
            return Div(left, right)

class Symbol:
    def simplify(self):
        return self

class Var(Symbol):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Var('{self.name}')"

    def __str__(self):
        return self.name

    def simplify(self):
        return self

    def deriv(self, variable):
        if variable == self.name:
            return Num(1)
        else:
            return Num(0)

class Num(Symbol):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Num({self.value})"

    def __str__(self):
        return str(self.value)

    def simplify(self):
        return self

    def deriv(self, variable):
        return Num(0)

class BinOp(Symbol):
    def simplify(self):
        self.left = self.left.simplify() if isinstance(self.left, Symbol) else self.left
        self.right = self.right.simplify() if isinstance(self.right, Symbol) else self.right
        return self.simplify_rule()

class Add(BinOp):
    precedence = 1
    operand = '+'
    wrap_right_at_same_precedence = False

    def compute(self, left_val, right_val):
        return left_val + right_val

    def simplify_rule(self):
        left, right = self.left, self.right
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.value + right.value)
        elif isinstance(left, Num) and left.value == 0:
            return right
        elif isinstance(right, Num) and right.value == 0:
            return left
        else:
            return Add(left, right)

class Sub(BinOp):
    precedence = 1
    operand = '-'
    wrap_right_at_same_precedence = False

    def compute(self, left_val, right_val):
        return left_val - right_val

    def simplify_rule(self):
        left, right = self.left, self.right
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.value - right.value)
        elif isinstance(right, Num) and right.value == 0:
            return left
        else:
            return Sub(left, right)

class Mul(BinOp):
    precedence = 2
    operand = '*'
    wrap_right_at_same_precedence = True

    def compute(self, left_val, right_val):
        return left_val * right_val

    def simplify_rule(self):
        left, right = self.left, self.right
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.value * right.value)
        elif isinstance(left, Num) and left.value == 0:
            return Num(0)
        elif isinstance(right, Num) and right.value == 0:
            return Num(0)
        elif isinstance(left, Num) and left.value == 1:
            return right
        elif isinstance(right, Num) and right.value == 1:
            return left
        else:
            return Mul(left, right)

class Div(BinOp):
    precedence = 2
    operand = '/'
    wrap_right_at_same_precedence = True

    def compute(self, left_val, right_val):
        return left_val / right_val

    def simplify_rule(self):
        left, right = self.left, self.right
        if isinstance(left, Num) and isinstance(right, Num):
            return Num(left.value / right.value)
        elif isinstance(left, Num) and left.value == 0:
            return Num(0)
        elif isinstance(right, Num) and right.value == 1:
            return left
        else:
            return Div(left, right)

def expression(s):
    return parse(tokenize(s))

def tokenize(s):
    tokens = []
    s = s.replace("(", " ( ").replace(")", " ) ").split()
    for t in s:
        try:
            tokens.append(float(t))
        except ValueError:
            tokens.append(t)
    return tokens

def parse(tokens):
    def parse_expression(index):
        token = tokens[index]
        if token == '(':
            left, next_index = parse_expression(index + 1)
            op = tokens[next_index]
            right, next_index = parse_expression(next_index + 1)
            return make_op(left, op, right), next_index + 1
        elif isinstance(token, float) or token.isnumeric() or token[0] == '-':
            return Num(float(token)), index + 1
        else:
            return Var(token), index + 1

    def make_op(left, op, right):
        if op == '+':
            return Add(left, right)
        elif op == '-':
            return Sub(left, right)
        elif op == '*':
            return Mul(left, right)
        elif op == '/':
            return Div(left, right)

    return parse_expression(0)[0]

if __name__ == "__main__":
    x = Var('x')
    y = Var('y')
    z = 2 * x - x * y + 3 * y

    print("Expression:")
    print(z)

    print("\nDerivative with respect to x:")
    print(z.deriv('x').simplify())

    print("\nDerivative with respect to y:")
    print(z.deriv('y').simplify())

    print("\nEvaluation:")
    print(z.eval({'x': 3, 'y': 7}))
