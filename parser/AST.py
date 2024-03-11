from dataclasses import dataclass
import parser_edsl as pe
from lexer import lexer
from lexer import Domaintag
from lexer.errors import *

stack_do = []

@dataclass
class Node:

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        raise NotImplementedError()


class Statement(Node):

    @staticmethod
    def parse(tuples: list):
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()

        current_token = tokens[0]
        if current_token.tag != Domaintag.DomainTag.Identifier:
            raise ValueError("Ожидается идентификатор вначале оператора")

        index = lex.token_idx
        try:
            if current_token.attrib == "read":
                return ReadStatement.parse(tuples)
            elif current_token.attrib == "print":
                return PrintStatement.parse(tuples)
            elif current_token.attrib == "format":
                return FormatStatement.parse(tuples)
            elif current_token.attrib == "goto":
                return GotoStatement.parse(tuples)
            elif current_token.attrib == "continue":
                return ContinueStatement.parse(tuples)
            elif current_token.attrib == "if":
                return IfStatement.parse(tuples)
            elif current_token.attrib == "do":
                return DoStatement.parse(tuples)
            elif current_token.attrib == "dimension":
                return DimensionStatement.parse(tuples)
            else:
                return AssignmentStatement.parse(tuples, lex)

        except Exception as ex:
            try:
                lex.analyze_string(tuples[0][1], with_kw=False)

                lex.token_idx = index
                return AssignmentStatement.parse(tuples, lex)
            except:
                raise ex

    def check(self, labels):
        pass


@dataclass
class Identifier(Node):
    name: str

    def check(self, labels):
        if len(self.name) > 6:
            raise IdentifierNameLengthError(None, self.name)


@dataclass
class Number(Node):
    value: float | int

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        tok = lex.next_token()
        value = 1
        if tok.tag == Domaintag.DomainTag.Subtraction_operator or tok.tag == Domaintag.DomainTag.Addition_operator:
            value = -1 if tok.tag == Domaintag.DomainTag.Subtraction_operator else 1
            tok = lex.next_token()
        if tok.tag == Domaintag.DomainTag.Integer or tok.tag == Domaintag.DomainTag.Multiplier:
            value *= int(tok.attrib)
        elif tok.tag == Domaintag.DomainTag.Real:
            value *= float(tok.attrib)
        else:
            raise RuntimeError()
        return Number(value)

    def check(self, labels):
        pass


@dataclass
class Label(Node):
    number: Number

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        result = Number.parse(lex)
        return Label(result)

    def check(self, labels):
        if self.number.value not in labels:
            raise LabelInexistantError(None, self.number.value)


class Expression(Node):
    def __init__(self, expressions):
        self.expressions = expressions

    def check(self, labels):
        pass


@dataclass
class ArithmeticExpression(Node):
    left: Expression
    operator: str
    right: Expression

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        term = Term.parse(lex)
        current_token = lex.current_token()
        result = None
        while (current_token.tag == Domaintag.DomainTag.Addition_operator or
                current_token.tag == Domaintag.DomainTag.Subtraction_operator):
            op = lex.next_token()
            rhs = Term.parse(lex)
            result = ArithmeticExpression(result if result else term, op.attrib, rhs)
            current_token = lex.current_token()
        return result if result else term
    def check(self, labels):
        self.left.check(labels)
        self.right.check(labels)


@dataclass
class IdentifierList(Node):
    identifiers: list[Identifier]

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        identifiers = [ArithmeticExpression.parse(lex)]
        current_token = lex.current_token()
        while current_token.tag == Domaintag.DomainTag.Comma:
            current_token = lex.next_token()
            identifiers.append(ArithmeticExpression.parse(lex))
            current_token = lex.current_token()
        return IdentifierList(identifiers)

    def check(self, labels):
        for ident in self.identifiers:
            ident.check(labels)


@dataclass
class ExpressionList(Node):
    expressions: list[ArithmeticExpression]

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        expressions = [ArithmeticExpression.parse(lex)]
        current_token = lex.current_token()
        while current_token.tag == Domaintag.DomainTag.Comma:
            current_token = lex.next_token()
            expressions.append(ArithmeticExpression.parse(lex))
            current_token = lex.current_token()
        return ExpressionList(expressions)

    def check(self, labels):
        for expr in self.expressions:
            expr.check(labels)


@dataclass
class StatementList(Node):
    statements: list[Statement]

    @staticmethod
    def parse(tuples: list):
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()

        statements = []

        while tokens[0].attrib != 'end':
            statements.append(Statement.parse(tuples))
            if len(tuples) == 0:
                raise ValueError("Отсутствует END")
            lex.analyze_string(tuples[0][1])
            tokens = lex.get_tokens()

        if not statements:
            raise ValueError("Программа не содержит ни одного оператора")

        return StatementList(statements)

    def check(self, labels):
        for stmt in self.statements:
            stmt.check(labels)


