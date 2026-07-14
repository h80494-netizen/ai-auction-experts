with open('public/map.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's find all checkbox inputs and their surrounding label text
import re
toggles = re.findall(r'<input[^>]+type=["\']checkbox["\'][^>]+id=["\']toggle-([^"\']+)["\'][^>]*>.*?<label[^>]*>(.*?)</label>', html, re.DOTALL)
for t in toggles:
    print(f"toggle-{t[0]}: {t[1].strip()}")

# Let's print out the exact list of checkbox toggles
print("\n--- ALL CHECKBOXES WITH ID STARTING WITH toggle- ---")
all_ch = re.findall(r'id=["\']toggle-([^"\']+)["\']', html)
for c in all_ch:
    print(f"toggle-{c}")
