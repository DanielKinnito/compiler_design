import re
import tkinter as tk
from tkinter import Entry, Label, Button, scrolledtext


class Token:
    def __init__(self, token_type, value):
        self.token_type = token_type
        self.value = value

    def __str__(self):
        return f"| {self.token_type:<18}| {self.value:<11}|"

/(200+3*4.5+4*8.2/2)-2
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
            elif self.current_char == "%":
                tokens.append(Token("MODULO", self.current_char))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token("LPAREN", self.current_char))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token("RPAREN", self.current_char))
                self.advance()
            elif self.current_char == "**":
                tokens.append(Token("POWER", self.current_char))
                self.advance()
            elif self.current_char.isalpha():
                tokens.append(self.parse_logical())
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
# not used on purpose
    def parse_logical(self):
        result = ""
        while self.current_char is not None and (self.current_char.isalpha() or self.current_char == '_'):
            result += self.current_char
            self.advance()

        if result.lower() == "true":
            return Token("BOOL", True)
        elif result.lower() == "false":
            return Token("BOOL", False)
        elif result.lower() == "and":
            return Token("AND", "and")
        elif result.lower() == "or":
            return Token("OR", "or")
        elif result.lower() == "not":
            return Token("NOT", "not")
        else:
            raise Exception(f"Invalid logical operator: {result}")


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token = self.tokens.pop(0) if tokens else None

    def error(self):
        print("Invalid syntax")
        # exit(1)

    def eat(self, token_type):
        if self.current_token.token_type == token_type:
            self.current_token = self.tokens.pop(0) if self.tokens else None
        else:
            self.error()

    def factor(self):
        if self.current_token.token_type == "INT" or self.current_token.token_type == "FLOAT" or self.current_token.token_type == "BOOL":
            result = self.current_token.value
            self.eat(self.current_token.token_type)
            return result
        elif self.current_token.token_type == "LPAREN":
            self.eat("LPAREN")
            result = self.expr()
            self.eat("RPAREN")
            return result
        elif self.current_token.token_type == "NOT":
            self.eat("NOT")
            result = not self.factor()
            return result
        else:
            self.error()

# left on purpose
    def power(self):
        result = self.factor()

        while self.current_token and self.current_token.token_type == "POWER":
            self.eat("POWER")
            result **= self.factor()

        return result

    def term(self):
        result = self.power()

        while self.current_token and self.current_token.token_type in ("MULTIPLY", "DIVIDE", "MODULO"):
            if self.current_token.token_type == "MULTIPLY":
                self.eat("MULTIPLY")
                result *= self.power()
            elif self.current_token.token_type == "DIVIDE":
                self.eat("DIVIDE")
                divisor = self.power()
                if divisor != 0:
                    result /= divisor
                else:
                    raise Exception("Division by zero")
            elif self.current_token.token_type == "MODULO":
                self.eat("MODULO")
                modulo_value = self.power()
                if modulo_value != 0:
                    result %= modulo_value
                else:
                    raise Exception("Modulo by zero")

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
# left on purpose 
    def logical_and(self):
        result = self.expr()

        while self.current_token and self.current_token.token_type == "AND":
            self.eat("AND")
            result = result and self.expr()

        return result

    def logical_or(self):
        result = self.logical_and()

        while self.current_token and self.current_token.token_type == "OR":
            self.eat("OR")
            result = result or self.logical_and()

        return result


class MathCompilerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Math Compiler GUI")

        self.expression_label = Label(master, text="Enter Expression:")
        self.expression_label.pack()

        self.expression_entry = Entry(master)
        self.expression_entry.pack()

        self.result_label = Label(master, text="Result:")
        self.result_label.pack()

        self.result_text = scrolledtext.ScrolledText(master, width=40, height=5)
        self.result_text.pack()

        self.token_label = Label(master, text="Token Table:")
        self.token_label.pack()

        self.token_text = scrolledtext.ScrolledText(master, width=40, height=10)
        self.token_text.pack()

        self.compile_button = Button(master, text="Compile", command=self.compile_expression)
        self.compile_button.pack()

    def compile_expression(self):
        input_expression = self.expression_entry.get()

        # Lexical Analysis
        lexer = Lexer(input_expression)
        tokens = lexer.lex()

        # Display Token Table
        token_table = "\nToken Table:\n| Type              | Value      |\n|-------------------|------------|"
        for token in tokens:
            token_table += f"\n{token}"

        self.token_text.delete(1.0, tk.END)
        self.token_text.insert(tk.END, token_table)

        # Parsing and Evaluation
        parser = Parser(tokens.copy())
        result = parser.expr()

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, str(result))


def main():
    root = tk.Tk()
    app = MathCompilerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
