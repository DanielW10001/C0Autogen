# -*- coding: utf-8 -*-

"""Reduced C0 Grammar Tree Analyser and Code Generator

Grammar: metagrammar.txt  # BNF Grammar
Target Text: grammar.txt  # Reduced C0 Grammar
Generate Code: Reduced C0 Code
"""

from typing import List
from abc import ABC, abstractmethod
from collections import deque
import codecs
import sys
import random
import re

__author__ = "Daniel (danielw10001@gmail.com)"
__docformat__ = 'reStructuredText'

GRAMMARTEXT: List[List[str]] = None
""":var GRAMMARTEXT: Grammar str list list

[
    [
        nonterminate_symbol_str,
        expression_str
    ],
    ...
]
"""
GRAMMAR = {}
""":var GRAMMAR: Grammar Dictionary

{
    Identifier: Expression,
    ...
    Identifier: Expression
}
"""
MAX_LOOP_INVOKE_NUMBER: int = 3
"""Max loop invoke number"""
INVOKETRACE: List[str] = []
"""Invoke Tace of Grammar Tree Construction

List of identifier str
"""
PRJDIR: str = r'.'
SRCDIR: str = PRJDIR
OUTDIR: str = PRJDIR
DOCDIR: str = PRJDIR + r'/doc'


class Expr(ABC):
    """Abstract Base Class of Expression"""

    @classmethod
    @abstractmethod
    def generate(cls, exp_q: deque):
        """Construct Expression instance with expression str queue

        :param exp_q: Expression str Queue
        """
        pass

    @classmethod
    def generate_with_identifier(cls, identifier: str):
        """Construct Expression instance with expression identifier

        :param identifier: Expression Identifier
        """
        global GRAMMARTEXT, GRAMMAR, INVOKETRACE
        if INVOKETRACE.count(identifier) > MAX_LOOP_INVOKE_NUMBER:
            # Loop Invoke Exceed: ExprCAB <Identifier> -> ExprCQ "Identifier"
            return cls.generate_with_expr_str("\"" + identifier + "\"")
        else:
            if identifier in GRAMMAR:
                # Reuse constructed grammar item
                return GRAMMAR[identifier]
            else:
                # Log Trace
                INVOKETRACE.append(identifier)
                for grammar_str in GRAMMARTEXT:
                    if '<' + identifier + '>' == grammar_str[0]:
                        # Construct Item
                        expr = cls.generate_with_expr_str(grammar_str[1])
                if len(INVOKETRACE) != len(set(INVOKETRACE)):
                    # Nested Invoked
                    pass
                else:
                    # Not Nested
                    # Add item to GRAMMAR
                    GRAMMAR[identifier] = expr
                # Unlog Trace
                INVOKETRACE.pop()
                return expr

    @classmethod
    def generate_with_expr_str(cls, expr_str: str):
        """Construct Expression instance with expression str

        :param expr_str: Expression str
        """
        return ExprA.generate(deque(expr_str))

    @abstractmethod
    def get_possibility_count(self) -> int:
        """Get possibility count of this expression"""
        pass

    @abstractmethod
    def get_random_instance(self) -> str:
        """Get random instance str of this expression"""
        pass

    def __str__(self) -> str:
        """Get String representation of this expression"""
        repr_str = f'{{{self.operator} -> [\n'
        for child in self.child_list:
            # Recursive
            repr_str += str(child) + ',\n'
        repr_str = repr_str[:-2]
        repr_str += '\n]}'
        return repr_str

    def get_grammar_tree(self) -> str:
        """Get grammar tree recursively"""
        tmp = ExprCAB.__str__
        # Recursivelize: Unset Unrecursive method
        del ExprCAB.__str__
        # Get recursive str
        grammar_tree = self.__str__()
        # Unrecursivelize: Set Unrecursive method
        ExprCAB.__str__ = tmp
        return grammar_tree


