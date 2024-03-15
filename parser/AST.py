from dataclasses import dataclass
import parser_edsl as pe
from lexer import lexer
from lexer import Domaintag
from lexer.errors import *
from parser.Types import *
from parser.SymbolsTable import *
from llvmlite import ir, binding

stack_do = []
format_labels = []

@dataclass
class Node:

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        raise NotImplementedError()

@dataclass
class Statement(Node):
    label: int
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

    def check(self, symbols_table:SymbolTable):
        self.statement = self.statement.check(symbols_table)
        return self



@dataclass
class Identifier(Node):
    name: str

    def check(self, symbol_table):
        if len(self.name) > 6:
            raise IdentifierNameLengthError(None, self.name)

        if symbol_table.lookup(self.name):
            self.type = symbol_table.lookup(self.name).type
        else:
            symbol_table.add(self.name, FloatT(), True)
        return self

    def codegen(self, symbols_table, lvalue=False):
        if lvalue:
            return symbols_table.lookup(self.name).llvmobj
        else:
            return symbols_table.builder.load(symbols_table.lookup(self.name).llvmobj)



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

    def codegen(self, symbols_table):
        if isinstance(self.type, IntegerT):
            return ir.Constant(ir.IntType(32), self.value)
        else:
            return ir.Constant(ir.FloatType(), self.value)

    def check(self, symbol_table):
        if isinstance(self.value, int):
            self.type = IntegerT()
        else:
            self.type = FloatT()
        return self


@dataclass
class Label(Node):
    number: Number

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        result = Number.parse(lex)
        return Label(result)

    def check(self, symbols_table):
        label = f"LABEL_{self.number.value}"
        # if symbols_table.lookup(label) is None:
        #     raise LabelInexistantError(None, self.number.value)
        return self

class Expression(Node):
    def __init__(self, expressions):
        self.expressions = expressions

    def check(self, symbols_table):
        for expr in self.expressions:
            expr.check(symbols_table)
        return self


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

    def codegen(self, symbol_table):
        add = symbol_table.builder.add if isinstance(self.type, IntegerT) else symbol_table.builder.fadd
        sub = symbol_table.builder.sub if isinstance(self.type, IntegerT) else symbol_table.builder.fsub
        if self.operator == '+':
            return add(self.left.codegen(symbol_table), self.right.codegen(symbol_table))
        elif self.operator == '-':
            return sub(self.left.codegen(symbol_table), self.right.codegen(symbol_table))
        else:
            raise RuntimeError()

    def check(self, symbols_table):
        if isinstance(self.left, Identifier):
            if symbols_table.lookup(self.left.name) is None:  # мейби нужно вызывать raise error, потому что переменная не определена выше
                # raise ValueError("Подозрительная переменная")
                symbols_table.add(self.left.name, FloatT(), True)

        self.left = self.left.check(symbols_table)
        self.right = self.right.check(symbols_table)

        if isinstance(self.left.type, IntegerT) and isinstance(self.right.type, IntegerT):
            self.type = IntegerT()
        # elif self.left.type is None or self.right.type is None:
        #     self.type = None
        else:
            if isinstance(self.left.type, IntegerT):
                self.left = FloatConversion(self.left).check(symbols_table)
            else:
                self.right = FloatConversion(self.right).check(symbols_table)
            self.type = FloatT()
        return self
@dataclass
class FloatConversion(Node):
    expression: Expression

    def codegen(self, symbols_table):
        return symbols_table.builder.sitofp(self.expression.codegen(symbols_table), ir.FloatType())

    def check(self, symbol_table):
        self.expression = self.expression.check(symbol_table)
        self.type = FloatT()
        return self

@dataclass
class IntegerConversion(Node):
    expression: Expression

    def codegen(self, symbols_table):
        return symbols_table.builder.fptosi(self.expression.codegen(symbols_table), ir.IntType(32))

    def check(self, symbol_table):
        self.expression = self.expression.check(symbol_table)
        self.type = IntegerT()
        return self

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

    def check(self, symbols_table):
        for i in range (len(self.identifiers)):
            self.identifiers[i] = self.identifiers[i].check(symbols_table)
        return self


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

    def check(self, symbols_table):
        for i in range(len(self.expressions)):
            self.expressions[i] = self.expressions[i].check(symbols_table)
        return self


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

    def codegen(self, symbols_table):
        for statement in self.statements:
            if statement.label:
                symbols_table.labels[statement.label] = symbols_table.builder.append_basic_block(f"{statement.label}")
        for statement in self.statements:
            statement.codegen(symbols_table)
        for i in range(len(symbols_table.func.basic_blocks) - 1):
            if symbols_table.func.basic_blocks[i].terminator is None:
                builder = ir.IRBuilder(symbols_table.func.basic_blocks[i])
                builder.branch(symbols_table.func.basic_blocks[i + 1])

    def check(self,  symbols_table: SymbolTable):
        for i in range(len(self.statements)):
            self.statements[i] = self.statements[i].check(symbols_table)
        return self


