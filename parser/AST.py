from dataclasses import dataclass
import parser_edsl as pe
from lexer import lexer
from lexer import Domaintag
from lexer.errors import *


@dataclass
class Node:
    pos: pe.Position

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        raise NotImplementedError()


class Statement(Node):

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        current_token = lex.expect(lex.current_token(), lexer.Token(Domaintag.DomainTag.Identifier, None, None))
        index = lex.token_idx
        try:
            if current_token.attrib == "read":
                return ReadStatement.parse(lex)
            elif current_token.attrib == "print":
                return PrintStatement.parse(lex)
            elif current_token.attrib == "format":
                return FormatStatement.parse(lex)
            elif current_token.attrib == "goto":
                return GotoStatement.parse(lex)
            elif current_token.attrib == "continue":
                return ContinueStatement.parse(lex)
            elif current_token.attrib == "if":
                return IfStatement.parse(lex)
            elif current_token.attrib == "dimension":
                return DimensionStatement.parse(lex)
            else:
                return AssignmentStatement.parse(lex)
        except Exception as ex:
            try:
                lex.token_idx = index
                return AssignmentStatement.parse(lex)
            except:
                raise ex

    def check(self, labels):
        pass


@dataclass
class Identifier(Node):
    name: str

    def check(self, labels):
        if len(self.name) > 6:
            raise IdentifierNameLengthError(self.pos, self.name)


@dataclass
class Number(Node):
    value: float | int

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        tok = lex.next_token()
        value = None
        if tok.tag == Domaintag.DomainTag.Integer or tok.tag == Domaintag.DomainTag.Multiplier:
            value = int(tok.attrib)
        elif tok.tag == Domaintag.DomainTag.Real:
            value = float(tok.attrib)
        else:
            raise RuntimeError()
        return Number(tok.coords.start.position(), value)

    def check(self, labels):
        pass


@dataclass
class Label(Node):
    number: Number

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        result = Number.parse(lex)
        return Label(result.pos, result)

    def check(self, labels):
        if self.number.value not in labels:
            raise LabelInexistantError(self.pos, self.number.value)


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
            result = ArithmeticExpression(op.coords.start.position(), result if result else term, op.attrib, rhs)
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
        return IdentifierList(identifiers[0].pos, identifiers)

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
        return ExpressionList(expressions[0].pos, expressions)

    def check(self, labels):
        for expr in self.expressions:
            expr.check(labels)


@dataclass
class StatementList(Node):
    statements: list[Statement]

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        statements = [Statement.parse(lex)]
        current_token = lex.current_token()
        while current_token.attrib != "end":
            statements.append(Statement.parse(lex))
            current_token = lex.current_token()
        return StatementList(statements[0].pos, statements)

    def check(self, labels):
        for stmt in self.statements:
            stmt.check(labels)


@dataclass
class Program(Node):
    identifier: Identifier
    statement_list: StatementList

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        kw_program = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None, None))
        identifier = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None, None))
        statements = StatementList.parse(lex)
        identifier = Identifier(identifier.coords.start.position(), identifier.attrib)
        return Program(kw_program.coords.start.position(), identifier, statements)

    def check(self, labels: list):
        self.identifier.check(labels)
        self.statement_list.check(labels)


@dataclass
class AssignmentStatement(Node):
    identifier: Identifier
    expression: ArithmeticExpression
    index: ExpressionList | None

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        identifier = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None, None))
        ident = Identifier(identifier.coords.start.position(), identifier.attrib)
        tok = lex.next_token()
        if tok.tag == Domaintag.DomainTag.Assign:
            expression = ArithmeticExpression.parse(lex)
            return AssignmentStatement(identifier.coords.start.position(), ident, expression, None)
        elif tok.tag == Domaintag.DomainTag.Lbracket:
            expr_list = ExpressionList.parse(lex)
            ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None, None))
            eq_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Assign, None, None))
            expr = ArithmeticExpression.parse(lex)
            return AssignmentStatement(identifier.coords.start.position(), ident, expr, expr_list)
        else:
            raise RuntimeError(f"{tok.coords}: expected token with tag - Assign | Lbracket, got - {tok.tag}")

    def check(self, labels):
        self.identifier.check(labels)


@dataclass
class ReadStatement(Node):
    format_identifier: Label
    identifiers: IdentifierList

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        read_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None, "read"))
        label = Label.parse(lex)
        comma_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Comma, None, None))
        identifiers = IdentifierList.parse(lex)
        return ReadStatement(read_kw.coords.start.position(), label, identifiers)

    def check(self, labels):
        self.format_identifier.check(labels)
        self.identifiers.check(labels)


