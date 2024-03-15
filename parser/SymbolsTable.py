class SymbolTable:
    def __init__(self):
        self.symbols = []
        self.program_functions = []
        self.suspicious_symbols = []
        self.labels = {}
        self.formats = {}

    def lookup(self, symbol):
        for i in range(len(self.symbols)):
            if symbol == self.symbols[i].value:
                return self.symbols[i]

        return None

    def add(self, symbol, type, suspicious=False):
        if symbol in self.symbols:
            raise ValueError(f"Символ {symbol} уже определен.")
        self.symbols.append(Symbol(symbol, type))
        if suspicious:
            self.suspicious_symbols.append(Symbol(symbol, type))

    def print_symbols(self):
        for symbol in self.symbols:
            print(f"{symbol.name}: {symbol.type}")


class Symbol:
    def __init__(self, value, type):
        self.value = value
        self.type = type
