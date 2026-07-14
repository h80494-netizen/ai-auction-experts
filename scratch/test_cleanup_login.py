import requests
from bs4 import BeautifulSoup

def test_login():
    session = requests.Session()
    
    # 1. Login
    login_url = "https://cleanup.seoul.go.kr/cleanup/login/actionLogin.do"
    # Actually, we need to find the correct login POST URL and parameters.
    # Usually it's j_username, j_password or similar.
    # Let's just fetch the login page first to find the form.
    res = session.get("https://cleanup.seoul.go.kr/cleanup/login/lscrMainIndx.do")
    soup = BeautifulSoup(res.text, 'html.parser')
    
    form = soup.find('form', id='loginForm') or soup.find('form')
    if form:
        print("Form action:", form.get('action'))
        inputs = form.find_all('input')
        for inp in inputs:
            print(f"Input: {inp.get('name')} = {inp.get('value')}")
    else:
        print("Login form not found.")
        print(res.text[:1000])

if __name__ == "__main__":
    test_login()
