import sys
from backend.doc_generator import generate_analysis_doc_from_markdown

test_markdown = """
# 1. 핵심요점
테스트
# 2. 기본정보
테스트2
"""

try:
    generate_analysis_doc_from_markdown("테스트 사건 2024", test_markdown, "downloads")
    print("Success")
except Exception as e:
    print(f"Error: {e}")
