with open('public/map.html', 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if "toggle-dev3" in l and "addEventListener" in l:
            print(f'{i+1}: {l.strip()}')