@dataclass
class PrintStatement(Node):
    format_identifier: Label
    identifiers: ExpressionList

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        print_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None, "print"))
        label = Label.parse(lex)
        comma_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Comma, None, None))
        identifiers = ExpressionList.parse(lex)
        return PrintStatement(print_kw.coords.start.position(), label, identifiers)

    def check(self, labels):
        self.format_identifier.check(labels)
        self.format_identifier.check(labels)


@dataclass
class FormatItem(Node):
    kind: str
    details: tuple[int, str | int]

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        format_tok = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Format_specifier, None, None))
        format_attr = format_tok.attrib
        kind, details = None, None
        if "h" in format_attr:
            kind = 'h'
            hstring = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.H_string, None, None))
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
        return FormatItem(format_tok.coords.start.position(), kind, details)


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
        return StatementList(items[0].pos, items)


@dataclass
class RepeatedFormatGroup(Node):
    count: Number
    items: FormatItemList | FormatItem

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        count = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Multiplier, None, None))
        count = Number(count.coords.start.position(), int(count.attrib))
        tok = lex.current_token()
        if tok.tag == Domaintag.DomainTag.Lbracket:
            cop_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None, None))
            items = FormatItemList.parse(lex)
            ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None, None))
            return RepeatedFormatGroup(count.pos, count, items)
        elif tok.tag == Domaintag.DomainTag.Format_specifier:
            items = FormatItem.parse(lex)
            return RepeatedFormatGroup(count.pos, count, items)
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
            return RepeatedFormatItem(items[0].pos, items)


@dataclass
class FormatList(Node):
    items: RepeatedFormatItem

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        cop_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None, None))
        items = RepeatedFormatItem.parse(lex)
        ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None, None))
        return FormatList(cop_kw.coords.start.position(), items)


@dataclass
class FormatStatement(Node):
    format_list: FormatList

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        format_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None, "format"))
        format_list = FormatList.parse(lex)
        return FormatStatement(format_kw.coords.start.position(), format_list)

    def check(self, labels):
        pass


@dataclass
class GotoStatement(Node):
    label: Label

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        goto_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None, "goto"))
        label = Label.parse(lex)
        return GotoStatement(goto_kw.coords.start.position(), label)

    def check(self, labels):
        self.label.check(labels)


@dataclass
class ContinueStatement(Node):

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        continue_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None, "continue"))
        return ContinueStatement(continue_kw.coords.start.position())

    def check(self, labels):
        pass


@dataclass
class IfStatement(Node):
    condition: ArithmeticExpression
    true_label: Label
    false_label: Label
    next_label: Label

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        if_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None, "if"))
        cop_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None, None))
        expression = ArithmeticExpression.parse(lex)
        ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None, None))
        true_label = Label.parse(lex)
        comma_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Comma, None, None))
        false_label = Label.parse(lex)
        comma_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Comma, None, None))
        next_label = Label.parse(lex)
        return IfStatement(if_kw.coords.start.position(), expression, true_label, false_label, next_label)

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
        identifier = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None, None))
        cop_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None, None))
        size = Number.parse(lex)
        ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None, None))
        ident = Identifier(identifier.coords.start.position(), identifier.attrib)
        return ArrayDeclaration(identifier.coords.start.position(), ident, size)

    def check(self, labels):
        self.identifier.check(labels)


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
        return ArrayDeclarationList(declarations[0].pos, declarations)

    def check(self, labels):
        for decl in self.declarations:
            decl.check(labels)


@dataclass
class DimensionStatement(Node):
    array_declaration_list: ArrayDeclarationList

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        dim_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None, "dimension"))
        array_decl_list = ArrayDeclarationList.parse(lex)
        return DimensionStatement(dim_kw.coords.start.position(), array_decl_list)

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
        if (current_token.tag == Domaintag.DomainTag.Multiplication_operator or
                current_token.tag == Domaintag.DomainTag.Division_operator):
            op = lex.next_token().attrib
            rhs = Term.parse(lex)
            return Term(exponential.pos, exponential, op, rhs)
        return exponential

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
        if tok.tag == Domaintag.DomainTag.Real or tok.tag == Domaintag.DomainTag.Integer or tok.tag == Domaintag.DomainTag.Multiplier:
            return Number.parse(lex)
        elif tok.tag == Domaintag.DomainTag.Lbracket:
            tok = lex.next_token()
            result = ArithmeticExpression.parse(lex)
            ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None, None))
            return result
        elif tok.tag == Domaintag.DomainTag.Identifier:
            identifier = lex.next_token()
            tok = lex.current_token()
            if tok.tag == Domaintag.DomainTag.Lbracket:
                cop_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None, None))
                expr_list = ExpressionList.parse(lex)
                ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None, None))
                return Call(identifier.coords.start.position(), identifier, expr_list)
            else:
                return Identifier(identifier.coords.start.position(), identifier.attrib)
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
            return Exponentiation(factor.pos, factor, rhs)
        return factor

    def check(self, labels):
        self.base.check(labels)
        self.exponent.check(labels)
