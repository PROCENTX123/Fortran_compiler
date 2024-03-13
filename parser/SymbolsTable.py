class SymbolTable:
    def __init__(self, parent=None):
        pass
        # self.parent = parent
        # self.symbols = []
        # self.child_tables = []



    def lookup(self, symbol):
        pass
        # return self.symbols.get(symbol, self.parent.lookup(symbol) if self.parent else None)



    def add(self, symbol, type):
        pass
        # if symbol in self.symbols:
        #     raise ValueError(f"Символ {symbol} уже определен.")
        # self.symbols.append(Symbol(symbol, type))


    def new_table(self):
        pass
        # result = SymbolTable(self)
        # self.child_tables.append(result)
        # return result

    def print_symbols(self):
        pass
        # for symbol in self.symbols():
        #     print(f"{symbol.name}: {symbol.type}")
        # if self.parent:
        #     self.parent.print_symbols()

class Symbol:
    def __init__(self, value, type):
        pass
        # self.value = value
        # self.type = type
