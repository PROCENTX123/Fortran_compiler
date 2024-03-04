from typing import Any, Optional
import parser_edsl as pe
from .Domaintag import DomainTag

class Position:
    def __init__(self, line: int, pos: int):
        self.line = line
        self.pos = pos

    def position(self):
        return pe.Position(0, self.line, self.pos)

    def __str__(self) -> str:
        return f'({self.line},{self.pos})'

class Coords:
    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end

    def __str__(self) -> str:
        return f'{self.start}-{self.end}'

class Token:
    def __init__(self, tag: DomainTag, coords: Coords, attrib: Optional[Any] = None):
        self.tag = tag
        self.coords = coords
        self.attrib = attrib

    def __str__(self) -> str:
        attrib_str = f' [{self.attrib}]' if self.attrib is not None else ''
        return f'{self.tag.value} {self.coords}{attrib_str}'