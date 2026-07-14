import re

with open(r"c:\Users\llll\Documents\두인경매\바이브코딩\public\map.html", "r", encoding="utf-8") as f:
    content = f.read()

# Let's find any sequences of 3 or more Chinese characters that are typically garbled text (like 吏€援щ떒)
# Or let's search specifically for non-ASCII characters that look like garbled EUC-KR in UTF-8
# Let's just find any occurrences of "吏€" (which is '지' in EUC-KR interpreted as UTF-8)
matches = re.finditer(r'[\u4e00-\u9fff\uac00-\ud7af\uff00-\uffef\u3000-\u303f]{2,}', content)

print("Potential garbled/Korean words:")
seen = set()
for m in matches:
    word = m.group(0)
    if word not in seen:
        seen.add(word)
        # Check if it has any typical EUC-KR garbling characters like '吏€', '援', '떒', '뾿'
        if any(c in word for c in ['吏', '援', '', '', '떒', '띻', '뎄', '꾧', '퀎']):
            print(f"Garbled: {word}")
        else:
            # Check if it contains normal Korean characters
            if any('\uac00' <= c <= '\ud7af' for c in word):
                # This is normal Korean, skip it or print it if needed
                pass
            else:
                print(f"Other: {word}")
