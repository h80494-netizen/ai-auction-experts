bat_content = """@echo off
chcp 65001 > nul
echo ===================================================
echo     온비드 공매물건 자동 추출기 (Web 버전)
echo ===================================================
echo.
echo 필수 라이브러리를 확인하고 설치합니다...
pip install -r requirements.txt > nul 2>&1
echo.
echo 서버를 시작합니다. 잠시만 기다려주세요...
echo 브라우저가 자동으로 열립니다.

:: 현재 배치 파일이 있는 경로로 작업 디렉토리 변경
cd /d "%~dp0"

:: 브라우저 자동 실행 (포트 5000)
start http://127.0.0.1:5000

:: Flask 앱 실행
python app.py

pause
"""

with open("실행하기.bat", "w", encoding="cp949") as f:
    f.write(bat_content)
