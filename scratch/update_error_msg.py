import re

with open('backend/ai_analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the generic 429 catch with a broader catch that includes 403
target = """            if "429" in err_msg:
                raise Exception("구글 Gemini API 무료 할당량(요청 수 제한)을 초과했습니다. 잠시 후 [분석 시작] 버튼을 다시 눌러주세요. 계속 발생 시 Google AI Studio에서 카드 등록이 필요합니다.")
            raise Exception(f"API 호출 오류: {err_msg}")"""

replacement = """            if "429" in err_msg:
                raise Exception("구글 Gemini API 무료 할당량(요청 수 제한)을 초과했습니다. 잠시 후 다시 시도해주세요.")
            elif "403" in err_msg and "denied access" in err_msg.lower():
                raise Exception("Google Gemini API 키가 차단되었거나 권한이 거부되었습니다 (403 Forbidden). Google AI Studio에 로그인하여 계정 상태를 확인하고 새로운 API 키를 발급받아 .env 파일에 업데이트해 주세요.")
            raise Exception(f"API 호출 오류: {err_msg}")"""

if target in content:
    content = content.replace(target, replacement)
    with open('backend/ai_analyzer.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated error handling in ai_analyzer.py")
else:
    print("Target string not found in ai_analyzer.py")
