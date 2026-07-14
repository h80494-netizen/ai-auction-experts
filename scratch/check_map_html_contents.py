with open('public/map.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's count how many times "toggle-gmr-pop-road" appears in the file
count_js_ref = content.count('toggle-gmr-pop-road')
print(f"Total occurrences of 'toggle-gmr-pop-road': {count_js_ref}")

# Let's check if there is the HTML checkbox in the file:
# typically <input type="checkbox" id="toggle-gmr-pop-road">
if '<input type="checkbox" id="toggle-gmr-pop-road">' in content:
    print("Found HTML checkbox!")
else:
    print("HTML CHECKBOX IS MISSING IN MAP.HTML!")
