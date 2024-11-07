import tkinter as tk
from tkinter import Label, Button, scrolledtext

class Token:
    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def __str__(self):
        return f"| {self.token_type:<18} | {str(self.value):<10} |"

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
        errors = []
        while self.current_char is not None:
            if self.current_char.isspace():
                self.advance()
            elif self.current_char.isdigit():
                tokens.append(self.parse_number())
            elif self.current_char.isalpha():
                tokens.append(self.parse_keyword())
            elif self.current_char in "+-*/%":
                tokens.append(Token(self.current_char, self.current_char))
                self.advance()
            elif self.current_char == "=":
                tokens.append(Token("ASSIGNMENT", "="))
                self.advance()
            elif self.current_char == ";":
                tokens.append(Token("SEMICOLON", ";"))
                self.advance()
            elif self.current_char in "{}()":
                tokens.append(Token(self.current_char, self.current_char))
                self.advance()
            elif self.current_char == ",":
                tokens.append(Token("COMMA", ","))
                self.advance()
            else:
                errors.append(f"Invalid character: {self.current_char}")
                self.advance()

        return tokens, errors

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

        keywords = {
            "int": "TYPE", "float": "TYPE", "double": "TYPE", "char": "TYPE", "void": "TYPE",
            "return": "RETURN", "if": "IF", "else": "ELSE", "while": "WHILE", "for": "FOR"
        }

        return Token(keywords.get(result, "IDENTIFIER"), result)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = self.tokens.pop(0) if tokens else None
        self.variables = {}

    def error(self, message="Invalid syntax"):
        raise Exception(message)

    def eat(self, token_type):
        while self.current_token and self.current_token.token_type == "ASSIGNMENT" and token_type == "SEMICOLON":
            self.current_token = self.tokens.pop(0) if self.tokens else None

        if self.current_token and self.current_token.token_type == token_type:
            self.current_token = self.tokens.pop(0) if self.tokens else None
        elif token_type == "SEMICOLON" and (
                self.current_token.token_type == "IDENTIFIER" or
                self.current_token.token_type == "NUMBER" or
                self.current_token.token_type in ("+", "-", "*", "/") or
                (self.current_token.token_type == "ASSIGNMENT" and self.tokens[0].token_type == "%")):
            return
        else:
            self.error(f"Expected {token_type}, but got {self.current_token.token_type}")

    def factor(self):
        if self.current_token.token_type == "NUMBER":
            result = self.current_token.value
            self.eat("NUMBER")
            return result
        elif self.current_token.token_type == "IDENTIFIER":
            result = self.variables.get(self.current_token.value)
            self.eat("IDENTIFIER")
            return result
        elif self.current_token.token_type == "LEFT_PAREN":
            self.eat("LEFT_PAREN")
            result = self.expr()
            self.eat("RIGHT_PAREN")
            return result
        elif self.current_token.token_type == "TYPE":
            result = self.current_token.value
            self.eat("TYPE")
            return result
        else:
            self.error(f"Unexpected token: {self.current_token.token_type}")

    def term(self):
        result = self.factor()

        while self.current_token and self.current_token.token_type in ("*", "/"):
            operator = self.current_token.token_type
            self.eat(operator)
            operand = self.factor()

            if operator == "*":
                result *= operand
            elif operator == "/":
                if operand != 0:
                    result /= operand
                else:
                    self.error("Division by zero")

        return result

    def expr(self):
        result = self.term()

        while self.current_token and self.current_token.token_type in ("+", "-"):
            operator = self.current_token.token_type
            self.eat(operator)
            operand = self.term()

            if operator == "+":
                result += operand
            elif operator == "-":
                result -= operand

        return result

    def statement(self):
        if self.current_token.token_type == "SEMICOLON":
            self.eat("SEMICOLON")
        elif self.current_token.token_type == "TYPE":
            self.variable_declaration()
        else:
            result = self.expr()
            var_name = self.current_token.value
            self.variables[var_name] = result
            self.eat("IDENTIFIER")
            self.eat("SEMICOLON")

    def block(self):
        if self.current_token.token_type == "LEFT_BRACE":
            self.eat("LEFT_BRACE")
            while self.current_token and self.current_token.token_type != "RIGHT_BRACE":
                self.statement()
            self.eat("RIGHT_BRACE")
        elif self.current_token.token_type == "SEMICOLON":
            self.eat("SEMICOLON")
        else:
            self.error(f"Expected LEFT_BRACE or SEMICOLON, but got {self.current_token.token_type}")

    def variable_declaration(self):
        data_type = self.current_token.value
        self.eat("TYPE")
        var_name = self.current_token.value
        self.eat("IDENTIFIER")

        if self.current_token.token_type == "ASSIGNMENT":
            self.eat("ASSIGNMENT")
            self.variables[var_name] = self.expr()
            self.eat("SEMICOLON")
        elif self.current_token.token_type == "SEMICOLON":
            self.variables[var_name] = None  # Default value for the variable
            self.eat("SEMICOLON")
        else:
            self.error()

    def parse(self):
        errors = []
        while self.current_token:
            try:
                self.statement()
            except Exception as e:
                errors.append(str(e))

        # Display Identifier Table
        identifier_table = "\nIdentifier Table:\n| Identifier        | Value      |\n|-------------------|------------|"
        for identifier, value in self.variables.items():
            identifier_table += f"\n| {identifier:<18} | {str(value):<10} |"

        return identifier_table, errors

class MathCompilerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Math Compiler GUI")

        self.program_label = Label(master, text="Enter Program:")
        self.program_label.pack()

        self.program_entry = scrolledtext.ScrolledText(master, width=40, height=10)
        self.program_entry.pack()
        
        self.compile_button = Button(master, text="Compile", command=self.compile_program)
        self.compile_button.pack()

        self.token_label = Label(master, text="Token Table:")
        self.token_label.pack()

        self.token_text = scrolledtext.ScrolledText(master, width=40, height=10)
        self.token_text.pack()

        self.identifier_label = Label(master, text="Identifier Table:")
        self.identifier_label.pack()

        self.identifier_text = scrolledtext.ScrolledText(master, width=40, height=10)
        self.identifier_text.pack()

        self.error_label = Label(master, text="Error Messages:")
        self.error_label.pack()

        self.error_text = scrolledtext.ScrolledText(master, width=40, height=5)
        self.error_text.pack()


    def compile_program(self):
        input_program = self.program_entry.get("1.0", tk.END)

        # Lexical Analysis
        lexer = Lexer(input_program)
        tokens, lex_errors = lexer.lex()

        # Display Token Table
        token_table = "\nToken Table:\n| Type              | Value      |\n|-------------------|------------|"
        for token in tokens:
            token_table += f"\n{token}"

        self.token_text.delete(1.0, tk.END)
        self.token_text.insert(tk.END, token_table)

        # Parsing and Execution
        parser = Parser(tokens.copy())
        identifier_table, parse_errors = parser.parse()

        self.identifier_text.delete(1.0, tk.END)
        self.identifier_text.insert(tk.END, identifier_table)

        # Display Errors
        error_messages = "\nError Messages:\n"
        if lex_errors or parse_errors:
            error_messages += "\n".join(lex_errors + parse_errors)
        else:
            error_messages += "No errors."

        self.error_text.delete(1.0, tk.END)
        self.error_text.insert(tk.END, error_messages)

def main():
    root = tk.Tk()
    app = MathCompilerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()