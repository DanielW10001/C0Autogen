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

__author__ = "Daniel (danielw10001@gmail.com)"
__docformat__ = 'reStructuredText'

# TODO (Daniel): Before 2019-10-01
#     - Implemente Abstract Method

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
        if identifier in INVOKETRACE:
            # Loop Invoke: ExprCAB <Identifier> -> ExprCQ "Identifier"
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

    # @abstractmethod
    def get_possibility_count(self) -> int:
        """Get possibility count of this expression"""
        pass

    # @abstractmethod
    def get_random_instance(self) -> str:
        """Get random instance of this expression"""
        pass

    def __str__(self) -> str:
        """Get String representation of this expression"""
        repr_str = f'{{{self.operator} -> [\n'
        for child in self.child_list:
            # Recursive
            repr_str += str(child) + ',\n'
        repr_str += ']\n'
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
    program_grammar = compile_grammar_file(DOCDIR + r'/grammar.txt')
    print(program_grammar.get_grammar_tree())


if __name__ == '__main__':
    test()
