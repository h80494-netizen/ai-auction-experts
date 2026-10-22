import re

text = open('public/map.html', encoding='utf-8').read()
words = re.findall(r'[^\s<>]*\?[^\s<>]*', text)
unique_words = sorted(list(set(words)))
for w in unique_words:
    print(w)
