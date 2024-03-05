import copy
from typing import Any, Type

from .Token import Coords, Position, Token
from .Domaintag import DomainTag


class LexicalAnalyzer:
    def __init__(self, tuples: list):
        self.lines = [line_text for _, line_text in tuples]
        self.row = 1
        self.i = 0
        self.col = 1
        self.token_idx = 0
        self.__tokens = None

    def __token_gen(self):
        for line in self.lines:
            line = line.lower()
            self.col = 1
            self.i = 0
            while self.i < len(line):

                ##Обработка операций
                # Обработка '='
                if line[self.i:self.i + 1].lower() == '=':
                    j = self.i + 1
                    coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                    yield Token(DomainTag.Assign, coords, '=')
                    self.i = j
                # Обработка '+'
                elif line[self.i:self.i + 1].lower() == '+':
                    j = self.i + 1
                    coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                    yield Token(DomainTag.Addition_operator, coords, '+')
                    self.i = j
                # Обработка '**'
                elif line[self.i:self.i + 2].lower() == '**':
                    j = self.i + 2
                    coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                    yield Token(DomainTag.Exponentiation_operator, coords, '**')
                    self.i = j
                # Обработка '-'
                elif line[self.i:self.i + 1].lower() == '-':
                    j = self.i + 1
                    coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                    yield Token(DomainTag.Subtraction_operator, coords, '-')
                    self.i = j
                # Обработка '*'
                elif line[self.i:self.i + 1].lower() == '*':
                    j = self.i + 1
                    coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                    yield Token(DomainTag.Multiplication_operator, coords, '*')
                    self.i = j
                # Обработка '/'
                elif line[self.i:self.i + 1].lower() == '/':
                    j = self.i + 1
                    coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                    yield Token(DomainTag.Division_operator, coords, '/')
                    self.i = j


                # Обработка Format
                elif line[self.i:self.i + 6].lower().startswith('format'):
                    identifier = line[self.i: self.i + 6]
                    j = self.i + 6
                    coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                    yield Token(DomainTag.Identifier, coords, identifier)
                    self.i = j

                    while self.i < len(line) and line[self.i] == ' ':
                        self.i += 1

                    if self.i < len(line) and line[self.i] == '(':
                        coords = Coords(Position(self.row, self.col + self.i), Position(self.row, self.i + 1))
                        yield Token(DomainTag.Lbracket, coords, '(')
                        self.i += 1
                        while self.i < len(line):
                            if line[self.i].isdigit():
                                start_i = self.i
                                while self.i < len(line) and line[self.i].isdigit():
                                    self.i += 1
                                number = line[start_i:self.i]

                                # Проверяем, следует ли за числом 'h' или 'x'
                                if self.i < len(line) and line[self.i].lower() in ['x', 'h']:
                                    spec = line[self.i].lower()
                                    coords = Coords(Position(self.row, self.col + start_i), Position(self.row, self.i))
                                    yield Token(DomainTag.Format_specifier, coords, number + spec)
                                    self.i += 1

                                    if spec == 'h':
                                        start_h = self.i
                                        number = int(number)
                                        while self.i < len(line) and number != 0:
                                            self.i += 1
                                            number -= 1
                                        if self.i > start_h:
                                            all_symbols = line[start_h:self.i]
                                            coords = Coords(Position(self.row, self.col + start_h),
                                                            Position(self.row, self.i))
                                            yield Token(DomainTag.H_string, coords, all_symbols)


                                else:
                                    coords = Coords(Position(self.row, self.col + start_i), Position(self.row, self.i))
                                    yield Token(DomainTag.Multiplier, coords, number)

                            elif line[self.i].lower() in ['i', 'f', 'e']:
                                spec_start = self.i
                                self.i += 1

                                while self.i < len(line) and line[self.i].isdigit():
                                    self.i += 1
                                if line[self.i:self.i + 1] == '.':
                                    self.i += 1
                                    while self.i < len(line) and line[self.i].isdigit():
                                        self.i += 1
                                spec = line[spec_start:self.i]
                                coords = Coords(Position(self.row, self.col + spec_start), Position(self.row, self.i))
                                yield Token(DomainTag.Format_specifier, coords, spec)
                            elif line[self.i] == ',':
                                coords = Coords(Position(self.row, self.col + self.i), Position(self.row, self.i + 1))
                                yield Token(DomainTag.Comma, coords, ',')
                                self.i += 1

                            elif line[self.i] == '(':
                                coords = Coords(Position(self.row, self.col + self.i), Position(self.row, self.i + 1))
                                yield Token(DomainTag.Lbracket, coords, '(')
                                self.i += 1

                            elif line[self.i] == ')':
                                coords = Coords(Position(self.row, self.col + self.i), Position(self.row, self.i + 1))
                                yield Token(DomainTag.Rbracket, coords, ')')
                                self.i += 1
                                break
                            else:
                                self.i += 1


                ##Обработка лексических знаков
                # Обработка ','
                elif line[self.i:self.i + 1].lower() == ',' :
                    j = self.i + 1
                    coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                    yield Token(DomainTag.Comma, coords, ',')
                    self.i = j

                # Обработка '('
                elif line[self.i:self.i + 1].lower() == '(':
                    j = self.i + 1
                    coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                    yield Token(DomainTag.Lbracket, coords, '(')
                    self.i = j

                # Обработка ')'
                elif line[self.i:self.i + 1].lower() == ')':
                    j = self.i + 1
                    coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                    yield Token(DomainTag.Rbracket, coords, ')')
                    self.i = j

                ##Обработка чисел и меток
                elif line[self.i].isdigit() or (line[self.i] == '-' and self.i + 1 < len(line) and line[self.i + 1].isdigit()) or (line[self.i] == '.' and self.i + 1 < len(line) and line[self.i + 1].isdigit()) :
                    j = self.i
                    if line[j] == '-':
                        j += 1
                    elif line[j] == '.':
                        j += 1
                    while j < len(line) and line[j].isdigit():
                        j += 1
                    if j < len(line) and line[j] == '.':
                        j += 1
                        while j < len(line) and line[j].isdigit():
                            j += 1
                    if j < len(line) and line[j].lower() == 'e':
                        j += 1
                        if j < len(line) and (line[j] == '+' or line[j] == '-'):
                            j += 1
                        while j < len(line) and line[j].isdigit():
                            j += 1

                    number = line[self.i:j]
                    coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                    if '.' in number or 'e' in number.lower():
                        yield Token(DomainTag.Real, coords, number)
                    else:
                        yield Token(DomainTag.Integer, coords, number)
                    self.i = j

                # Обработка идентификатора
                elif line[self.i].lower().isalpha():
                    j = 0
                    if line[self.i:].lower().startswith('if'):
                        coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                        yield Token(DomainTag.Identifier, coords, "if")
                        self.i += 2
                    elif line[self.i:].lower().startswith("read"):
                        coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                        yield Token(DomainTag.Identifier, coords, "read")
                        self.i += 4
                    elif line[self.i:].lower().startswith("print"):
                        coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                        yield Token(DomainTag.Identifier, coords, "print")
                        self.i += 5
                    elif line[self.i:].lower().startswith("goto"):
                        coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                        yield Token(DomainTag.Identifier, coords, "goto")
                        self.i += 4
                    elif line[self.i:].lower().startswith("continue"):
                        coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                        yield Token(DomainTag.Identifier, coords, "continue")
                        self.i += 8
                    elif line[self.i:].lower().startswith("dimension"):
                        coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                        yield Token(DomainTag.Identifier, coords, "dimension")
                        self.i += 9
                    elif line[self.i:].lower().startswith("program"):
                        coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                        yield Token(DomainTag.Identifier, coords, "program")
                        self.i += 7
                    elif line[self.i:].lower().startswith("end"):
                        coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                        yield Token(DomainTag.Identifier, coords, "end")
                        self.i += 3
                    elif line[self.i:].lower().startswith("do"):
                        coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                        yield Token(DomainTag.Identifier, coords, "do")
                        self.i += 2
                    else:
                        j = self.i + 1
                        while j < len(line) and line[j].isalnum():
                            j += 1
                        identifier = line[self.i:j]
                        coords = Coords(Position(self.row, self.col + self.i), Position(self.row, j))
                        yield Token(DomainTag.Identifier, coords, identifier)
                        self.i = j

                elif line[self.i] == ' ':
                    self.i += 1

                else:
                    j = self.i + 1
                    while j < len(line) and line[j:j + 2] != '&H' and not line[j].isalpha():
                        j += 1
                    lexem = line[self.i:j]
                    if lexem:
                        yield Token(DomainTag.Error, Coords(Position(self.row, self.i + 1), Position(self.row, j)))
                    self.i = j
            self.row += 1

    # def gluing_tokens(self):
    #     while self.__tokens != (Token(DomainTag.Rbracket) or Token(DomainTag.Assign)):


    def next_token(self):
        result = self.tokens()[self.token_idx]
        self.token_idx += 1
        return result

    def current_token(self):
        return self.tokens()[self.token_idx]

    def tokens(self):
        if not self.__tokens:
            self.token_idx = 0
            self.__tokens = list(self.__token_gen())
        return self.__tokens

    def expect(self, found: Token, expected: Token):
        if found.tag != expected.tag:
            raise RuntimeError(f"{found.coords}: expected token with tag - {expected.tag}, got - {found.tag}")
        if expected.attrib:
            if found.attrib != expected.attrib:
                raise RuntimeError(f"{found.coords}: expected token with attrib - {expected.attrib}, got - {found.attrib}")
        return found
