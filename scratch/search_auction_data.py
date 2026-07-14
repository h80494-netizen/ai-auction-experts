with open('public/map.html', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'auctionData' in line:
            print(f"{idx}: {line.strip()}")
