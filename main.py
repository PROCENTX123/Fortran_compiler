from lexer.check_lexer import make_lexer
from parser.AST import Program
from pprint import pprint


if __name__ == "__main__":
    tokens, unique_labels, analyzer = make_lexer('test1.txt')
    tree = Program.parse(analyzer)
    tree.check(unique_labels)
    pprint(tree)
    print("NICE")

