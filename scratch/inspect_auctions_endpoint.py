with open('backend/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

found = False
for idx, line in enumerate(lines):
    if '@app.get("/api/map/auctions")' in line:
        found = True
        for i in range(idx, min(len(lines), idx + 150)):
            print(f'{i+1}: {lines[i].rstrip()}')
            if 'def ' in lines[i] and i > idx + 5: # stop at next function
                # break if we reach another endpoint decorator
                pass
            if '@app.get' in lines[i] and i > idx:
                break