@dataclass
class Program(Node):
    identifier: Identifier
    statement_list: StatementList

    @staticmethod
    def parse(tuples: list):
        global format_labels
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

        return Program(identifier, statements), format_labels

    def codegen(self, module_name=None):
        program_module = ir.Module(name=module_name if module_name else __file__)
        program_module.triple = binding.get_default_triple()
        program_module.data_layout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-f80:128-n8:16:32:64-S128"
        self.symbols_table.module = program_module
        self.symbols_table.func = ir.Function(self.symbols_table.module, ir.FunctionType(ir.VoidType(), []), "Main")
        self.symbols_table.builder = ir.IRBuilder(self.symbols_table.func.append_basic_block("entry"))
        for current_symbol in self.symbols_table.symbols:
            instr = self.symbols_table.builder.alloca(current_symbol.type.llvm_type(), 1, current_symbol.value)
            current_symbol.llvmobj = instr
        self.statement_list.codegen(self.symbols_table)
        self.symbols_table.builder.ret_void()
        return program_module


    def check(self):
        system_functions = ['sin', 'cos', 'alog', 'alog10', 'sqrt', 'abs', 'exp']
        self.symbols_table = SymbolTable()
        for function in system_functions:
            self.symbols_table.program_functions.append(function)
        self.statement_list = self.statement_list.check(self.symbols_table)
        self.symbols_table.suspicious_symbols = [symbol for symbol in self.symbols_table.suspicious_symbols if
                                                    symbol.value not in self.symbols_table.symbols]
        return self, self.symbols_table




@dataclass
class AssignmentStatement(Statement):
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
            if lex.current_token().tag != Domaintag.DomainTag.EOF:
                raise ValueError("Выражение спарсилось не до конца")
            label_op = tuples[0][0]
            tuples.pop(0)
            return AssignmentStatement(label_op, ident, expression, None)
        elif tok.tag == Domaintag.DomainTag.Lbracket:
            expr_list = ExpressionList.parse(lex)
            ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None))
            eq_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Assign, None))
            expr = ArithmeticExpression.parse(lex)
            label_op = tuples[0][0]
            tuples.pop(0)
            return AssignmentStatement(label_op, ident, expr, expr_list)
        else:
            raise RuntimeError(f"{tok.coords}: expected token with tag - Assign | Lbracket, got - {tok.tag}")

    def codegen(self, symbols_table):
        if self.label:
            symbols_table.builder = ir.IRBuilder(symbols_table.labels[self.label])
        ptr = self.identifier.codegen(symbols_table, True)
        value = self.expression.codegen(symbols_table)
        symbols_table.builder.store(value, ptr)

    def check(self, symbol_table):
        self.expression = self.expression.check(symbol_table)

        if symbol_table.lookup(self.identifier.name) is None:
            symbol_table.add(self.identifier.name, self.expression.type)

        self.identifier = self.identifier.check(symbol_table)

        if self.identifier.type != self.expression.type:
            if isinstance(self.expression.type, IntegerT):
                self.expression = FloatConversion(self.expression).check(symbol_table)
            else:
                self.expression = IntegerConversion(self.expression).check(symbol_table)
        return self


@dataclass
class ReadStatement(Statement):
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
        label_op = tuples[0][0]
        tuples.pop(0)
        return ReadStatement(label_op, label, identifiers)

    def codegen(self, symbols_table):
        if self.label:
            symbols_table.builder = ir.IRBuilder(symbols_table.labels[self.label])
        args = []
        for identifier in self.identifiers.identifiers:
            args.append(symbols_table.lookup(identifier.name).llvmobj)
        symbols_table.builder.call(symbols_table.lookup_function('read').llvmobj, [symbols_table.formats[self.format_identifier.number].codegen(symbols_table)] + args)

    def check(self, symbols_table):
        self.format_identifier = self.format_identifier.check(symbols_table)
        self.identifiers = self.identifiers.check(symbols_table)
        return self


