import parser_edsl as pe
import abc
from dataclasses import dataclass
from copy import deepcopy



class SemanticError(pe.Error):
    def __init__(self, pos, message):
        self.pos = pos
        self.__message = message

    @property
    def message(self):
        return self.__message


class IdentifierNameLengthError(SemanticError):
    def __init__(self, pos, identifier):
        self.pos = pos
        self.identifier = identifier

    @property
    def message(self):
        return f"Длина идентификатора:{self.pos}, больше 6 символов"


class UndefinedSymbolError(SemanticError):
    def __init__(self, pos, identifier):
        self.pos = pos
        self.identifier = identifier

    @property
    def message(self):
        return f"Идентификатор {self.identifier} не определен"

class LabelInexistantError(SemanticError):
    def __init__(self, pos, label):
        self.pos = pos
        self.label = label

    @property
    def message(self):
        return f"Метки с номером:{self.label}, не существует"

class LabelRedefinitionError(SemanticError):
    def __init__(self, pos, label):
        self.pos = pos
        self.label = label

    @property
    def message(self):
        return f"Метки с номером:{self.label}, не существует"


class FormatWithoutLabelError(SemanticError):
    def __init__(self, pos, label):
        self.pos = pos
        self.label = label

    @property
    def message(self):
        return f"у Format:{self.label} нет метки, не существует"
