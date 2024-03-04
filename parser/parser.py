# ##Обработка ключевых слов
#                 #Обработка PRINT
#                 if line[i:i + 5].lower() == 'print' and (len(line) == i + 5 or line[i + 5] == ' '):
#                     j = i + 5
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Keyword, coords, 'PRINT'))
#                     i = j
#
#                     while i < len(line) and line[i] == ' ':
#                         i += 1
#
#                     if i < len(line) and line[i].isdigit():
#                         start_i = i
#                         while i < len(line) and line[i].isdigit():
#                             i += 1
#                         format_number = line[start_i:i]
#                         coords = Coords(Position(self.row, col + start_i), Position(self.row, i))
#                         self.tokens.append(Token(DomainTag.Format_label, coords, format_number))
#
#                 # Обработка Read
#                 if line[i:i + 4].lower() == 'read' and (len(line) == i + 4 or line[i + 4] == ' '):
#                     j = i + 4
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Keyword, coords, 'READ'))
#                     i = j
#
#                     while i < len(line) and line[i] == ' ':
#                         i += 1
#
#                     if i < len(line) and line[i].isdigit():
#                         start_i = i
#                         while i < len(line) and line[i].isdigit():
#                             i += 1
#                         format_number = line[start_i:i]
#                         coords = Coords(Position(self.row, col + start_i), Position(self.row, i))
#                         self.tokens.append(Token(DomainTag.Format_label, coords, format_number))
#
                # # Обработка Format
                # if line[i:i + 6].lower() == 'format' and (i + 6 == len(line) or line[i + 6] in ' ('):
                #     j = i + 6
                #     coords = Coords(Position(self.row, col + i), Position(self.row, j))
                #     self.tokens.append(Token(DomainTag.Keyword, coords, 'FORMAT'))
                #     i = j
                #
                #     while i < len(line) and line[i] == ' ':
                #         i += 1
                #
                #     if i < len(line) and line[i] == '(':
                #         coords = Coords(Position(self.row, col + i), Position(self.row, i + 1))
                #         self.tokens.append(Token(DomainTag.Lbracket, coords, '('))
                #         i += 1
                #         while i < len(line):
                #             if line[i].isdigit():
                #                 start_i = i
                #                 while i < len(line) and line[i].isdigit():
                #                     i += 1
                #                 number = line[start_i:i]
                #
                #
                #                 # Проверяем, следует ли за числом 'h' или 'x'
                #                 if i < len(line) and line[i].lower() in ['x', 'h']:
                #                     spec = line[i].lower()
                #                     coords = Coords(Position(self.row, col + start_i), Position(self.row, i))
                #                     self.tokens.append(Token(DomainTag.Format_specifier, coords, number + spec))
                #                     i += 1
                #
                #                     if spec == 'h':
                #                         start_h = i
                #                         number = int(number)
                #                         while i < len(line) and number != 0:
                #                             i += 1
                #                             number -= 1
                #                         if i > start_h:
                #                             all_symbols = line[start_h:i]
                #                             coords = Coords(Position(self.row, col + start_h), Position(self.row, i))
                #                             self.tokens.append(Token(DomainTag.H_string, coords, all_symbols))
                #
                #
                #                 else:
                #                     coords = Coords(Position(self.row, col + start_i), Position(self.row, i))
                #                     self.tokens.append(Token(DomainTag.Multiplier, coords, number))
                #
                #             elif line[i].lower() in ['i', 'f', 'e']:
                #                 spec_start = i
                #                 i += 1
                #
                #                 while i < len(line) and line[i].isdigit():
                #                     i += 1
                #                 if line[i:i+1] == '.':
                #                     i += 1
                #                     while i < len(line) and line[i].isdigit():
                #                         i += 1
                #                 spec = line[spec_start:i]
                #                 coords = Coords(Position(self.row, col + spec_start), Position(self.row, i))
                #                 self.tokens.append(Token(DomainTag.Format_specifier, coords, spec))
                #             elif line[i] == ',':
                #                 coords = Coords(Position(self.row, col + i), Position(self.row, i + 1))
                #                 self.tokens.append(Token(DomainTag.Comma, coords, ','))
                #                 i+=1
                #
                #             elif line[i] == '(':
                #                 coords = Coords(Position(self.row, col + i), Position(self.row, i + 1))
                #                 self.tokens.append(Token(DomainTag.Lbracket, coords, '('))
                #                 i += 1
                #
                #             elif line[i] == ')':
                #                 coords = Coords(Position(self.row, col + i), Position(self.row, i + 1))
                #                 self.tokens.append(Token(DomainTag.Rbracket, coords, ')'))
                #                 i += 1
                #                 break
                #             else:
                #                 i += 1

