import sys
with open('backend/ai_analyzer.py', 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('gemini-3.6-flash', 'gemini-1.5-flash')

safety_settings = """safety_settings = [
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                ]
                response = model.generate_content(contents, safety_settings=safety_settings)"""

code = code.replace('response = model.generate_content(contents)', safety_settings)

with open('backend/ai_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(code)