class ExprA(Expr):
    """ExpressionA"""

    def __init__(self):
        """Construct ExpressionA instance """
        self.operator = '|'
        self.child_list = []

    @classmethod
    def generate(cls, exp_q: deque):
        """Construct ExpressionA instance with expression str queue

        :param exp_q: Expression str Queue
        """
        exprA = cls()
        exprA.child_list.append(ExprB.generate(exp_q))
        while len(exp_q) > 0 and exp_q[0] == '|':
            exp_q.popleft()
            exprA.child_list.append(ExprB.generate(exp_q))
        return exprA

    def get_possibility_count(self) -> int:
        """Get instance possibility count"""
        possibility_count = 0
        for child_expr in self.child_list:
            # Add Principle
            possibility_count += child_expr.get_possibility_count()
        return possibility_count

    def get_random_instance(self) -> str:
        """Get random instance str"""
        return random.choice(self.child_list).get_random_instance()


class ExprB(Expr):
    """ExpressionB"""
    def __init__(self):
        """Construct ExpressionB instance"""
        self.operator = '+'
        self.child_list = []

    @classmethod
    def generate(cls, exp_q: deque):
        """Construct ExpressionB instance with expression str queue

        :param exp_q: Expression str Queue
        """
        exprB = cls()
        exprB.child_list.append(ExprC.generate(exp_q))
        while len(exp_q) > 0 and\
            (
                exp_q[0] == '[' or
                exp_q[0] == '{' or
                exp_q[0] == '(' or
                exp_q[0] == '<' or
                exp_q[0] == '\"' or
                exp_q[0] == '\''
        ):
            exprB.child_list.append(ExprC.generate(exp_q))
        return exprB

    def get_possibility_count(self) -> int:
        """Get instance possibility count"""
        possibility_count = 1
        for child_expr in self.child_list:
            # Multiply Principle
            possibility_count *= child_expr.get_possibility_count()
        return possibility_count

    def get_random_instance(self) -> str:
        """Get random instance str"""
        instance_str = ''
        for child_expr in self.child_list:
            instance_str += child_expr.get_random_instance()
        return instance_str


class ExprC(Expr):
    """ExpressionC"""

    def __init__(self, operator: str):
        """Construct ExpressionC instance with operator str"""
        self.operator = operator
        self.child_list = []

    @classmethod
    def generate(cls, exp_q: deque):
        """Construct ExpressionC instance with expression str queue

        :param: exp_q: Expresion str Queue
        """
        if len(exp_q) > 0 and exp_q[0] == '[':
            return ExprCSB.generate(exp_q)
        elif len(exp_q) > 0 and exp_q[0] == '{':
            return ExprCCB.generate(exp_q)
        elif len(exp_q) > 0 and exp_q[0] == '(':
            return ExprCRB.generate(exp_q)
        elif len(exp_q) > 0 and exp_q[0] == '<':
            return ExprCAB.generate(exp_q)
        elif len(exp_q) > 0 and (exp_q[0] == '\"' or exp_q[0] == '\''):
            return ExprCQ.generate(exp_q)
        else:
            raise SyntaxError(f"Unknow Token: {exp_q[0]}")


class ExprCSB(ExprC):
    """ExpressionC with Square Bracket"""

    @classmethod
    def generate(cls, exp_q: deque):
        """Construct ExpressionC Square Bracket instance with expression str
        queue

        :param exp_q: Expression str Queue
        """
        if len(exp_q) > 0 and exp_q[0] == '[':
            exp_q.popleft()
            # Construct with '[]' operator
            exprCSB = cls(operator='[]')
            exprCSB.child_list.append(ExprA.generate(exp_q))
            if len(exp_q) > 0 and exp_q[0] == ']':
                exp_q.popleft()
                return exprCSB
            else:
                raise SyntaxError(f"Unknow Token: {exp_q[0]}")
        else:
            raise SyntaxError(f"Unknow Token: {exp_q[0]}")

    def get_possibility_count(self) -> int:
        """Get instance possibility count"""
        # Empty or SupExpression
        return 1 + self.child_list[0].get_possibility_count()

    def get_random_instance(self) -> str:
        """Get random instance str"""
        return random.choice([self.child_list[0].get_random_instance(), ''])


