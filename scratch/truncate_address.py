import os

filepath = 'public/analysis.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Normalize to LF for easy replacement
content = content.replace('\r\n', '\n')

# 1. Add the truncateAddressToDong function right after <script>
script_start = '<script>'
function_def = """<script>
    // 법정동(동, 리, 가)까지만 주소 자르기 헬퍼 함수
    function truncateAddressToDong(address) {
        if (!address) return '-';
        const addr = address.trim();
        const match = addr.match(/^.*?[동리가](\\s|$)/);
        if (match) {
            return match[0].trim();
        }
        const parts = addr.split(/\\s+/);
        return parts.slice(0, 3).join(' ');
    }"""

if script_start in content and "truncateAddressToDong" not in content:
    content = content.replace(script_start, function_def, 1) # Only replace the first script tag (which contains the page logic)
    print("Function definition added.")
else:
    print("Function definition already exists or <script> not found.")

# 2. Modify the table row address column
target_table_cell = '<td style="font-size: 0.78rem; font-weight: 500;">${item.address}</td>'
replacement_table_cell = '<td style="font-size: 0.78rem; font-weight: 500;" title="${item.address}">${truncateAddressToDong(item.address)}</td>'

if target_table_cell in content:
    content = content.replace(target_table_cell, replacement_table_cell)
    print("Table address column modified.")
else:
    print("Target table cell not found.")

# Convert back to CRLF
content = content.replace('\n', '\r\n')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done!")
