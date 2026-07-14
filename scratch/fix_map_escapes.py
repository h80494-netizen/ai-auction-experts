file_path = 'public/map.html'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '\\' + '${'
count = content.count(target)
print("Count of targets: " + str(count))

if count > 0:
    new_content = content.replace(target, '${')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Replacement success.")
else:
    print("Target not found.")