class ExprCCB(ExprC):
    """ExpressionC with Curly Bracket"""

    @classmethod
    def generate(cls, exp_q: deque):
        """Construct ExpressionC Curly Bracket instance with expression str
        queue

        :param exp_q: Expression str Queue
        """
        if len(exp_q) > 0 and exp_q[0] == '{':
            exp_q.popleft()
            # Construct with '{}' operator
            exprCCB = cls(operator='{}')
            exprCCB.child_list.append(ExprA.generate(exp_q))
            if len(exp_q) > 0 and exp_q[0] == '}':
                exp_q.popleft()
                return exprCCB
            else:
                raise SyntaxError(f"Unknow Token: {exp_q[0]}")
        else:
            raise SyntaxError(f"Unknow Token: {exp_q[0]}")

    def get_possibility_count(self) -> int:
        """Get instance possibility count"""
        supexpr_possibility_count = self.child_list[0].get_possibility_count()
        # Only consider {0, 2}
        # Empty or SupExpr or SupExpr SupExpr
        return 1 + supexpr_possibility_count + supexpr_possibility_count ** 2

    def get_random_instance(self) -> str:
        """Get random instance str"""
        return random.choice([
            lambda expr: '',  # Empty
            lambda expr: expr.get_random_instance(),  # SupExpr
            lambda expr: expr.get_random_instance() +  # SupExpr SupExpr
            expr.get_random_instance()
        ])(self.child_list[0])


class ExprCRB(ExprC):
    """ExpressionC with Round Bracket"""

    @classmethod
    def generate(cls, exp_q: deque):
        """Construct ExpressionC Round Bracket instance with expression str
        queue

        :param exp_q: Expression str Queue
        """
        if len(exp_q) > 0 and exp_q[0] == '(':
            exp_q.popleft()
            # Construct with '()' operator
            exprCRB = cls(operator='()')
            exprCRB.child_list.append(ExprA.generate(exp_q))
            if len(exp_q) > 0 and exp_q[0] == ')':
                exp_q.popleft()
                return exprCRB
            else:
                raise SyntaxError(f"Unknow Token: {exp_q[0]}")
        else:
            raise SyntaxError(f"Unknow Token: {exp_q[0]}")

    def get_possibility_count(self) -> int:
        """Get instance possibility count"""
        return self.child_list[0].get_possibility_count()

    def get_random_instance(self) -> str:
        """Get random instance str"""
        return self.child_list[0].get_random_instance()


class ExprCAB(ExprC):
    """ExpressionC with Angle Bracket"""

    @classmethod
    def generate(cls, exp_q: deque):
        """Construct ExpresionC Angle Bracket instance with expression str
        queue

        :param exp_q: Expression str Queue
        """
        if len(exp_q) > 0 and exp_q[0] == '<':
            exp_q.popleft()
            # Construct with '<>' operator
            exprCAB = cls(operator='<>')
            # Get identiier
            identifier_str = ''
            while len(exp_q) > 0 and exp_q[0] != '>':
                if exp_q[0] == '\\':  # Trans meanning
                    exp_q.popleft()
                    if re.fullmatch(r'\w', exp_q[0]):
                        # Control Escape: \a, \b, \c, ...
                        identifier_str += eval('\'\\' + exp_q.popleft() + '\'')
                    else:
                        # Literal Escape: \\, \<, \>, \', \", ...
                        identifier_str += exp_q.popleft()
                else:
                    # exp_q[0] != '>' and exp_q[0] != '\\'
                    identifier_str += exp_q.popleft()
            if len(exp_q) > 0 and exp_q[0] == '>':
                # Bracket match
                exp_q.popleft()
                exprCAB.identifier_str = identifier_str
                # Construct recursively
                # Note that Loop Recurse will be blocked in
                #     Expr.generate_with_identifier
                exprCAB.child_list.append(
                    Expr.generate_with_identifier(identifier_str))
                return exprCAB
            else:
                raise SyntaxError(f"Unknow Token: {exp_q[0]}")
        else:
            raise SyntaxError(f"Unknow Token: {exp_q[0]}")

    def __str__(self):
        """Override Expr.__str__ with Nonrecursive one"""
        return '<' + self.identifier_str + '>'

    def get_possibility_count(self) -> int:
        """Get instance possibility count"""
        return self.child_list[0].get_possibility_count()

    def get_random_instance(self) -> str:
        """Get random instance str"""
        return self.child_list[0].get_random_instance()


