from bs4 import BeautifulSoup

with open("scratch/search_result_6060.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')

print("--- INPUTS in FORM ---")
form = soup.find('form', attrs={'name': 'frm'})
if form:
    # Find all input, select, and button elements in the form
    for elem in form.find_all(['input', 'select', 'textarea']):
        name = elem.get('name')
        value = elem.get('value', '')
        type_ = elem.get('type', '')
        if type_ == 'checkbox':
            checked = 'checked' in elem.attrs
            print(f"Checkbox: name={name}, value={value}, checked={checked}")
        elif type_ == 'radio':
            checked = 'checked' in elem.attrs
            print(f"Radio: name={name}, value={value}, checked={checked}")
        elif elem.name == 'select':
            options = [opt.get('value') for opt in elem.find_all('option')]
            selected = [opt.get('value') for opt in elem.find_all('option') if 'selected' in opt.attrs]
            print(f"Select: name={name}, options={options}, selected={selected}")
        else:
            print(f"Input: name={name}, value={value}, type={type_}")
else:
    print("Form 'frm' not found")
