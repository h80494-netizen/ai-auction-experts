import re

with open('public/analysis.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace best3.forEach((item, index) => { with a try-catch block
old_str = "best3.forEach((item, index) => {"
new_str = """best3.forEach((item, index) => {
                try {"""

old_str2 = """                // Load demographics for card asynchronously
                loadDemographicsForCard(item, index);
            });"""
new_str2 = """                // Load demographics for card asynchronously
                loadDemographicsForCard(item, index);
                } catch(err) {
                    console.error(err);
                    bestContainer.innerHTML += `<div style="color:red; font-size: 20px;">ERROR in best3 loop: ${err.message}<br>${err.stack}</div>`;
                }
            });"""

# also try-catch the table loop
old_str3 = """            itemsList.forEach(item => {"""
new_str3 = """            itemsList.forEach(item => {
                try {"""

old_str4 = """                tableBody.appendChild(tr);
            });"""
new_str4 = """                tableBody.appendChild(tr);
                } catch(err) {
                    console.error(err);
                    tableBody.innerHTML += `<tr><td colspan="10" style="color:red;">ERROR in table loop: ${err.message}</td></tr>`;
                }
            });"""

if old_str in content:
    content = content.replace(old_str, new_str)
if '// 비동기 분석 로드 호출' in content:
    content = content.replace('// 비동기 분석 로드 호출\n                loadDemographicsForCard(item, index);\n            });', 
                              '// 비동기 분석 로드 호출\n                loadDemographicsForCard(item, index);\n                } catch(err) {\n                    bestContainer.innerHTML += `<div style="color:red; padding:20px;">ERROR in best3 loop: ${err.message}</div>`;\n                }\n            });')
    
# Wait, let's just use a simpler replacement
content = content.replace("best3.forEach((item, index) => {", "best3.forEach((item, index) => { try {")
content = content.replace("loadDemographicsForCard(item, index);\n            });", "loadDemographicsForCard(item, index);\n} catch(err) { bestContainer.innerHTML += `<div style='color:red'>${err.message}</div>`; console.error(err); }\n            });")

content = content.replace("itemsList.forEach(item => {", "itemsList.forEach(item => { try {")
content = content.replace("tableBody.appendChild(tr);\n            });", "tableBody.appendChild(tr);\n} catch(err) { tableBody.innerHTML += `<tr><td colspan='10' style='color:red'>${err.message}</td></tr>`; console.error(err); }\n            });")

with open('public/analysis.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Injected error loggers.")