@dataclass
class Program(Node):
    identifier: Identifier
    statement_list: StatementList

    @staticmethod
    def parse(tuples: list):
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()

        if len(tokens) != 2:
            raise ValueError("Неверное количество токенов для определения программы")

        kw_program = tokens[0]
        if not (kw_program.tag == Domaintag.DomainTag.Identifier and kw_program.attrib.lower() == "program"):
            raise ValueError(f"Ожидается ключевое слово 'PROGRAM', получено '{kw_program.attrib}'")

        identifier = tokens[1]
        if identifier.tag != Domaintag.DomainTag.Identifier:
            raise ValueError("Ожидается идентификатор после 'PROGRAM'")

        identifier = Identifier(identifier.attrib)
        tuples.pop(0)
        statements = StatementList.parse(tuples)

        return Program(identifier, statements)

    def check(self, labels: list):
        self.identifier.check(labels)
        self.statement_list.check(labels)


@dataclass
class AssignmentStatement(Node):
    identifier: Identifier
    expression: ArithmeticExpression
    index: ExpressionList | None

    @staticmethod
    def parse(tuples: list, lex: lexer.LexicalAnalyzer):

        identifier = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None))
        ident = Identifier(identifier.attrib)
        tok = lex.next_token()
        if tok.tag == Domaintag.DomainTag.Assign:
            expression = ArithmeticExpression.parse(lex)
            tuples.pop(0)
            return AssignmentStatement(ident, expression, None)
        elif tok.tag == Domaintag.DomainTag.Lbracket:
            expr_list = ExpressionList.parse(lex)
            ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None))
            eq_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Assign, None))
            expr = ArithmeticExpression.parse(lex)
            tuples.pop(0)
            return AssignmentStatement(ident, expr, expr_list)
        else:
            raise RuntimeError(f"{tok.coords}: expected token with tag - Assign | Lbracket, got - {tok.tag}")

    def check(self, labels):
        self.identifier.check(labels)


@dataclass
class ReadStatement(Node):
    format_identifier: Label
    identifiers: IdentifierList

    @staticmethod
    def parse(tuples: list):
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()
        read_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, "read"))
        label = Label.parse(lex)
        comma_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Comma, None))
        identifiers = IdentifierList.parse(lex)
        tuples.pop(0)
        return ReadStatement(label, identifiers)

    def check(self, labels):
        self.format_identifier.check(labels)
        self.identifiers.check(labels)


@dataclass
class PrintStatement(Node):
    format_identifier: Label
    identifiers: ExpressionList

    @staticmethod
    def parse(tuples: list):
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()
        print_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, "print"))
        label = Label.parse(lex)
        comma_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Comma, None))
        identifiers = ExpressionList.parse(lex)
        tuples.pop(0)
        return PrintStatement(label, identifiers)

    def check(self, labels):
        self.format_identifier.check(labels)
        self.format_identifier.check(labels)


@dataclass
class FormatItem(Node):
    kind: str
    details: tuple[int, str | int]

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        format_tok = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Format_specifier, None))
        format_attr = format_tok.attrib
        kind, details = None, None
        if "h" in format_attr:
            kind = 'h'
            hstring = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.H_string, None))
            details = (int(format_attr[:-1]), hstring.attrib)
        elif "x" in format_attr:
            kind = 'x'
            details = (int(format_attr[:-1]), None)
        elif "f" in format_attr:
            kind = 'f'
            format_attr = format_attr[1:]
            splitted = format_attr.split('.')
            details = (int(splitted[0]), int(splitted[1]))
        elif "e" in format_attr:
            kind = 'e'
            format_attr = format_attr[1:]
            splitted = format_attr.split('.')
            details = (int(splitted[0]), int(splitted[1]))
        elif "i" in format_attr:
            kind = 'i'
            details = (int(format_attr[1:]), None)
        return FormatItem(kind, details)


@dataclass
class FormatItemList(Node):
    items: list[FormatItem]

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        items = [FormatItem.parse(lex)]
        current_token = lex.current_token()
        while current_token.tag == Domaintag.DomainTag.Comma:
            current_token = lex.next_token()
            items.append(FormatItem.parse(lex))
            current_token = lex.current_token()
        return StatementList(items)


@dataclass
class RepeatedFormatGroup(Node):
    count: Number
    items: FormatItemList | FormatItem

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        count = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Multiplier, None))
        count = Number(int(count.attrib))
        tok = lex.current_token()
        if tok.tag == Domaintag.DomainTag.Lbracket:
            cop_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None))
            items = FormatItemList.parse(lex)
            ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None))
            return RepeatedFormatGroup(count, items)
        elif tok.tag == Domaintag.DomainTag.Format_specifier:
            items = FormatItem.parse(lex)
            return RepeatedFormatGroup(count, items)
        else:
            raise RuntimeError()


