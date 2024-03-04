import parser_edsl as pe
import re

def create_terminal():
    #regular
    INTEGER = pe.Terminal('INTEGER', '[0-9]+', int)
    REAL = pe.Terminal('REAL', '[0-9]+(\\.[0-9]*)?(e[-+]?[0-9]+)?', float)
    ALL_SYMBOLS = pe.Terminal('ALL_SYMBOLS', r'[0-9A-Za-zА-Яа-яёЁ\s!\"#$%&\'()*+,\-./:;<=>?@\[\]^_`{|}~]', str.upper)
    POSITIVE = pe.Terminal('POSITIVE', '[1-9][0-9]*', int)
    STRING = pe.Terminal('STRING', '[A-Za-z][A-Za-z0-9]*', str.upper)


    #key_word
    PLUS = pe.Terminal('+', '+', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    MINUS = pe.Terminal('-', '-', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    MUL = pe.Terminal('*', '*', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    DIV = pe.Terminal('/', '/', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    EXP = pe.Terminal('**', '**', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    READ = pe.Terminal('read', 'read', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    PRINT = pe.Terminal('print', 'print', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    FORMAT = pe.Terminal('format', 'format', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    GO_TO = pe.Terminal('go to', 'go to', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    IF = pe.Terminal('if', 'if', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    CONTINUE = pe.Terminal('continue', 'continue', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    DIMENSION = pe.Terminal('dimension', 'dimension', lambda name: None, re_flags=re.IGNORECASE,priority=10)
    ASSIGMENT = pe.Terminal('=', '=', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    COMMA = pe.Terminal(',', ',', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    LBRACKET = pe.Terminal('(', '(', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    RBRACKET = pe.Terminal(')', ')', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    END = pe.Terminal('end', 'end', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    POINT = pe.Terminal('.', '.', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    PROGRAM = pe.Terminal('program', 'program', lambda name: None, re_flags=re.IGNORECASE, priority=10)
    return INTEGER, REAL, ALL_SYMBOLS, POSITIVE, STRING, PLUS, MINUS, MUL, DIV, EXP, READ, PRINT, FORMAT, GO_TO,\
        IF, CONTINUE, DIMENSION, ASSIGMENT, COMMA, LBRACKET, RBRACKET, END, POINT, PROGRAM
