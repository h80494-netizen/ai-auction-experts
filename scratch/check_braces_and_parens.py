import re
import sys

with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
if not match:
    print("No script block found")
    sys.exit(1)

script = match.group(1)
lines = script.split('\n')

stack = [] # holds (char, line_num, col_num)
in_string = False
string_char = None
in_comment = False
in_multiline_comment = False

for line_idx, line in enumerate(lines):
    line_num = line_idx + 1
    col_idx = 0
    while col_idx < len(line):
        char = line[col_idx]
        
        # Handle multiline comments
        if in_multiline_comment:
            if char == '*' and col_idx + 1 < len(line) and line[col_idx+1] == '/':
                in_multiline_comment = False
                col_idx += 2
                continue
            col_idx += 1
            continue
            
        # Handle single line comments
        if in_comment:
            break # comment goes to end of line
            
        # Handle string literals
        if in_string:
            if char == '\\':
                col_idx += 2 # skip escaped character
                continue
            if char == string_char:
                in_string = False
            col_idx += 1
            continue
            
        # Start of comments or strings
        if char == '/' and col_idx + 1 < len(line) and line[col_idx+1] == '/':
            break # single line comment
        if char == '/' and col_idx + 1 < len(line) and line[col_idx+1] == '*':
            in_multiline_comment = True
            col_idx += 2
            continue
        if char in ["'", '"', '`']:
            in_string = True
            string_char = char
            col_idx += 1
            continue
            
        # Braces and Parentheses
        if char in ['{', '(']:
            stack.append((char, line_num, col_idx + 1))
        elif char == '}':
            if not stack:
                print(f"Extra closing brace '}}' at line {line_num}, col {col_idx+1}")
            else:
                last_char, l_num, c_num = stack.pop()
                if last_char != '{':
                    print(f"Mismatch: '{last_char}' opened at line {l_num}:{c_num} closed by '}}' at line {line_num}:{col_idx+1}")
        elif char == ')':
            if not stack:
                print(f"Extra closing paren ')' at line {line_num}, col {col_idx+1}")
            else:
                last_char, l_num, c_num = stack.pop()
                if last_char != '(':
                    print(f"Mismatch: '{last_char}' opened at line {l_num}:{c_num} closed by ')' at line {line_num}:{col_idx+1}")
                    
        col_idx += 1
    # End of line, reset single line comment
    in_comment = False

# Print remaining unclosed elements in stack
if stack:
    print(f"Unclosed elements ({len(stack)} remaining):")
    for item in stack[:20]:
        print(f"  '{item[0]}' opened at line {item[1]}, col {item[2]}")
else:
    print("Stack is completely empty! Everything matched perfectly.")
