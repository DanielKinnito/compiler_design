#include <iostream>
#include <string>
#include <sstream>
#include <unordered_map>
#include <unordered_set>

// Token types
enum TokenType {
    INTEGER,
    FLOAT,
    DOUBLE,
    IDENTIFIER,
    PLUS,
    EQUAL,
    SEMICOLON,
    KEYWORD,
    EOF_TOKEN
};

// Token structure
struct Token {
    TokenType type;
    std::string value;
};

class Lexer {
public:
    Lexer(const std::string& input) : input(input), currentPos(0) {}

    // Lexical analysis
    Token getNextToken() {
        while (currentPos < input.length()) {
            char currentChar = input[currentPos];

            if (isdigit(currentChar)) {
                return parseNumber();
            } else if (isalpha(currentChar) || currentChar == '_') {
                return parseIdentifierOrKeyword();
            } else if (currentChar == '+') {
                currentPos++;
                return Token{PLUS, "+"};
            } else if (currentChar == '=') {
                currentPos++;
                return Token{EQUAL, "="};
            } else if (currentChar == ';') {
                currentPos++;
                return Token{SEMICOLON, ";"};
            }

            // Skip whitespace
            else if (isspace(currentChar)) {
                currentPos++;
                continue;
            }

            // If the character is not recognized
            else {
                std::cerr << "Error: Unrecognized character '" << currentChar << "'" << std::endl;
                exit(1);
            }
        }

        return Token{EOF_TOKEN, ""};
    }

private:
    // Helper function to parse numbers
    Token parseNumber() {
        std::stringstream valueStream;
        while (currentPos < input.length() && (isdigit(input[currentPos]) || input[currentPos] == '.')) {
            valueStream << input[currentPos];
            currentPos++;
        }

        std::string value = valueStream.str();

        if (value.find('.') != std::string::npos) {
            return Token{DOUBLE, value};  // Corrected from FLOAT to DOUBLE
        } else {
            return Token{INTEGER, value};
        }
    }

    // Helper function to parse identifiers or keywords
    Token parseIdentifierOrKeyword() {
        std::stringstream valueStream;
        while (currentPos < input.length() && (isalnum(input[currentPos]) || input[currentPos] == '_')) {
            valueStream << input[currentPos];
            currentPos++;
        }

        std::string identifier = valueStream.str();

        // Check if the identifier is a keyword
        if (isKeyword(identifier)) {
            return Token{KEYWORD, identifier};
        } else {
            return Token{IDENTIFIER, identifier};
        }
    }

    // Helper function to check if a string is a keyword
    bool isKeyword(const std::string& str) {
        static const std::unordered_set<std::string> keywords = {"int", "float", "double"};
        return keywords.find(str) != keywords.end();
    }

    std::string input;
    size_t currentPos;
};

class Parser {
public:
    Parser(Lexer& lexer) : lexer(lexer), currentToken(lexer.getNextToken()) {}

    // Parsing
    void parseProgram() {
        while (currentToken.type != EOF_TOKEN) {
            parseStatement();
        }
    }

    // Accessor for variables
    const std::unordered_map<std::string, std::pair<std::string, int>>& getVariables() const {
        return variables;
    }

private:
    // Helper function to consume the current token
    void eat(TokenType expectedType) {
        if (currentToken.type == expectedType) {
            currentToken = lexer.getNextToken();
        } else {
            std::cerr << "Error: Expected token type " << expectedType << ", but got " << currentToken.type << std::endl;
            exit(1);
        }
    }

    // Helper function to parse statements
    void parseStatement() {
        if (currentToken.type == KEYWORD) {
            parseVariableDeclaration();
        } else if (currentToken.type == IDENTIFIER) {
            parseAssignment();
        } else {
            std::cerr << "Error: Unexpected token type " << currentToken.type << " in statement" << std::endl;
            exit(1);
        }
    }

    // Helper function to parse variable declarations
    void parseVariableDeclaration() {
        std::string variableType = currentToken.value;
        eat(KEYWORD);

        Token identifierToken = currentToken;
        eat(IDENTIFIER);

        eat(EQUAL);

        int value = parseExpression();
        eat(SEMICOLON);

        // For simplicity, store the variable in a map (you may want a symbol table in a real compiler)
        variables[identifierToken.value] = std::make_pair(variableType, value);
    }

    // Helper function to parse assignments
    void parseAssignment() {
        Token identifierToken = currentToken;
        eat(IDENTIFIER);
        eat(EQUAL);

        int value = parseExpression();
        eat(SEMICOLON);

        // Update the variable value in the map
        if (variables.find(identifierToken.value) != variables.end()) {
            variables[identifierToken.value].second = value;
        } else {
            std::cerr << "Error: Variable '" << identifierToken.value << "' not declared" << std::endl;
            exit(1);
        }
    }

    // Helper function to parse expressions
    int parseExpression() {
        int result = parseTerm();

        while (currentToken.type == PLUS) {
            Token op = currentToken;
            eat(PLUS);
            result += parseTerm();
        }

        return result;
    }

    // Helper function to parse terms
    int parseTerm() {
        if (currentToken.type == INTEGER || currentToken.type == FLOAT || currentToken.type == DOUBLE) {
            int result = std::stoi(currentToken.value);
            eat(currentToken.type);
            return result;
        } else if (currentToken.type == IDENTIFIER) {
            // Look up the variable value in the map
            std::string identifier = currentToken.value;
            eat(IDENTIFIER);

            if (variables.find(identifier) != variables.end()) {
                return variables[identifier].second;
            } else {
                std::cerr << "Error: Variable '" << identifier << "' not declared" << std::endl;
                exit(1);
            }
        } else {
            std::cerr << "Error: Unexpected token type " << currentToken.type << " in term" << std::endl;
            exit(1);
        }
    }

    Lexer& lexer;
    Token currentToken;
    std::unordered_map<std::string, std::pair<std::string, int>> variables;
};

int main() {
    // User input
    std::cout << "Enter your program (Ctrl+D to end input):" << std::endl;
    std::string inputProgram;
    std::string line;
    while (std::getline(std::cin, line)) {
        inputProgram += line + "\n";
    }

    // Lexical analysis
    Lexer lexer(inputProgram);

    // Parsing
    Parser parser(lexer);
    parser.parseProgram();

    // Output variable values
    std::cout << "\nVariable Values:" << std::endl;
    std::cout << "----------------" << std::endl;

    // Access the variables using the public member function
    for (const auto& entry : parser.getVariables()) {
        std::cout << entry.first << " (" << entry.second.first << ") = " << entry.second.second << std::endl;
    }

    return 0;
}