from .lexer import LexicalAnalyzer
from .preprocessing import create_preprocessing

def make_lexer(namefile):
    pair_lable_operator = create_preprocessing(namefile)
    unique_labels = []
    # пример того как работает preprocessing
    for tuple in pair_lable_operator:
        if tuple[0]:
            unique_labels.append(tuple[0])
        # print(tuple)

    analyzer = LexicalAnalyzer(pair_lable_operator)
    tokens = analyzer.tokens()

    # пример того как работает лексический анализатор
    # for token in tokens:
    #     print(token)

    return tokens, unique_labels, analyzer