@dataclass
class PrintStatement(Statement):
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
        label_op = tuples[0][0]
        tuples.pop(0)
        return PrintStatement(label_op, label, identifiers)

    def codegen(self, symbols_table):
        if self.label:
            symbols_table.builder = ir.IRBuilder(symbols_table.labels[self.label])
        args = []
        for identifier in self.identifiers.expressions:
            args.append(identifier.codegen(symbols_table))
        symbols_table.builder.call(symbols_table.lookup_function('print').llvmobj, [symbols_table.formats[self.format_identifier.number].codegen(symbols_table)] + args)

    def check(self, labels):
        self.format_identifier.check(labels)
        return self


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

    def codegen(self, symbol_table):
        if self.kind == 'x':
            return ' ' * self.details[0]
        elif self.kind == 'h':
            return self.details[1]
        elif self.kind == 'e':
            return f'%{self.details[0] + self.details[1] + 1}.{self.details[1]}e'
        elif self.kind == 'f':
            return f'%{self.details[0] + self.details[1] + 1}.{self.details[1]}f'
        else:
            return f'%{self.details[0]}d'

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
        return FormatItemList(items)

    def codegen(self, symbol_table):
        return ''.join([item.codegen(symbol_table) for item in self.items])


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

    def codegen(self, symbol_table):
        return self.items.codegen(symbol_table) * self.count.value


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

    def codegen(self, symbol_table):
        if isinstance(self.items, list):
            return ''.join([item.codegen(symbol_table) for item in self.items])
        else:
            return self.items.codegen(symbol_table)


@dataclass
class FormatList(Node):
    items: RepeatedFormatItem

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        cop_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None))
        items = RepeatedFormatItem.parse(lex)
        ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None))
        return FormatList(items)

    def codegen(self, symbol_table):
        if hasattr(self, "__cached_var"):
            return self.__cached_var
        else:
            if hasattr(FormatList, "static_cnt"):
                FormatList.static_cnt += 1
            else:
                FormatList.static_cnt = 1
            value = self.items.codegen(symbol_table)
            var = ir.GlobalVariable(symbol_table.module, ir.ArrayType(ir.IntType(32), len(value) + 1), f".str.{FormatList.static_cnt}")
            var.initializer = ir.Constant(ir.ArrayType(ir.IntType(32), len(value) + 1), [ord(char) for char in value] + [0])
            self.__cached_var = var
            return self.__cached_var


@dataclass
class FormatStatement(Statement):
    format_list: FormatList

    @staticmethod
    def parse(tuples: list):
        global format_labels
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        if tuples[0][0] is None:
            raise ValueError("Передается оператор Format без метки")
        format_labels.append(tuples[0][0])
        tokens = lex.get_tokens()
        format_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, "format"))
        format_list = FormatList.parse(lex)
        label_op = tuples[0][0]
        tuples.pop(0)
        return FormatStatement(label_op, format_list)

    def codegen(self, symbols_table):
        if self.label:
            symbols_table.builder = ir.IRBuilder(symbols_table.labels[self.label])

    def check(self, symbol_table):
        symbol_table.formats[self.label] = self.format_list
        return self


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

    def check(self, symbol_table):
        self.end_value = self.end_value.check(symbol_table)
        self.start_value = self.start_value.check(symbol_table)
        self.step = self.step.check(symbol_table)
        if isinstance(self.end_value.type, IntegerT) and isinstance(self.start_value.type, IntegerT) and isinstance(self.step.type, IntegerT):
            self.type = IntegerT()
        else:
            self.type = FloatT()
        return self



