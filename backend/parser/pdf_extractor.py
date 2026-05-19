import fitz  # PyMuPDF
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    PDF 파일에서 텍스트를 추출합니다.
    주의: 스캔본 이미지 형태의 PDF(오래된 등기부 등)는 텍스트가 추출되지 않을 수 있습니다.
    이 경우 별도의 OCR 모듈(Tesseract 등) 도입이 필요합니다.
    """
    if not os.path.exists(pdf_path):
        return f"Error: 파일을 찾을 수 없습니다 - {pdf_path}"
        
    text_content = ""
    try:
        # PDF 문서 열기
        doc = fitz.open(pdf_path)
        
        # 모든 페이지 순회하며 텍스트 추출
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            text_content += text + "\n"
            
        doc.close()
        return text_content.strip()
        
    except Exception as e:
        return f"Error: PDF 파싱 실패 - {str(e)}"

if __name__ == "__main__":
    # 테스트용
    pass
