import re

class Token:
    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def __str__(self):
        return f"| {self.token_type:<18}| {self.value:<11}|"


class Lexer:
    def __init__(self, input_text):
        self.input_text = input_text
        self.position = 0
        self.current_char = self.input_text[self.position]

    def advance(self):
        self.position += 1
        if self.position < len(self.input_text):
            self.current_char = self.input_text[self.position]
        else:
            self.current_char = None

    def lex(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char.isspace():
                self.advance()
            elif self.current_char.isdigit() or self.current_char == '.':
                tokens.append(self.parse_number())
            elif self.current_char == "+":
                tokens.append(Token("PLUS", self.current_char))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token("MINUS", self.current_char))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token("MULTIPLY", self.current_char))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token("DIVIDE", self.current_char))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token("LPAREN", self.current_char))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token("RPAREN", self.current_char))
                self.advance()
            else:
                raise Exception(f"Invalid character: {self.current_char}")

        return tokens

    def parse_number(self):
        result = ""
        decimal_count = 0

        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char

            if self.current_char == '.':
                decimal_count += 1
                if decimal_count > 1:
                    raise Exception("Invalid number")

            self.advance()

        if '.' in result:
            return Token("FLOAT", float(result))
        else:
            return Token("INT", int(result))


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = self.tokens.pop(0) if tokens else None

    def error(self):
        print("Invalid syntax")
        exit(1)

    def eat(self, token_type):
        if self.current_token.token_type == token_type:
            self.current_token = self.tokens.pop(0) if self.tokens else None
        else:
            self.error()

    def factor(self):
        if self.current_token.token_type == "INT" or self.current_token.token_type == "FLOAT":
            result = self.current_token.value
            self.eat(self.current_token.token_type)
            return result
        elif self.current_token.token_type == "LPAREN":
            self.eat("LPAREN")
            result = self.expr()
            self.eat("RPAREN")
            return result
        else:
            self.error()

    def term(self):
        result = self.factor()

        while self.current_token and self.current_token.token_type in ("MULTIPLY", "DIVIDE"):
            if self.current_token.token_type == "MULTIPLY":
                self.eat("MULTIPLY")
                result *= self.factor()
            elif self.current_token.token_type == "DIVIDE":
                self.eat("DIVIDE")
                divisor = self.factor()
                if divisor != 0:
                    result /= divisor
                else:
                    raise Exception("Division by zero")

        return result

    def expr(self):
        result = self.term()

        while self.current_token and self.current_token.token_type in ("PLUS", "MINUS"):
            if self.current_token.token_type == "PLUS":
                self.eat("PLUS")
                result += self.term()
            elif self.current_token.token_type == "MINUS":
                self.eat("MINUS")
                result -= self.term()

        return result


def main():
    input_expression = "2.5 + (3 - 1.2) * 5.8"

    # Lexical Analysis
    lexer = Lexer(input_expression)
    tokens = lexer.lex()

    # Display Token Table
    print("\nToken Table:")
    print("| Type              | Value      |")
    print("|-------------------|------------|")
    for token in tokens:
        print(token)

    # Parsing and Evaluation
    parser = Parser(tokens.copy())
    result = parser.expr()
    print("\nOutput:", result)


if __name__ == "__main__":
    main()