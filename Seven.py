# lexer.py
from collections import namedtuple

Token = namedtuple('Token', ['type', 'value', 'pos_start', 'pos_end'])

TT_INT = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'
TT_EOF = 'EOF'

DIGITS = '0123456789'


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos += 1

        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def make_tokens(self):
        tokens = []

        while self.current_char is not None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, '+'))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, '-'))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, '*'))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, '/'))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, '('))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, ')'))
                self.advance()
            else:
                pos_start = self.pos
                char = self.current_char
                self.advance()
                return [], Exception(f"Illegal character '{char}'", pos_start, self.pos)

        tokens.append(Token(TT_EOF, None))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos

        while self.current_char is not None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
            num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)


# parser.py
class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error:
                self.error = res.error
            return res.node

        return res

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        self.error = error
        return self


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.advance()

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token

    def parse(self):
        res = self.expr()
        if not res.error and self.current_token.type != TT_EOF:
            return res.failure(Exception('Expected '+TT_EOF, self.current_token.pos_start, self.current_token.pos_end))
        return res

    def factor(self):
        res = ParseResult()
        token = self.current_token

        if token.type in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(OperationNode(factor, token))

        elif token.type in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(token.value))

        elif token.type == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_token.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(Exception("Expected ')'", self.current_token.pos_start, self.current_token.pos_end))

        return res.failure(Exception("Expected int, float, '+', '-', or '('", token.pos_start, token.pos_end))

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TTDIV))

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error:
            return res

        while self.current_token.type in ops:
            op_token = self.current_token
            res.register(self.advance())
            right = res.register(func())
            if res.error:
                return res
            left = OperationNode(left, op_token, right)

        return res.success(left)


class NumberNode:
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.value}'


class OperationNode:
    def __init__(self, left, op, right=None):
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self):
        return f'({self.left}, {self.op}, {self.right})'


# main.py
def run(text):
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    parser = Parser(tokens)
    ast = parser.parse()

    return ast, ast.error


def string_with_arrows(text, pos_start, pos_end):
    result = ''

    # Calculate indices
    idx_start = max(text.rfind('\n', 0, pos_start.idx), 0)
    idx_end = text.find('\n', idx_start + 1)
    if idx_end < 0:
        idx_end = len(text)

    # Generate each line
    line_count = pos_end.ln - pos_start.ln + 1
    for i in range(line_count):
        # Calculate line columns
        line = text[idx_start:idx_end]
        col_start = pos_start.col if i == 0 else 0
        col_end = pos_end.col if i == line_count - 1 else len(line) - 1

        # Append to result
        result += line + '\n'
        result += ' ' * col_start + '^' * (col_end - col_start)

        # Re-calculate indices
        idx_start = idx_end
        idx_end = text.find('\n', idx_start + 1)
        if idx_end < 0:
            idx_end = len(text)

    return result.replace('\t', '')


# Example usage
text = input("Enter an expression: ")
ast, error = run(text)

if ast:
    print(ast)
else:
    pos_start = ast.pos_start if error.pos_start is None else error.pos_start
    pos_end = ast.pos_end if error.pos_end is None else error.pos_end
    print(f'Error: {error}\n\n{string_with_arrows(text, pos_start, pos_end)}')