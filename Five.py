import re

class Node:
    def __init__(self, value):
        self.value = value
        self.children = []

    def __repr__(self, level=0):
        ret = "\t" * level + repr(self.value) + "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

def lexer(program):
    token_types = {
        "KEYWORD": {"int", "float", "char", "double", "if", "else", "while", "for", "switch", "return"},
        "IDENTIFIER": r'[a-zA-Z_]\w*',
        "OPERATOR": r'[-+*/()=]',
        "INTEGER": r'\d+',
        "FLOAT": r'\d+\.\d+',
        "SPECIAL_CHARACTER": r'[{};,]',
        "WHITESPACE": r'\s+',
    }

    tokens = []
    i = 0

    while i < len(program):
        match = None

        for type, pattern in token_types.items():
            if isinstance(pattern, set):
                values = pattern
                regex = re.compile(fr'\b(?:{"|".join(re.escape(v) for v in values)})\b')
            else:
                regex = re.compile(pattern)

            match = regex.match(program, i)
            if match:
                value = match.group(0)
                tokens.append(Token(type, value))
                i = match.end()
                break

        if not match:
            raise ValueError(f"Invalid token at position {i}: {program[i:i+10]}...")

    return tokens

def parse_program(tokens):
    root = Node("Program")
    current_node = root
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token.type == 'KEYWORD' and token.value in {'int', 'float', 'char', 'double'}:
            declaration_node = Node(f"Variable Declaration: {token.value}")
            current_node.children.append(declaration_node)

            i += 1  # Move to the next token
            if i < len(tokens) and tokens[i].type == 'IDENTIFIER':
                variable_node = Node(f"Identifier: {tokens[i].value}")
                declaration_node.children.append(variable_node)

                i += 1  # Move to the next token
                if i < len(tokens) and tokens[i].type == 'OPERATOR' and tokens[i].value == '=':
                    assignment_node = Node("Assignment")
                    declaration_node.children.append(assignment_node)

                    i += 1  # Move to the next token
                    expression_node = parse_expression(tokens, i)
                    assignment_node.children.append(expression_node)
                else:
                    raise ValueError(f"Invalid variable declaration: {tokens[i:i+3]}")
            else:
                raise ValueError(f"Invalid variable declaration: {tokens[i:i+2]}")

        i += 1

    return root

def parse_expression(tokens, start):
    # Placeholder for expression parsing
    expression_node = Node("Expression")
    current_node = expression_node

    i = start
    while i < len(tokens) and tokens[i].type != 'SPECIAL_CHARACTER' and tokens[i].value != ';':
        token_node = Node(f"{tokens[i].type}: {tokens[i].value}")
        current_node.children.append(token_node)
        i += 1

    return expression_node

def interpret(node):
    # Placeholder for interpretation
    if node.value.startswith("Variable Declaration"):
        variable_name = node.children[1].value.split(":")[1].strip()
        print(f"Variable {variable_name} declared.")
    return None

if __name__ == "__main__":
    program = input("Enter a program statement: ")

    # Lexical analysis
    tokens = lexer(program)

    # Parsing
    try:
        program_tree = parse_program(tokens)
        print("\nParsing Tree:")
        display_parse_tree(program_tree)

        # Interpretation
        interpret(program_tree)

    except ValueError as e:
        print("Error:", e)

    # Display token table (excluding whitespaces)
    print("\nToken Table:")
    print("| Type              | Value      |")
    print("|-------------------|------------|")
    for token in tokens:
        if token.type != 'WHITESPACE':
            print(f"| {token.type:<17} | {token.value:<10} |")

    # Count and display the number of whitespaces
    num_whitespaces = sum(1 for token in tokens if token.type == 'WHITESPACE')
    print(f"\nNumber of Whitespaces: {num_whitespaces}")