@dataclass
class DoStatement(Statement):
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
        lable_op = tuples[0][0]
        tuples.pop(0)
        nested_operators = NestedList.parse(tuples, do_label)
        return DoStatement(lable_op, do_label, Identifier(index.attrib), values, nested_operators)

    def codegen(self, symbols_table):
        if self.label:
            symbols_table.builder = ir.IRBuilder(symbols_table.labels[self.label])

        idx = symbols_table.func.basic_blocks.index(symbols_table.llvm.builder.block) + 1
        cond_block = symbols_table.func.insert_basic_block(idx)
        cond_block_builder = ir.IRBuilder(cond_block)
        body_block = symbols_table.func.insert_basic_block(idx + 1)
        body_block_builder = ir.IRBuilder(body_block)
        inc_block = symbols_table.func.insert_basic_block(idx + 2)
        inc_block_builder = ir.IRBuilder(inc_block)
        end_block = symbols_table.func.insert_basic_block(idx + 3)

    def check(self, symbol_table):
        self.values = self.values.check(symbol_table)
        if isinstance(self.values.type, IntegerT):
            symbol_table.add(self.index.name, IntegerT())
        else:
            symbol_table.add(self.index.name, FloatT())
        self.nested_operators = self.nested_operators.check(symbol_table)
        return self

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

    def check(self, symbol_table):
        for i in range (len(self.statements)):
            self.statements[i] = self.statements[i].check(symbol_table)
        return self


@dataclass
class GotoStatement(Statement):
    go_to_label: Label

    @staticmethod
    def parse(tuples: list):
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()
        goto_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, "goto"))
        label = Label.parse(lex)
        label_op = tuples[0][0]
        tuples.pop(0)
        return GotoStatement(label_op, label)

    def codegen(self, symbols_table):
        if self.label:
            symbols_table.builder = ir.IRBuilder(symbols_table.labels[self.label])
        symbols_table.builder.branch(symbols_table.labels[self.label])


    def check(self, symbols_table):
        self.go_to_label = self.go_to_label.check(symbols_table)
        return self


@dataclass
class ContinueStatement(Statement):

    @staticmethod
    def parse(tuples: list):
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()
        continue_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, "continue"))
        label_op = tuples[0][0]
        tuples.pop(0)
        return ContinueStatement(label_op)

    def codegen(self, symbols_table):
        if self.label:
            symbols_table.builder = ir.IRBuilder(symbols_table.labels[self.label])

    def check(self, labels):
        return self


@dataclass
class IfStatement(Statement):
    condition: ArithmeticExpression
    negative_label: Label
    zero_label: Label
    positive_label: Label

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
        label_op = tuples[0][0]
        tuples.pop(0)
        return IfStatement(label_op, expression, true_label, false_label, next_label)

    def codegen(self, symbols_table):
        if self.label:
            symbols_table.builder = ir.IRBuilder(symbols_table.labels[self.label])
        cond = self.condition.codegen(symbols_table)
        cmp = symbols_table.builder.icmp_signed('<', cond, ir.Constant(ir.IntType(32), 0))
        idx = symbols_table.func.basic_blocks.index(symbols_table.builder.block) + 1
        cond_block = symbols_table.func.insert_basic_block(idx)
        symbols_table.builder.cbranch(cmp, symbols_table.labels[self.negative_label.number.value], cond_block)
        new_builder = ir.IRBuilder(cond_block)
        cmp = new_builder.icmp_signed('==', cond, ir.Constant(ir.IntType(32), 0))
        new_builder.cbranch(cmp, symbols_table.labels[self.zero_label.number.value], symbols_table.labels[self.positive_label.number.value])

    def check(self, symbol_table):
        self.condition = self.condition.check(symbol_table)
        self.negative_label = self.negative_label.check(symbol_table)
        self.zero_label = self.zero_label.check(symbol_table)
        self.positive_label = self.positive_label.check(symbol_table)
        return self


@dataclass
class ArrayDeclaration(Node):
    identifier: Identifier
    size: ExpressionList

    @staticmethod
    def parse(lex: lexer.LexicalAnalyzer):
        identifier = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None))
        cop_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None))
        size = ExpressionList.parse(lex)
        ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None))
        ident = Identifier(identifier.attrib)
        return ArrayDeclaration(ident, size)

    def check(self, symbol_table):
        self.size = self.size.check(symbol_table)
        size = []
        for i in range(len(self.size.expressions)):
            if isinstance(self.size.expressions[i], Number) is False:
                raise ValueError("В определение размера массива вводится не число")
            if isinstance(self.size.expressions[i].type, IntegerT)is False:
                raise ValueError("В определение размера массива вводится не целое число")
            if self.size.expressions[i].value < 0:
                raise ValueError("В определении размера массива должно использоваться беззнаковое число, однако обнаружено число с знаком.")


        for i in range (len(self.size.expressions)):
            size.append(self.size.expressions[i].value)

        if symbol_table.lookup(self.identifier.name) is None:
            symbol_table.add(self.identifier.name, ArrayT(FloatT(), size))
        return self


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

    def check(self, symbol_table):
        for i in range(len(self.declarations)):
            self.declarations[i] = self.declarations[i].check(symbol_table)
        return self


