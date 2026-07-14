import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
import requests

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

import os
import json
import uuid
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

def analyze_pdf_for_location(pdf_url: str, title: str = ""):
    """
    Downloads a PDF from a given URL to the data folder and uses Gemini Vision
    to analyze its contents.
    """
    if not GEMINI_API_KEY:
        return {
            "status": "error",
            "message": "GEMINI_API_KEY가 설정되지 않았습니다."
        }

    try:
        # 1. Download PDF
        file_name = f"downloaded_{uuid.uuid4().hex[:8]}.pdf"
        file_path = os.path.join(DATA_DIR, file_name)
        
        response = requests.get(pdf_url, stream=True, timeout=15)
        response.raise_for_status()
        
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        # 2. Upload to Gemini
        uploaded_file = genai.upload_file(path=file_path, display_name=file_name)
        
        # 3. Analyze with Gemini
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        prompt = f"""
        당신은 대한민국 부동산 및 국토개발 전문가입니다.
        다음 첨부된 PDF 문서(제목: {title})를 심층 분석하여 아래 항목들을 추출해 주세요.
        
        1. 핵심 요약 (3줄 이내)
        2. 주요 규제 완화 또는 개발 호재 여부
        3. 구체적인 위치(시/군/구 및 도로명/지번 등) 및 면적
        4. 토지 보상 또는 수용 예정 여부
        5. 투자 또는 입찰 시 유의사항
        
        결과를 깔끔한 마크다운 형식의 텍스트로 정리해서 답변해 주세요.
        """
        
        result = model.generate_content([uploaded_file, prompt])
        analysis_text = result.text
        
        # Cleanup uploaded file if needed (optional)
        # genai.delete_file(uploaded_file.name)
        
        return {
            "status": "success",
            "analysis": analysis_text,
            "saved_path": file_path
        }
        
    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": f"PDF 분석 중 오류가 발생했습니다: {str(e)}\n{traceback.format_exc()}"
        }