@dataclass
class RepeatedFormatItem(Node):
    items: list[FormatItem | RepeatedFormatGroup] | RepeatedFormatGroup

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        tok = lex.current_token()
        if tok.tag == Domaintag.DomainTag.Multiplier:
            return RepeatedFormatGroup.parse(lex)
        elif tok.tag == Domaintag.DomainTag.Format_specifier:
            items = [FormatItem.parse(lex)]
            tok = lex.current_token()
            if tok.tag == Domaintag.DomainTag.Comma:
                tok = lex.next_token()
                tail = RepeatedFormatItem.parse(lex)
                if isinstance(tail.items, list):
                    items += tail.items
                else:
                    items.append(tail.items)
            return RepeatedFormatItem(items)


@dataclass
class FormatList(Node):
    items: RepeatedFormatItem

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        cop_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None))
        items = RepeatedFormatItem.parse(lex)
        ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None))
        return FormatList(items)


@dataclass
class FormatStatement(Node):
    format_list: FormatList

    @staticmethod
    def parse(tuples: list):
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()
        format_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, "format"))
        format_list = FormatList.parse(lex)
        tuples.pop(0)
        return FormatStatement(format_list)

    def check(self, labels):
        pass


@dataclass
class NumberList(Node):
    start_value: (Number | Identifier)
    end_value: (Number | Identifier)
    step: (Number | Identifier)

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        if lex.current_token().tag == Domaintag.DomainTag.Real or lex.current_token().tag == Domaintag.DomainTag.Integer:
            start_value = Number.parse(lex)
        elif lex.current_token().tag == Domaintag.DomainTag.Identifier:
            start_value = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None))
        comma_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Comma, None))
        if lex.current_token().tag == Domaintag.DomainTag.Real or lex.current_token().tag == Domaintag.DomainTag.Integer:
            end_value = Number.parse(lex)
        elif lex.current_token().tag == Domaintag.DomainTag.Identifier:
            end_value = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None))
        tok = lex.current_token()
        if tok.tag == Domaintag.DomainTag.Comma:
            comma_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Comma, None))
            if lex.current_token().tag == Domaintag.DomainTag.Real or lex.current_token().tag == Domaintag.DomainTag.Integer:
                step = Number.parse(lex)
            elif lex.current_token().tag == Domaintag.DomainTag.Identifier:
                step = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None))
        else:
            step = Number(1)
        return NumberList(start_value, end_value, step)

    def check(self):
        pass



@dataclass
class DoStatement(Node):
    do_label: Label
    index: Identifier
    values: NumberList
    nested_operators: list[Statement]


    @staticmethod
    def parse(tuples: list):
        global stack_do
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()
        do_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, "do"))
        do_label = Label.parse(lex)
        stack_do.append(do_label.number.value)
        index = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None))
        eq_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Assign, None))
        values = NumberList.parse(lex)
        tuples.pop(0)
        nested_operators = NestedList.parse(tuples, do_label)
        return DoStatement(do_label, index, values, nested_operators)

    def check(self, labels):
        pass

@dataclass
class NestedList(Node):
    statements: list[Statement]
    end_do_operator: Statement

    @staticmethod
    def parse(tuples: list, do_label: int):
        global stack_do
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()

        statements = []

        while tuples[0][0] != do_label.number.value:
            if lex.current_token().attrib == 'end':
                raise ValueError("Незаконченный цикл DO")
            if tuples[0][0] in stack_do and tuples[0][0] != do_label.number.value:
                raise ValueError("Пересекающиеся циклы DO")
            statements.append(Statement.parse(tuples))
            if len(tuples) == 0:
                raise ValueError("Отсутствует END")
            lex.analyze_string(tuples[0][1])
            tokens = lex.get_tokens()
        end_do_operator = Statement.parse(tuples)
        stack_do.pop(-1)

        return NestedList(statements, end_do_operator)

    def check(self, labels):
        for stmt in self.statements:
            stmt.check(labels)


@dataclass
class GotoStatement(Node):
    label: Label

    @staticmethod
    def parse(tuples: list):
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()
        goto_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, "goto"))
        label = Label.parse(lex)
        tuples.pop(0)
        return GotoStatement(label)

    def check(self, labels):
        self.label.check(labels)


@dataclass
class ContinueStatement(Node):

    @staticmethod
    def parse(tuples: list):
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()
        continue_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, "continue"))
        tuples.pop(0)
        return ContinueStatement()

    def check(self, labels):
        pass