#                 #Обработка IF
#                 elif line[i: i + 2].lower() == 'if' and (len(line) == i + 2 or line[i + 2] in [' ', '(',
#                                                                                                '\t']):
#                     j = i + 2
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Keyword, coords, 'if'))
#                     i = j
#
#
#                     while i < len(line) and line[i] in [' ', '\t']:
#                         i += 1
#
#
#                     if i < len(line) and line[i] == '(':
#                         j = i + 1
#                         coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                         self.tokens.append(Token(DomainTag.Lbracket, coords, '('))
#                         i = j
#
#                         count_inner_brackets = 1
#                         while i < len(line) and count_inner_brackets != 0:
#                             if line[i] == '(':
#                                 count_inner_brackets += 1
#                                 j = i + 1
#                                 coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                                 self.tokens.append(Token(DomainTag.Lbracket, coords, '('))
#                                 i = j
#
#                             elif line[i] == ')':
#                                 count_inner_brackets -= 1
#                                 j = i + 1
#                                 coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                                 self.tokens.append(Token(DomainTag.Rbracket, coords, ')'))
#                                 i = j
#                             elif line[i:i + 1].lower() == '=' and (len(line) == i + 1 or line[i + 1] == ' '):
#                                 j = i + 1
#                                 coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                                 self.tokens.append(Token(DomainTag.Assign, coords, '='))
#                                 i = j
#
#                             elif line[i:i + 1].lower() == '+' and (len(line) == i + 1 or line[i + 1] == ' '):
#                                 j = i + 1
#                                 coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                                 self.tokens.append(Token(DomainTag.Addition_operator, coords, '+'))
#                                 i = j
#
#                             elif line[i:i + 1].lower() == '-' and (len(line) == i + 1 or line[i + 1] == ' '):
#                                 j = i + 1
#                                 coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                                 self.tokens.append(Token(DomainTag.Subtraction_operator, coords, '-'))
#                                 i = j
#
#                             elif line[i:i + 1].lower() == '*' and (len(line) == i + 1 or line[i + 1] == ' '):
#                                 j = i + 1
#                                 coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                                 self.tokens.append(Token(DomainTag.Multiplication_operator, coords, '*'))
#                                 i = j
#
#                             elif line[i:i + 1].lower() == '/' and (len(line) == i + 1 or line[i + 1] == ' '):
#                                 j = i + 1
#                                 coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                                 self.tokens.append(Token(DomainTag.Division_operator, coords, '/'))
#                                 i = j
#
#                             elif line[i:i + 2].lower() == '**' and (len(line) == i + 2 or line[i + 2] == ' '):
#                                 j = i + 2
#                                 coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                                 self.tokens.append(Token(DomainTag.Exponentiation_operator, coords, '**'))
#                                 i = j
#
#                             elif line[i].isdigit():
#                                 j = i
#                                 while j < len(line) and line[j].isdigit():
#                                     j += 1
#                                 if j < len(line) and line[j] == '.':
#                                     j += 1
#                                     while j < len(line) and line[j].isdigit():
#                                         j += 1
#                                 if j < len(line) and line[j].lower() == 'e':
#                                     j += 1
#                                     if j < len(line) and (line[j] == '+' or line[j] == '-'):
#                                         j += 1
#                                     while j < len(line) and line[j].isdigit():
#                                         j += 1
#
#                                 number = line[i:j]
#                                 coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                                 if '.' in number or 'e' in number.lower():
#                                     self.tokens.append(Token(DomainTag.Real, coords, number))
#                                 else:
#                                     self.tokens.append(Token(DomainTag.Integer, coords, number))
#                                 i = j
#
#                             elif line[i] == ' ':
#                                 i += 1
#
#
#                             elif line[i].lower().isalpha():
#                                 j = i + 1
#                                 while j < len(line) and line[j].isalnum():
#                                     j += 1
#                                 identifier = line[i:j]
#                                 coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                                 self.tokens.append(
#                                     Token(DomainTag.Identifier, coords, identifier_table.add(identifier)))
#                                 i = j
#
#                     for _ in range(3):
#                         while i < len(line) and line[i] in [' ', '\t']:
#                             i += 1
#
#                         start_label = i
#                         while i < len(line) and line[i].isdigit():
#                             i += 1
#                         label = line[start_label:i]
#                         if label:
#                             coords = Coords(Position(self.row, col + start_label), Position(self.row, i))
#                             self.tokens.append(Token(DomainTag.Label, coords, label))
#
#                         if _ < 2:
#                             while i < len(line) and line[i] in [' ', '\t']:
#                                 i += 1
#                             if i < len(line) and line[i] == ',':
#                                 j = i + 1
#                                 coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                                 self.tokens.append(Token(DomainTag.Comma, coords, ','))
#                                 i = j
#
#
#
#                 #Обработка GOTO
#                 elif line[i:i + 5].lower() == 'go to' and (len(line) == i + 5 or line[i + 5] == ' '):
#                     j = i + 5
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Keyword, coords, 'go to'))
#                     i = j
#
#                     while i < len(line) and line[i] == ' ':
#                         i += 1
#
#                     if i < len(line) and line[i].isdigit():
#                         start_i = i
#                         while i < len(line) and line[i].isdigit():
#                             i += 1
#                         format_number = line[start_i:i]
#                         coords = Coords(Position(self.row, col + start_i), Position(self.row, i))
#                         self.tokens.append(Token(DomainTag.Label, coords, format_number))
#
#
#                 #Обработка Continue
#                 elif line[i:i + 8].lower() == 'continue' and (len(line) == i + 8 or line[i + 8] == ' '):
#                     j = i + 8
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Keyword, coords, 'continue'))
#                     i = j
#                 #Обработка Program
#                 elif line[i:i + 7].lower() == 'program' and (len(line) == i + 7 or line[i + 7] == ' '):
#                     j = i + 7
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Keyword, coords, 'program'))
#                     i = j
#                 #Обработка End
#                 elif line[i:i + 3].lower() == 'end' and (len(line) == i + 3 or line[i + 3] == ' '):
#                     j = i + 3
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Keyword, coords, 'end'))
#                     i = j
#                 #Обработка Dimension
#                 elif line[i:i + 9].lower() == 'dimension' and (len(line) == i + 9 or line[i + 9] == ' '):
#                     j = i + 9
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Keyword, coords, 'dimension'))
#                     i = j
#
#
#
#                 ##Обработка операций
#                 #Обработка '='
#                 elif line[i:i + 1].lower() == '=' and (len(line) == i + 1 or line[i + 1] == ' '):
#                     j = i + 1
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Assign, coords, '='))
#                     i = j
#                 #Обработка '+'
#                 elif line[i:i + 1].lower() == '+' and (len(line) == i + 1 or line[i + 1] == ' '):
#                     j = i + 1
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Addition_operator, coords, '+'))
#                     i = j
#                 #Обработка '-'
#                 elif line[i:i + 1].lower() == '-' and (len(line) == i + 1 or line[i + 1] == ' '):
#                     j = i + 1
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Subtraction_operator, coords, '-'))
#                     i = j
#                 #Обработка '*'
#                 elif line[i:i + 1].lower() == '*' and (len(line) == i + 1 or line[i + 1] == ' '):
#                     j = i + 1
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Multiplication_operator, coords, '*'))
#                     i = j
#                 #Обработка '/'
#                 elif line[i:i + 1].lower() == '/' and (len(line) == i + 1 or line[i + 1] == ' '):
#                     j = i + 1
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Division_operator, coords, '/'))
#                     i = j
#                 #Обработка '**'
#                 elif line[i:i + 2].lower() == '**' and (len(line) == i + 2 or line[i + 2] == ' '):
#                     j = i + 2
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Exponentiation_operator, coords, '**'))
#                     i = j
#
#
#
#                 ##Обработка лексических знаков
#                 #Обработка ','
#                 elif line[i:i + 1].lower() == ',' and (len(line) == i + 1 or line[i + 1] == ' '):
#                     j = i + 1
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Comma, coords, ','))
#                     i = j
#
#                 #Обработка '('
#                 elif line[i:i + 1].lower() == '(':
#                     j = i + 1
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Lbracket, coords, '('))
#                     i = j
#
#                 #Обработка ')'
#                 elif line[i:i + 1].lower() == ')':
#                     j = i + 1
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     self.tokens.append(Token(DomainTag.Rbracket, coords, ')'))
#                     i = j
#
#                 ##Обработка чисел и меток
#                 elif line[i].isdigit():
#                     j = i
#                     while j < len(line) and line[j].isdigit():
#                         j += 1
#                     if j < len(line) and line[j] == '.':
#                         j += 1
#                         while j < len(line) and line[j].isdigit():
#                             j += 1
#                     if j < len(line) and line[j].lower() == 'e':
#                         j += 1
#                         if j < len(line) and (line[j] == '+' or line[j] == '-'):
#                             j += 1
#                         while j < len(line) and line[j].isdigit():
#                             j += 1
#
#                     number = line[i:j]
#                     coords = Coords(Position(self.row, col + i), Position(self.row, j))
#                     if i < 5:
#                         self.tokens.append(Token(DomainTag.Label, coords, number))
#                     else:
#                         if '.' in number or 'e' in number.lower():
#                             self.tokens.append(Token(DomainTag.Real, coords, number))
#                         else:
#                             self.tokens.append(Token(DomainTag.Integer, coords, number))
#                     i = j