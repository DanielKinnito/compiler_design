import re

# Token types
TOKEN_TYPES = {
    "KEYWORD": {"int", "float", "if", "else", "while", "for", "switch", "return"},
    "IDENTIFIER": r'[a-zA-Z_]\w*',
    "OPERATOR": r'[-+*/()]',
    "INTEGER": r'\d+',
    "FLOAT": r'\d+\.\d+',
    "WHITESPACE": r'\s+',
}

# Token class
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"


# Lexer function
def lexer(program):
    tokens = []
    for type, pattern in TOKEN_TYPES.items():
        if isinstance(pattern, set):
            values = pattern
            regex = re.compile(fr'\b(?:{"|".join(re.escape(v) for v in values)})\b')
        else:
            regex = re.compile(pattern)
        matches = regex.finditer(program)
        for match in matches:
            value = match.group(0)
            tokens.append(Token(type, value))
    return tokens


# Parser function (for simplicity, handles only basic arithmetic expressions)
# Updated Parser function
def parse(tokens):
    stack = []
    operators = {'+', '-', '*', '/'}

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token.type == 'KEYWORD' and token.value in {'int', 'float', 'char', 'double'}:
            # Function declaration
            if i + 2 < len(tokens) and tokens[i + 1].type == 'IDENTIFIER' and tokens[i + 2].type == 'OPERATOR' and tokens[i + 2].value == '(':
                i += 3  # Skip the identifier and '('
                while i < len(tokens) and not (tokens[i].type == 'OPERATOR' and tokens[i].value == ')'):
                    i += 1
                i += 1  # Skip the ')'
                if i < len(tokens) and tokens[i].type == 'OPERATOR' and tokens[i].value == '{':
                    i += 1  # Skip the '{'
                    while i < len(tokens) and not (tokens[i].type == 'OPERATOR' and tokens[i].value == '}'):
                        i += 1
                    i += 1  # Skip the '}'
                else:
                    raise ValueError(f"Invalid function declaration: {tokens[i:i+3]}")
            else:
                raise ValueError(f"Invalid function declaration: {tokens[i:i+3]}")

        elif token.type == 'KEYWORD' and token.value == 'return':
            # Return statement
            i += 1
            while i < len(tokens) and not (tokens[i].type == 'OPERATOR' and tokens[i].value == ';'):
                i += 1
            i += 1  # Skip the ';'

        elif token.type == 'IDENTIFIER':
            stack.append(token.value)

        elif token.type == 'OPERATOR' and token.value in operators:
            if len(stack) >= 2:
                b = stack.pop()
                a = stack.pop()
                if token.value == '+':
                    stack.append(a + b)
                elif token.value == '-':
                    stack.append(a - b)
                elif token.value == '*':
                    stack.append(a * b)
                elif token.value == '/':
                    stack.append(a / b)
            else:
                raise ValueError(f"Invalid expression: {tokens}")

        i += 1

    if len(stack) == 1:
        return stack[0]
    else:
        raise ValueError(f"Invalid expression: {tokens}")


# Main program
if __name__ == "__main__":
    program = input("Enter a program statement: ")

    # Lexical analysis
    tokens = lexer(program)

    # Parsing and Execution
    try:
        result = parse(tokens)
        print("Result:", result)
    except ValueError as e:
        print("Error:", e)

    # Display token table (excluding whitespaces)
    print("\nToken Table:")
    print("| Type       | Value      |")
    print("|------------|------------|")
    for token in tokens:
        if token.type != 'WHITESPACE':
            print(f"| {token.type:<10} | {token.value:<10} |")

    # Count and display the number of whitespaces
    num_whitespaces = sum(1 for token in tokens if token.type == 'WHITESPACE')
    print(f"\nNumber of Whitespaces: {num_whitespaces}")