@dataclass
class DimensionStatement(Statement):
    array_declaration_list: ArrayDeclarationList

    @staticmethod
    def parse(tuples: list):
        lex = lexer.LexicalAnalyzer(tuples[0])
        lex.analyze_string(tuples[0][1])
        tokens = lex.get_tokens()
        dim_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, "dimension"))
        array_decl_list = ArrayDeclarationList.parse(lex)
        lable_op = tuples[0][0]
        tuples.pop(0)
        return DimensionStatement(lable_op, array_decl_list)

    def check(self, symbol_table):
        self.array_declaration_list = self.array_declaration_list.check(symbol_table)
        return self


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

    def codegen(self, symbol_table):
        mul = symbol_table.builder.mul if isinstance(self.type, IntegerT) else symbol_table.builder.fmul
        div = symbol_table.builder.sdiv if isinstance(self.type, IntegerT) else symbol_table.builder.fdiv
        if self.operator == '*':
            return mul(self.left.codegen(symbol_table), self.right.codegen(symbol_table))
        elif self.operator == '/':
            return div(self.left.codegen(symbol_table), self.right.codegen(symbol_table))
        else:
            raise RuntimeError()

    def check(self, symbol_table):
        self.left = self.left.check(symbol_table)
        self.right = self.right.check(symbol_table)
        if isinstance(self.left.type, IntegerT) and isinstance(self.right.type, IntegerT):
            self.type = IntegerT()
        else:
            if isinstance(self.left.type, IntegerT):
                self.left = FloatConversion(self.left).check(symbol_table)
            else:
                self.right = FloatConversion(self.right).check(symbol_table)
            self.type = FloatT()
        return self


@dataclass
class Call(Node):
    identifier: Identifier
    argument_list: ExpressionList


    def check(self, symbol_table):
        if self.identifier.name in symbol_table.program_functions:
            self.identifier.type = FunctionsT

        self.identifier = self.identifier.check(symbol_table)
        self.argument_list = self.argument_list.check(symbol_table)

        if isinstance(self.identifier.type, ArrayT):
            return ArrayIndex(self.identifier, self.argument_list).check(symbol_table)

        self.type = self.identifier.type
        return self
@dataclass
class ArrayIndex(Node):
    name: Identifier
    argument_list: ExpressionList
    def check(self, symbol_table):

        for i in range(len(self.argument_list.expressions)):

            if not isinstance(self.argument_list.expressions[i].type, IntegerT):
                self.argument_list.expressions[i] = IntegerConversion(self.argument_list.expressions[i]).check(symbol_table)

            if isinstance(self.argument_list.expressions[i], Number) and self.argument_list.expressions[i].value < 0:
                raise ValueError(
                    "При вызове массива должно использоваться беззнаковое число, однако обнаружено число с знаком.")
        self.type = self.name.type
        return self



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
            identifier = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Identifier, None))
            tok = lex.current_token()
            if tok.tag == Domaintag.DomainTag.Lbracket:
                cop_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Lbracket, None))
                expr_list = ExpressionList.parse(lex)
                ccp_kw = lex.expect(lex.next_token(), lexer.Token(Domaintag.DomainTag.Rbracket, None))
                ident = Identifier(identifier.attrib)
                return Call(ident, expr_list)
            else:
                return Identifier(identifier.attrib)
        else:
            raise RuntimeError("")

    def check(self, symbol_table):
        self.value = self.value.check(symbol_table)
        return self


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

    def codegen(self, symbol_table):
        exp = symbol_table.lookup_function('exp').llvmobj
        return symbol_table.builder.call(exp, [self.base.codegen(symbol_table), self.exponent.codegen(symbol_table)])


    def check(self, symbol_table):
        self.base = self.base.check(symbol_table)
        self.exponent = self.exponent.check(symbol_table)
        if isinstance(self.base.type, IntegerT) and isinstance(self.exponent.type, IntegerT):
            self.type = IntegerT()
        elif self.base.type is None or self.exponent.type is None:
            self.type = None
        else:
            self.type = FloatT()
        return self
