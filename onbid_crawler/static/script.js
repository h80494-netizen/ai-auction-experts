document.addEventListener('DOMContentLoaded', () => {
    const btnWeeklyAll = document.getElementById('btn-weekly-all');
    const btnCrawl = document.getElementById('btn-crawl');
    const btnCrawlDooin = document.getElementById('btn-crawl-dooin');
    const btnCrawlDooinRegional = document.getElementById('btn-crawl-dooin-regional');
    const btnCrawlSeoul = document.getElementById('btn-crawl-seoul');
    const btnCrawlIncheon = document.getElementById('btn-crawl-incheon');
    const btnCrawlKyunggi = document.getElementById('btn-crawl-kyunggi');
    const btnCrawlKangwon = document.getElementById('btn-crawl-kangwon');
    const btnCrawlChungnam = document.getElementById('btn-crawl-chungnam');
    const btnCrawlJeonnam = document.getElementById('btn-crawl-jeonnam');
    const btnCancel = document.getElementById('btn-cancel');
    const btnRetry = document.getElementById('btn-retry');
    
    const actionSections = document.querySelectorAll('.action-section');
    const statusContainer = document.getElementById('status-container');
    const successContainer = document.getElementById('success-container');
    const errorContainer = document.getElementById('error-container');
    const errorDesc = document.getElementById('error-desc');
    const statusMessage = document.getElementById('status-message');

    if (btnWeeklyAll) btnWeeklyAll.addEventListener('click', () => startCrawling('/api/weekly_pipeline', '주간 전체 자동화 파이프라인(온비드 공매 + 수도권/지방권 경매 크롤링 → 신규 물건 KakaoGeocode → 엑셀 시트 탑재 → 로컬 DB & AWS 서버 배포)을 실행 중입니다...<br><span class="sub-message">완료될 때까지 잠시만 기다려주세요.</span>'));
    if (btnCrawl) btnCrawl.addEventListener('click', () => startCrawling('/api/crawl', '온비드 진행/수의계약 물건 및 과거 취소·회수 물건을 통합 수집 중입니다...<br><span class="sub-message">창을 닫지 말고 잠시만 기다려주세요.</span>'));
    if (btnCrawlDooin) btnCrawlDooin.addEventListener('click', () => startCrawling('/api/crawl_dooin', '두인경매에서 수도권 데이터를 가져오는 중입니다... (1~3분 소요)<br><span class="sub-message">창을 닫지 말고 잠시만 기다려주세요.</span>'));
    if (btnCrawlDooinRegional) btnCrawlDooinRegional.addEventListener('click', () => startCrawling('/api/crawl_dooin_regional', '강원/충남/전남(광주) 두인경매에서 데이터를 가져오는 중입니다... (1~3분 소요)<br><span class="sub-message">창을 닫지 말고 잠시만 기다려주세요.</span>'));
    if (btnCrawlSeoul) btnCrawlSeoul.addEventListener('click', () => startCrawling('/api/crawl_region/seoul', '서울 두인경매에서 데이터를 가져오는 중입니다...<br><span class="sub-message">창을 닫지 말고 잠시만 기다려주세요.</span>'));
    if (btnCrawlIncheon) btnCrawlIncheon.addEventListener('click', () => startCrawling('/api/crawl_region/incheon', '인천 두인경매에서 데이터를 가져오는 중입니다...<br><span class="sub-message">창을 닫지 말고 잠시만 기다려주세요.</span>'));
    if (btnCrawlKyunggi) btnCrawlKyunggi.addEventListener('click', () => startCrawling('/api/crawl_region/kyunggi', '경기 두인경매에서 데이터를 가져오는 중입니다...<br><span class="sub-message">창을 닫지 말고 잠시만 기다려주세요.</span>'));
    if (btnCrawlKangwon) btnCrawlKangwon.addEventListener('click', () => startCrawling('/api/crawl_region/kangwon', '강원 두인경매에서 데이터를 가져오는 중입니다...<br><span class="sub-message">창을 닫지 말고 잠시만 기다려주세요.</span>'));
    if (btnCrawlChungnam) btnCrawlChungnam.addEventListener('click', () => startCrawling('/api/crawl_region/chungnam', '충남 두인경매에서 데이터를 가져오는 중입니다...<br><span class="sub-message">창을 닫지 말고 잠시만 기다려주세요.</span>'));
    if (btnCrawlJeonnam) btnCrawlJeonnam.addEventListener('click', () => startCrawling('/api/crawl_region/jeonnam', '전남(광주) 두인경매에서 데이터를 가져오는 중입니다...<br><span class="sub-message">창을 닫지 말고 잠시만 기다려주세요.</span>'));

    if (btnCancel) {
        btnCancel.addEventListener('click', async () => {
            btnCancel.textContent = '취소하는 중...';
            btnCancel.disabled = true;
            try {
                await fetch('/api/cancel', { method: 'POST' });
            } catch(e) {
                console.error(e);
            }
        });
    }

    if (btnRetry) btnRetry.addEventListener('click', resetUI);

    async function startCrawling(apiUrl, statusText) {
        // UI 상태 업데이트: 실행 버튼 숨기고 로딩 표시
        actionSections.forEach(el => el.classList.add('hidden'));
        statusContainer.classList.remove('hidden');
        successContainer.classList.add('hidden');
        errorContainer.classList.add('hidden');
        
        if (btnCancel) {
            btnCancel.textContent = '크롤링 취소';
            btnCancel.disabled = false;
        }
        
        if (statusText) {
            statusMessage.innerHTML = statusText;
        }

        try {
            // Flask 서버에 크롤링 시작 요청 (비동기 태스크 생성)
            let response;
            try {
                response = await fetch(apiUrl, {
                    method: 'POST',
                });
            } catch (netErr) {
                throw new Error("서버에 연결할 수 없습니다.<br><span style='font-size:0.85em; color:#a0aec0;'>'실행하기.bat' 또는 콘솔 창이 정상적으로 켜져 있는지 확인해주세요.</span>");
            }

            if (!response.ok) {
                let errorMsg = `서버 에러 (${response.status})`;
                try {
                    const errorData = await response.json();
                    if (errorData.message) errorMsg = errorData.message;
                } catch (e) {
                    // JSON 파싱 실패 시 기본 에러 메시지 사용
                }
                throw new Error(errorMsg);
            }

            const data = await response.json();
            const taskId = data.task_id;
            
            // 상태 확인 폴링 루프 (네트워크 일시 오류 시 최대 5회 재시도)
            let consecutiveErrors = 0;
            const maxConsecutiveErrors = 5;

            while (true) {
                await new Promise(resolve => setTimeout(resolve, 3000)); // 3초 대기
                
                let statusRes;
                try {
                    statusRes = await fetch(`/api/status/${taskId}`);
                    consecutiveErrors = 0; // 성공 시 카운트 리셋
                } catch (pollErr) {
                    consecutiveErrors++;
                    console.warn(`상태 확인 재시도 중 (${consecutiveErrors}/${maxConsecutiveErrors})...`);
                    if (consecutiveErrors >= maxConsecutiveErrors) {
                        throw new Error("서버와의 연결이 끊어졌습니다.<br><span style='font-size:0.85em; color:#a0aec0;'>서버 프로세스가 종료되었는지 확인해주세요.</span>");
                    }
                    continue;
                }

                if (!statusRes.ok) {
                    throw new Error(`상태 확인 실패 (${statusRes.status})`);
                }
                
                const statusData = await statusRes.json();
                
                if (statusData.status === 'completed') {
                    // 완료 시 파일 다운로드 호출
                    const downloadRes = await fetch(`/api/download/${taskId}`);
                    if (!downloadRes.ok) throw new Error('파일 다운로드 실패');
                    
                    const blob = await downloadRes.blob();
                    
                    // Content-Disposition 헤더에서 파일명 추출 시도
                    let filename = '데이터.xlsx';
                    const disposition = downloadRes.headers.get('Content-Disposition');
                    if (disposition && disposition.indexOf('attachment') !== -1) {
                        const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                        const matches = filenameRegex.exec(disposition);
                        if (matches != null && matches[1]) { 
                            filename = matches[1].replace(/['"]/g, '');
                        }
                    }

                    // 임시 링크를 생성하여 다운로드 실행
                    const windowUrl = window.URL || window.webkitURL;
                    const downloadUrl = windowUrl.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = downloadUrl;
                    a.download = decodeURIComponent(filename); // 파일명 디코딩
                    document.body.appendChild(a);
                    a.click();
                    a.remove();
                    windowUrl.revokeObjectURL(downloadUrl);

                    // 성공 UI 표시
                    statusContainer.classList.add('hidden');
                    successContainer.classList.remove('hidden');
                    
                    setTimeout(resetUI, 5000);
                    break;
                } else if (statusData.status === 'error') {
                    throw new Error(statusData.message || '알 수 없는 오류');
                }
                // running 상태면 루프를 계속 돌며 대기
            }

        } catch (error) {
            console.error('Crawling failed:', error);
            
            // 에러 UI 표시
            statusContainer.classList.add('hidden');
            errorContainer.classList.remove('hidden');
            
            let message = error.message;
            if (message === 'Failed to fetch') {
                message = "서버와 연결할 수 없습니다.<br><span style='font-size:0.85em; color:#a0aec0;'>'실행하기.bat' 또는 Flask 서버가 켜져 있는지 확인해주세요.</span>";
            }
            errorDesc.innerHTML = message;
        }
    }

    function resetUI() {
        actionSections.forEach(el => el.classList.remove('hidden'));
        statusContainer.classList.add('hidden');
        successContainer.classList.add('hidden');
        errorContainer.classList.add('hidden');
        if (btnCancel) {
            btnCancel.textContent = '크롤링 취소';
            btnCancel.disabled = false;
        }
    }
});
