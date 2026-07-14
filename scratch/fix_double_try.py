with open('public/analysis.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('best3.forEach((item, index) => { try {\n                try {', 'best3.forEach((item, index) => { try {')

with open('public/analysis.html', 'w', encoding='utf-8') as f:
    f.write(content)
