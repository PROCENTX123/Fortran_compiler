class SymbolTable:
    def __init__(self, parent=None):
        self.parent = parent
        self.tables = []

    def lookup(self, symbol):
        pass

    def add(self, symbol):
        pass

    def new_table(self):
        result = SymbolTable(self)
        self.tables.append(result)
        return result