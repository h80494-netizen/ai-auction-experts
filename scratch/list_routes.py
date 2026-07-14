with open('backend/app.py', 'r', encoding='utf-8') as f:
    for i, l in enumerate(f):
        if '@app.get("/api/map/' in l or '@app.get("/api/' in l:
            print(f'{i+1}: {l.strip()}')
