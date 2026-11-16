@echo off
chcp 65001 > nul
echo ======================================================================
echo   [두인경매] 주간 경·공매 자동 크롤링 + KakaoGeocode + DB/AWS 배포
echo ======================================================================
echo.
cd /d "C:\Users\llll\Documents\두인경매\온비드크롤링"
python weekly_auto_pipeline.py %*
echo.
echo 작업이 완료되었습니다. 로그 파일: C:\Users\llll\Documents\두인경매\온비드크롤링\logs
