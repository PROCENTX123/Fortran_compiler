from lexer.check_lexer import make_lexer
from parser.AST import Program
from pprint import pprint


if __name__ == "__main__":
    unique_labels, pair_lable_operator = make_lexer('test1.txt')
    tree, format_labels = Program.parse(pair_lable_operator)
    _, symbol_table = tree.check()
    pprint(tree)
    print("NICE")

