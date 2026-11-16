import os

bat_path = r"C:\Users\llll\Desktop\온비드_웹크롤러_실행.bat"
content = """@echo off
cd /d "c:\\Users\\llll\\Documents\\두인경매\\온비드크롤링"
start http://127.0.0.1:5000
python app.py
pause
"""

with open(bat_path, "w", encoding="cp949") as f:
    f.write(content)
