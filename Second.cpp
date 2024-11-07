#include <iostream>
#include <string>
#include <sstream>
#include <vector>  // Include the necessary header for vector
#include <unordered_map>
#include <unordered_set>


// Token types
enum TokenType {
    INTEGER,
    FLOAT,
    DOUBLE,
    IDENTIFIER,
    PLUS,
    MINUS,
    MULTIPLY,
    DIVIDE,
    EQUAL,
    SEMICOLON,
    KEYWORD,
    EOF_TOKEN
};

// Token structure
struct Token {
    TokenType type;
    std::string name;
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
                return Token{PLUS, "PLUS", "+"};
            } else if (currentChar == '-') {
                currentPos++;
                return Token{MINUS, "MINUS", "-"};
            } else if (currentChar == '*') {
                currentPos++;
                return Token{MULTIPLY, "MULTIPLY", "*"};
            } else if (currentChar == '/') {
                currentPos++;
                return Token{DIVIDE, "DIVIDE", "/"};
            } else if (currentChar == '=') {
                currentPos++;
                return Token{EQUAL, "EQUAL", "="};
            } else if (currentChar == ';') {
                currentPos++;
                return Token{SEMICOLON, "SEMICOLON", ";"};
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

        return Token{EOF_TOKEN, "EOF", ""};
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
            return Token{DOUBLE, "DOUBLE", value};
        } else {
            return Token{INTEGER, "INTEGER", value};
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
            return Token{KEYWORD, identifier, identifier};
        } else {
            return Token{IDENTIFIER, "IDENTIFIER", identifier};
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

    // Accessor for tokens
    const std::vector<Token>& getTokens() const {
        return tokens;
    }
    const std::unordered_map<std::string, std::pair<std::string, int>>& getVariables() const {
        return variables;
    }

private:
    // Helper function to consume the current token
    void eat(TokenType expectedType) {
        if (currentToken.type == expectedType) {
            tokens.push_back(currentToken);
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

        while (currentToken.type == PLUS || currentToken.type == MINUS || currentToken.type == MULTIPLY || currentToken.type == DIVIDE) {
            Token op = currentToken;
            eat(op.type);
            int termValue = parseTerm();

            switch (op.type) {
                case PLUS:
                    result += termValue;
                    break;
                case MINUS:
                    result -= termValue;
                    break;
                case MULTIPLY:
                    result *= termValue;
                    break;
                case DIVIDE:
                    if (termValue == 0) {
                        std::cerr << "Error: Division by zero" << std::endl;
                        exit(1);
                    }
                    result /= termValue;
                    break;
                default:
                    break;
            }
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
    std::vector<Token> tokens;  // Store all tokens
};

// Function to display tokens in a table format
void displayTokens(const std::vector<Token>& tokens) {
    std::cout << "\nTokens:" << std::endl;
    std::cout << "-------------------------------------" << std::endl;
    std::cout << "|  Type      |  Name      |  Value   |" << std::endl;
    std::cout << "-------------------------------------" << std::endl;

    for (const auto& token : tokens) {
        std::cout << "|  " << token.type << "  |  " << token.name << "  |  " << token.value << "  |" << std::endl;
    }

    std::cout << "-------------------------------------" << std::endl;
}

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

    // Display variable values
    std::cout << "\nVariable Values:" << std::endl;
    std::cout << "----------------" << std::endl;

    for (const auto& entry : parser.getVariables()) {
        std::cout << entry.first << " (" << entry.second.first << ") = " << entry.second.second << std::endl;
    }

    // Display tokens
    displayTokens(parser.getTokens());

    return 0;
}