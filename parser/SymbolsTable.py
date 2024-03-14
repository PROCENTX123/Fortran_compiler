class SymbolTable:
    def __init__(self, parent=None):

        self.parent = parent
        self.symbols = []
        self.child_tables = []
        self.program_functions = []
        self.suspicious_symbols = []

    def swap_type(self, symbol, new_type):
        for i in range(len(self.symbols)):
            if symbol.name == self.symbols[i].value:
                self.symbols[i].type = new_type

    def lookup(self, symbol):
        for i in range(len(self.symbols)):
            if symbol == self.symbols[i].value:
                return self.symbols[i]

        if self.parent:
            return self.parent.lookup(symbol)

        return None

    def add(self, symbol, type, syspicious=False):
        if symbol in self.symbols:
            raise ValueError(f"Символ {symbol} уже определен.")
        self.symbols.append(Symbol(symbol, type))
        if syspicious == True:
            self.suspicious_symbols.append(Symbol(symbol, type))


    def new_table(self):
        result = SymbolTable(self)
        self.child_tables.append(result)
        return result

    def print_symbols(self):
        for symbol in self.symbols():
            print(f"{symbol.name}: {symbol.type}")
        if self.parent:
            self.parent.print_symbols()

class Symbol:
    def __init__(self, value, type):
        self.value = value
        self.type = type
