with open('backend/ai_analyzer.py', 'rb') as f:
    data = f.read()

# Try to decode with errors='replace'
content = data.decode('utf-8', errors='replace')

# Look for the exact corrupted chunk:
# "  * **성        try:\r\n            # 로컬 PDF 텍스트 추출 완료 및 프롬프트 주입으로 File API 업로드 필요 없음 (속도 3배 개선)\r\n            response = model.generate_content([prompt])\r\n            return response.text고, 지료 청구나 지분 인수/공유물 분할 소송 등 실질적인 출구 전략을 제시할 것."
# We should replace it with the corrected text:
# "  * **성립 여부**: 유치권 성립 여부(점유 시점, 피담보채권 성립 시점), 법정지상권 성립 여부(토지/건물 소유자 동일성 여부 등) 분석 및 지료 청구나 지분 인수/공유물 분할 소송 등 실질적인 출구 전략을 제시할 것."

# Let's do a substring replacement of the corrupted bytes
corrupted_str = "  * **성\ufffd        try:\n            # 로컬 PDF 텍스트 추출 완료 및 프롬프트 주입으로 File API 업로드 필요 없음 (속도 3배 개선)\n            response = model.generate_content([prompt])\n            return response.text고, 지료 청구나 지분 인수/공유물 분할 소송 등 실질적인 출구 전략을 제시할 것."
# Normalize newline endings
content_normalized = content.replace('\r\n', '\n')
corrupted_str_normalized = corrupted_str.replace('\r\n', '\n')

corrected_str = "  * **성립 여부**: 유치권 성립 여부(점유 시점, 피담보채권 성립 시점), 법정지상권 성립 여부(토지/건물 소유자 동일성 여부 등) 분석 및 지료 청구나 지분 인수/공유물 분할 소송 등 실질적인 출구 전략을 제시할 것."

if corrupted_str_normalized in content_normalized:
    content_normalized = content_normalized.replace(corrupted_str_normalized, corrected_str)
    print("SUCCESS: Corrupted chunk found and replaced!")
else:
    # Try a looser match in case spacing differs
    import re
    pattern = re.compile(r'  \* \*\*성\ufffd\s*try:.*?return response\.text고,\s*지료 청구', re.DOTALL)
    if pattern.search(content_normalized):
        content_normalized = pattern.sub("  * **성립 여부**: 유치권 성립 여부(점유 시점, 피담보채권 성립 시점), 법정지상권 성립 여부(토지/건물 소유자 동일성 여부 등) 분석 및 지료 청구", content_normalized)
        print("SUCCESS: Corrupted chunk found and replaced via regex!")
    else:
        print("ERROR: Corrupted chunk not found in the normalized content.")

# Save the healed file back as UTF-8 (clean)
with open('backend/ai_analyzer.py', 'w', encoding='utf-8') as f:
    f.write(content_normalized)

print("Healed file saved as backend/ai_analyzer.py")
