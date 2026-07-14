with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html", "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("async function fetchDistrictUnits()")
if idx != -1:
    print("Found at index:", idx)
    print("Printing 1200 characters from match:")
    print(repr(content[idx:idx+1200]))
else:
    print("Not found at all!")