class ExprCQ(ExprC):
    """ExpressionC with Quotation"""

    @classmethod
    def generate(cls, exp_q: deque):
        """Construct Expression with Quotation instance with expression str
        queue

        :param exp_q: Expression str Queue
        """
        if len(exp_q) > 0 and (exp_q[0] == '\"' or exp_q[0] == '\''):
            operator = exp_q.popleft()
            # Construct with '\"\"' operator
            exprCQ = cls(operator=operator*2)
            # Get Content
            content = ''
            while len(exp_q) > 0 and exp_q[0] != operator:
                if exp_q[0] == '\\':  # Trans meanning
                    exp_q.popleft()
                    if re.fullmatch(r'\w', exp_q[0]):
                        # Control Escape: \a, \b, \c, ...
                        content += eval('\'\\' + exp_q.popleft() + '\'')
                    else:
                        # Literal Escape: \\, \<, \>, \', \", ...
                        content += exp_q.popleft()
                else:
                    # exp_q[0] != '\'' and exp_q[0] != '\"'\
                    #     and exp_q[0] != '\\'
                    content += exp_q.popleft()
            if len(exp_q) > 0 and exp_q[0] == operator:
                # Bracket Match
                exp_q.popleft()
                exprCQ.child_list.append(content)
                return exprCQ
            else:
                raise SyntaxError(f"Unknow Token: {exp_q[0]}")
        else:
            raise SyntaxError(f"Unknow Token: {exp_q[0]}")

    def get_possibility_count(self) -> int:
        """Get possibility count"""
        return 1

    def get_random_instance(self) -> str:
        """Get random instance str"""
        return self.child_list[0]


class SyntaxError(Exception):
    """Syntax Error"""
    pass


def compile_grammar_file(grammar_file_dir: str) -> Expr:
    """Read grammar file and get 程序 expression

    :param grammar_file_dir: Grammar File Dir

    :return: 程序 expression
    """
    global GRAMMARTEXT
    # Open grammar file
    with codecs.open(grammar_file_dir, r'r', encoding='utf-8')\
            as grammar_file:
        # Read Grammar, delete comment and split identifier and expression
        GRAMMARTEXT = [grammar.strip().split('//')[0].split('::=')
                       for grammar in grammar_file]
    return Expr.generate_with_identifier('程序')


def test():
    # Redirect stdio
    sys.stdin = codecs.open(
        filename=SRCDIR + r'/in.txt', mode='r', encoding='utf-8')
    sys.stdout = codecs.open(
        filename=SRCDIR + r'/out.txt', mode='w', encoding='utf-8')
    sys.stderr = codecs.open(
        filename=SRCDIR + r'/err.txt', mode='w', encoding='utf-8')

    global DOCDIR
    # Read Reduced C0 Grammar
    program_grammar = compile_grammar_file(DOCDIR + r'/autogen_grammar.txt')
    # Usage Here
    # Example:
    # print(program_grammar)
    # print(program_grammar.get_grammar_tree())
    # print(program_grammar.get_possibility_count())
    # print(program_grammar.get_random_instance())


if __name__ == '__main__':
    test()
