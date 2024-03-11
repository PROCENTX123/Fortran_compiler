from typing import Any, Optional
import parser_edsl as pe
from .Domaintag import DomainTag


class Token:
    def __init__(self, tag: DomainTag, attrib: Optional[Any] = None):
        self.tag = tag
        self.attrib = attrib

    def __str__(self) -> str:
        attrib_str = f' [{self.attrib}]' if self.attrib is not None else ''
        return f'{self.tag.value} {attrib_str}'