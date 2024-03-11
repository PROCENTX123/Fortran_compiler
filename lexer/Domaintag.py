from enum import Enum

class DomainTag(Enum):
    #типичные теги
    Identifier = 'Identifier'
    Error = 'Error'

    #теги для чисел
    Integer = 'Integer'
    Real = 'Real'

    EOF = 'EOF'

    #дополнения к format
    Format_specifier = 'Format_specifier'
    Format_label = 'Format_label' #ищем это у read и print
    H_string = 'H_string'
    Multiplier = 'Multiplier'

    #лексические знаки
    Comma = 'Comma'
    Lbracket = 'Lbracket'
    Rbracket = 'Rbracket'

    #арифметические операторы
    Assign = 'Assign'
    Addition_operator = 'Addition_operator'
    Subtraction_operator = 'Subtraction_operator'
    Multiplication_operator = 'Multiplication_operator'
    Division_operator = 'Division_operator'
    Exponentiation_operator = 'Exponentiation_operator'

