from lexer.check_lexer import make_lexer
from parser.AST import Program
from pprint import pprint


if __name__ == "__main__":
    unique_labels, pair_lable_operator = make_lexer('test.txt')
    tree = Program.parse(pair_lable_operator)
    tree.check(unique_labels)
    pprint(tree)
    print("NICE")

