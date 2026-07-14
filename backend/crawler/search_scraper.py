# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import urllib.parse
import traceback

def search_expert_opinions(case_number: str) -> str:
    """
    네이버 블로그/카페 검색을 통해 해당 사건번호에 대한 경매 전문가들의 분석글을 스크래핑합니다.
    검색된 상위 1~2개 글의 텍스트를 추출하여 AI에게 Context(RAG)로 제공할 목적으로 사용됩니다.
    """
    print(f"네이버 전문가 분석글 검색 중... (사건번호: {case_number})")
    
    query = urllib.parse.quote(f'"{case_number}" 경매 권리분석 OR 추천')
    # 네이버 블로그 검색 URL (모바일 페이지가 크롤링이 용이함)
    url = f"https://m.search.naver.com/search.naver?display=3&qdt=0&query={query}&sm=mtb_nmr&where=m_blog"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=5)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 블로그 글 텍스트 추출 (주요 내용 클래스 위주)
        # api_txt_lines, api_subject_bx 등 네이버 모바일 블로그 검색 결과 클래스
        items = soup.select('.api_txt_lines.desc')
        
        expert_context = ""
        count = 0
        for item in items:
            text = item.get_text(strip=True)
            if len(text) > 30:
                count += 1
                expert_context += f"[전문가 의견 {count}]: {text}\n"
                if count >= 2:  # 상위 2개만 추출
                    break
                    
        if expert_context:
            return expert_context
        else:
            return "해당 사건번호에 대한 인터넷 전문가 분석글(블로그 등)을 찾을 수 없습니다."
            
    except Exception as e:
        print(f"웹 검색 스크래핑 오류: {e}")
        return "인터넷 검색 중 오류가 발생하여 전문가 의견을 참조하지 못했습니다."
