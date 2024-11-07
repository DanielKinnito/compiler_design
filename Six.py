import re

class Token:
    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def __str__(self):
        return f"| {self.token_type:<18} | {self.value:<10} |"


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
            elif self.current_char.isdigit():
                tokens.append(self.parse_number())
            elif self.current_char.isalpha():
                tokens.append(self.parse_keyword())
            elif self.current_char in "+-*/":
                tokens.append(Token(self.current_char, self.current_char))
                self.advance()
            elif self.current_char == "=":
                tokens.append(Token("ASSIGNMENT", "="))
                self.advance()
            elif self.current_char == ";":
                tokens.append(Token("SEMICOLON", ";"))
                self.advance()
            elif self.current_char == "{":
                tokens.append(Token("LEFT_BRACE", "{"))
                self.advance()
            elif self.current_char == "}":
                tokens.append(Token("RIGHT_BRACE", "}"))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token("LEFT_PAREN", "("))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token("RIGHT_PAREN", ")"))
                self.advance()
            elif self.current_char == ",":
                tokens.append(Token("COMMA", ","))
                self.advance()
            else:
                raise Exception(f"Invalid character: {self.current_char}")

        return tokens

    def parse_number(self):
        result = ""
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            result += self.current_char
            self.advance()

        if '.' in result:
            return Token("NUMBER", float(result))
        else:
            return Token("NUMBER", int(result))

    def parse_keyword(self):
        result = ""
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        if result in ["int", "float", "double", "char", "void"]:
            return Token("TYPE", result)
        elif result == "return":
            return Token("RETURN", result)
        elif result == "if":
            return Token("IF", result)
        elif result == "else":
            return Token("ELSE", result)
        elif result == "while":
            return Token("WHILE", result)
        elif result == "for":
            return Token("FOR", result)
        else:
            return Token("IDENTIFIER", result)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = self.tokens.pop(0) if tokens else None
        self.variables = {}

    def error(self):
        print("Invalid syntax")
        # exit(1)

    def eat(self, token_type):
        if self.current_token.token_type == token_type:
            self.current_token = self.tokens.pop(0) if self.tokens else None
        else:
            self.error()

    def factor(self):
        if self.current_token.token_type == "NUMBER":
            result = self.current_token.value
            self.eat("NUMBER")
            return result
        elif self.current_token.token_type == "IDENTIFIER":
            result = self.current_token.value
            self.eat("IDENTIFIER")
            return result
        elif self.current_token.token_type == "LEFT_PAREN":
            self.eat("LEFT_PAREN")
            result = self.expr()
            self.eat("RIGHT_PAREN")
            return result
        else:
            self.error()

    def term(self):
        result = self.factor()

        while self.current_token and self.current_token.token_type in ("PLUS", "MINUS", "MULTIPLY", "DIVIDE"):
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
            elif self.current_token.token_type == "PLUS":
                self.eat("PLUS")
                result += self.factor()
            elif self.current_token.token_type == "MINUS":
                self.eat("MINUS")
                result -= self.factor()

        return result

    def expr(self):
        result = self.term()

        while self.current_token and self.current_token.token_type in ("+", "-"):
            if self.current_token.token_type == "+":
                self.eat("+")
                result += self.term()
            elif self.current_token.token_type == "-":
                self.eat("-")
                result -= self.term()

        return result

    def block(self):
        if self.current_token.token_type == "LEFT_BRACE":
            self.eat("LEFT_BRACE")
            while self.current_token and self.current_token.token_type != "RIGHT_BRACE":
                result = self.statement()  # Capture the return value of statement
                # Handle the return value if needed
            self.eat("RIGHT_BRACE")
        else:
            self.error()

    def function_declaration(self):
        self.eat("TYPE")  # Return type
        func_name = self.current_token.value
        self.eat("IDENTIFIER")
        self.eat("LEFT_PAREN")

        while self.current_token and self.current_token.token_type != "RIGHT_PAREN":
            self.parameter()

            if self.current_token and self.current_token.token_type == "COMMA":
                self.eat("COMMA")
        self.eat("RIGHT_PAREN")

        if self.current_token and self.current_token.token_type == "LEFT_BRACE":
            self.eat("LEFT_BRACE")
            while self.current_token and self.current_token.token_type != "RIGHT_BRACE":
                self.statement()
            self.eat("RIGHT_BRACE")
        else:
            self.eat("SEMICOLON")

    def parameter(self):
        self.eat("TYPE")
        self.eat("IDENTIFIER")

        while self.current_token and self.current_token.token_type == "COMMA":
            self.eat("COMMA")
            self.eat("TYPE")
            self.eat("IDENTIFIER")

    def statement(self):
        if self.current_token.token_type == "RETURN":
            self.eat("RETURN")
            result = self.expr()
            self.eat("SEMICOLON")
            return result
        elif self.current_token.token_type in ["TYPE"]:
            self.function_declaration()
        else:
            self.variable_declaration()


def main():
    input_program = """
    int add(int a, int b) {
        return a + b;
    }

    int main() {
        int x = 5, y = 3;
        int result = add(x, y);
        return result;
    }
    """

    # Lexical Analysis
    lexer = Lexer(input_program)
    tokens = lexer.lex()

    # Display Token Table
    print("\nToken Table:")
    print("| Type              | Value      |")
    print("|-------------------|------------|")
    for token in tokens:
        print(token)

    parser = Parser(tokens.copy())
    parser.block()  # Start parsing from the block
    print("\nParsing completed successfully.")


if __name__ == "__main__":
    main()