@dataclass
class IfStatement(Node):
    condition: ArithmeticExpression
    true_label: Label
    false_label: Label
    next_label: Label

    @staticmethod
    def parse(tuples: list):
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()
        if_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, "if"))
        cop_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None))
        expression = ArithmeticExpression.parse(lex)
        ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None))
        true_label = Label.parse(lex)
        comma_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Comma, None))
        false_label = Label.parse(lex)
        comma_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Comma, None))
        next_label = Label.parse(lex)
        tuples.pop(0)
        return IfStatement(expression, true_label, false_label, next_label)

    def check(self, labels):
        self.true_label.check(labels)
        self.false_label.check(labels)
        self.next_label.check(labels)


@dataclass
class ArrayDeclaration(Node):
    identifier: Identifier
    size: Number

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        identifier = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None))
        cop_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None))
        size = Number.parse(lex)
        ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None))
        ident = Identifier(identifier.attrib)
        return ArrayDeclaration(ident, size)

    def check(self, labels):
        self.identifier.check(labels)

        #пока не нужно отлетит на парсинге в runtime
        # if not isinstance(self.size, Number):
        #     raise TypeError(f"Размер массива {self.identifier.name} должен быть числом")

        if not (isinstance(self.size.value, int) and self.size.value >= 0):
            raise ValueError(f"Размер массива {self.identifier.name} должен быть целым числом без знака, получено: {self.size.value}")


@dataclass
class ArrayDeclarationList(Node):
    declarations: list[ArrayDeclaration]

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        declarations = [ArrayDeclaration.parse(lex)]
        current_token = lex.current_token()
        while current_token.tag == Domaintag.DomainTag.Comma:
            current_token = lex.next_token()
            declarations.append(ArrayDeclaration.parse(lex))
            current_token = lex.current_token()
        return ArrayDeclarationList(declarations)

    def check(self, labels):
        for decl in self.declarations:
            decl.check(labels)


@dataclass
class DimensionStatement(Node):
    array_declaration_list: ArrayDeclarationList

    @staticmethod
    def parse(tuples: list):
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()
        dim_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, "dimension"))
        array_decl_list = ArrayDeclarationList.parse(lex)
        tuples.pop(0)
        return DimensionStatement(array_decl_list)

    def check(self, labels):
        self.array_declaration_list.check(labels)


@dataclass
class Term(Node):
    left: Expression
    operator: str
    right: Expression

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        exponential = Exponentiation.parse(lex)
        current_token = lex.current_token()
        result = None
        while (current_token.tag == Domaintag.DomainTag.Multiplication_operator or
               current_token.tag == Domaintag.DomainTag.Division_operator):
            op = lex.next_token()
            rhs = Exponentiation.parse(lex)
            result = Term(result if result else exponential, op.attrib, rhs)
            current_token = lex.current_token()
        return result if result else exponential

    def check(self, labels):
        self.left.check(labels)
        self.right.check(labels)


@dataclass
class Call(Node):
    identifier: Identifier
    argument_list: ExpressionList

    def check(self, labels):
        self.identifier.check(labels)
        self.argument_list.check(labels)


@dataclass
class Factor(Node):
    value: Number | Identifier | ArithmeticExpression | Call
    # self.kind = kind

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        tok = lex.current_token()
        if tok.tag == Domaintag.DomainTag.Real or tok.tag == Domaintag.DomainTag.Integer or tok.tag == Domaintag.DomainTag.Multiplier or tok.tag == Domaintag.DomainTag.Subtraction_operator or tok.tag == Domaintag.DomainTag.Addition_operator:
            return Number.parse(lex)
        elif tok.tag == Domaintag.DomainTag.Lbracket:
            tok = lex.next_token()
            result = ArithmeticExpression.parse(lex)
            ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None))
            return result
        elif tok.tag == Domaintag.DomainTag.Identifier:
            identifier = lex.next_token()
            tok = lex.current_token()
            if tok.tag == Domaintag.DomainTag.Lbracket:
                cop_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None))
                expr_list = ExpressionList.parse(lex)
                ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None))
                return Call(identifier, expr_list)
            else:
                return Identifier(identifier.attrib)
        else:
            raise RuntimeError("")

    def check(self, labels):
        self.value.check(labels)


@dataclass
class Exponentiation(Node):
    base: Factor
    exponent: Expression

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        factor = Factor.parse(lex)
        current_token = lex.current_token()
        if current_token.tag == Domaintag.DomainTag.Exponentiation_operator:
            op = lex.next_token().attrib
            rhs = Exponentiation.parse(lex)
            return Exponentiation(factor, rhs)
        return factor

    def check(self, labels):
        self.base.check(labels)
        self.exponent.check(labels)
