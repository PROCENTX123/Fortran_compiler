from .errors import *

def remove_comments(filename):
    with open(filename, 'r') as file:
        lines = [line[:72].rstrip() + '\n' if len(line) > 72 else line for line in file]

    with open(filename, 'w') as file:
        file.writelines(lines)


def gluing_strings(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    new_lines = []
    for i in range(len(lines)):
        if i > 0 and len(lines[i]) > 5 and lines[i][5] not in [' ', '\n', '\t']:
            new_lines[-1] = new_lines[-1].rstrip('\n') + lines[i][6:72] + '\n'
        else:
            new_lines.append(lines[i][:72])
    with open(filename, 'w') as file:
        file.writelines(new_lines)

    with open(filename, 'w') as file:
        file.writelines(new_lines)


def create_tuples_from_lines(filename):
    tuples_list = []
    defined_labels = []
    with open(filename, 'r') as file:
        idx = 0
        for line in file:
            idx += 1
            if line[6:72] == '':
                continue
            number = line[:5].strip()
            text = line[6:72].strip()
            label = None if not number else int(number)
            if label and label in defined_labels:
                raise LabelRedefinitionError(pe.Position(0, idx, 1), label)
            if "format" in text and not label and "=" not in text:
                raise FormatWithoutLabelError(pe.Position(0, idx, 1), text)
            if not ("format" in text and label):
                text = text.replace(' ', '')
            tuples_list.append((label, text))
            defined_labels.append(label)
    return tuples_list


def create_preprocessing(filename):
    remove_comments(filename)
    gluing_strings(filename)
    tuples = create_tuples_from_lines(filename)
    return tuples
