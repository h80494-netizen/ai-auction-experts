// --- Authentication ---
document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('loginOverlay');
    const pwdInput = document.getElementById('passwordInput');
    const loginBtn = document.getElementById('loginBtn');

    if (sessionStorage.getItem('auth_token') === 'verified') {
        overlay.classList.add('hidden');
    }

    const attemptLogin = async () => {
        const pwd = pwdInput.value;
        if (!pwd) return;
        
        loginBtn.innerText = "확인 중...";
        try {
            const res = await fetch('/api/verify', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: pwd })
            });
            const data = await res.json();
            if (data.status === 'success') {
                sessionStorage.setItem('auth_token', 'verified');
                overlay.classList.add('hidden');
            } else {
                alert('비밀번호가 일치하지 않습니다.');
                pwdInput.value = '';
                pwdInput.focus();
            }
        } catch (e) {
            alert(`로그인 통신 오류: ${e.message}`);
        } finally {
            loginBtn.innerText = "입장하기";
        }
    };

    if (loginBtn) {
        loginBtn.addEventListener('click', attemptLogin);
        pwdInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') attemptLogin();
        });
    }
});
// ----------------------

// DOM 요소
const caseNumberInput = document.getElementById('caseNumberInput');
const searchCaseBtn = document.getElementById('searchCaseBtn');
const secondaryInputScreen = document.getElementById('secondaryInputScreen');
const addressListContainer = document.getElementById('addressListContainer');
const startBtn = document.getElementById('startBtn');
const errorMsg = document.getElementById('errorMsg');
const loadingState = document.getElementById('loadingState');
const finalReport = document.getElementById('finalReport');
const downloadBtn = document.getElementById('downloadBtn');
const isRegulatedAreaDisplay = document.getElementById('isRegulatedAreaDisplay');
const isRegulatedAreaInput = document.getElementById('isRegulatedArea');
const agingDisplay = document.getElementById('agingDisplay');
const resultImage = document.getElementById('resultImage');
const imagePlaceholder = document.getElementById('imagePlaceholder');

let currentCaseData = null; // 선택된 물건 데이터 보관
let isAutoAnalyze = false; // 자동 분석 여부 플래그

// 사건번호 엔터 키 검색 이벤트
if (caseNumberInput) {
    caseNumberInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (searchCaseBtn && !searchCaseBtn.disabled) {
                searchCaseBtn.click();
            }
        }
    });
}
// 1. 사건 조회 (대법원 스크래핑 버튼 클릭)
searchCaseBtn.addEventListener('click', async () => {
    const caseNumber = caseNumberInput.value.trim();
    if (!caseNumber) {
        showError("사건번호를 입력해주세요.");
        return;
    }

    showError("");
    searchCaseBtn.innerHTML = '<div class="spinner" style="display:inline-block; margin-right:8px; border-top-color:#fff;"></div>조회 중...';
    searchCaseBtn.disabled = true;
    addressListContainer.innerHTML = '';
    secondaryInputScreen.style.display = 'none';
    finalReport.classList.add('hidden');

    try {
        const response = await fetch('/api/search_cases', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ case_number: caseNumber })
        });
        const data = await response.json();

        if (response.ok && data.status === "success") {
            const results = data.data; // 리스트 형태 반환 가정
            if (results && results.length > 0) {
                renderAddressList(results);
                secondaryInputScreen.style.display = 'flex';
                // 첫 번째 물건 자동 선택
                addressListContainer.querySelector('.address-btn').click();
                
                // 자동 권리분석 실행 연동
                console.log("[Auto-Analyze] results loaded, isAutoAnalyze =", isAutoAnalyze);
                if (typeof isAutoAnalyze !== 'undefined' && isAutoAnalyze) {
                    console.log("[Auto-Analyze] triggering startBtn click in 500ms...");
                    isAutoAnalyze = false;
                    setTimeout(() => {
                        console.log("[Auto-Analyze] startBtn state - disabled:", startBtn.disabled);
                        if (startBtn && !startBtn.disabled) {
                            startBtn.click();
                            console.log("[Auto-Analyze] startBtn.click() invoked!");
                        }
                    }, 500);
                }
            } else {
                showError("조회된 물건이 없습니다. 사건번호를 확인해주세요.");
            }
        } else {
            let errorText = data.message || '알 수 없는 에러';
            showError(`서버 오류 (${response.status}): ${errorText}`);
        }
    } catch (err) {
        console.error(err);
        showError(`통신 오류: ${err.message}`);
    } finally {
        searchCaseBtn.innerHTML = '대법원 스크래핑 <i class="fa-solid fa-search"></i>';
        searchCaseBtn.disabled = false;
    }
});

// 주소 리스트 렌더링
function renderAddressList(results) {
    results.forEach((item, index) => {
        const btn = document.createElement('button');
        btn.className = 'address-btn';
        btn.style.cssText = 'padding: 15px; background: rgba(0,0,0,0.4); border: 1px solid var(--glass-border); border-radius: 8px; color: #fff; text-align: left; cursor: pointer; transition: all 0.2s;';
        btn.innerHTML = `
            <div style="font-size:1.1rem; margin-bottom:5px;"><strong>물건 ${index + 1}</strong>: ${item.address}</div>
            <div style="font-size:0.9rem; color:var(--text-muted);">감정가: ${formatNumber(item.appraised_value)}원 | 최저가: ${formatNumber(item.minimum_value)}원 | 승인일: ${item.approval_date || '알 수 없음'}</div>
        `;
        
        btn.addEventListener('mouseover', () => {
            if(!btn.classList.contains('selected')) {
                btn.style.borderColor = 'var(--neon-purple)';
                btn.style.background = 'rgba(187, 0, 255, 0.1)';
            }
        });
        btn.addEventListener('mouseout', () => {
            if(!btn.classList.contains('selected')) {
                btn.style.borderColor = 'var(--glass-border)';
                btn.style.background = 'rgba(0,0,0,0.4)';
            }
        });

        btn.addEventListener('click', () => {
            // 모든 버튼 선택 해제
            document.querySelectorAll('.address-btn').forEach(b => {
                b.classList.remove('selected');
                b.style.borderColor = 'var(--glass-border)';
                b.style.background = 'rgba(0,0,0,0.4)';
            });
            // 현재 버튼 선택
            btn.classList.add('selected');
            btn.style.borderColor = 'var(--neon-purple)';
            btn.style.background = 'rgba(187, 0, 255, 0.2)';
            
            // 데이터 설정 및 자동 산출
            currentCaseData = item;
            
            // 부동산 종류 및 사용승인일자 자동 입력
            const pTypeInput = document.getElementById('propertyType');
            if(pTypeInput) {
                pTypeInput.value = item.property_type || "알 수 없음";
            }
            const aDateInput = document.getElementById('approvalDate');
            if(aDateInput) {
                aDateInput.value = item.approval_date || "알 수 없음";
            }
            toggleHouseCount();
            
            calculateAutoFields(item.address, item.approval_date);
            
            // 이미지 세팅 (있다면)
            if (item.photo_url) {
                resultImage.src = item.photo_url;
                resultImage.style.display = 'block';
                imagePlaceholder.style.display = 'none';
            }
            
            startBtn.disabled = false;
        });

        addressListContainer.appendChild(btn);
    });
}

// 자동 산출 로직 (규제지역 & 노후도)
function calculateAutoFields(address, approvalDate) {
    // 1. 규제지역 여부 (서울 전역, 경기 12개 지역: 수원 팔달/장안/영통, 안양 동안, 분당 등)
    let isRegulated = false;
    const addr = address || "";
    
    if (addr.includes("서울")) {
        isRegulated = true;
    } else if (addr.includes("경기")) {
        const regulatedGyeonggi = ["과천시", "광명시", "하남시", "의왕시", "분당구", "수정구", "중원구", "영통구", "장안구", "팔달구", "수지구", "동안구"];
        for (let r of regulatedGyeonggi) {
            if (addr.includes(r)) {
                isRegulated = true;
                break;
            }
        }
    }
    
    isRegulatedAreaInput.value = isRegulated ? "true" : "false";
    if (isRegulated) {
        isRegulatedAreaDisplay.innerHTML = '<span style="color:var(--danger);"><i class="fa-solid fa-triangle-exclamation"></i> 조정대상지역 (취득세/양도세 중과)</span>';
        isRegulatedAreaDisplay.style.background = 'rgba(248, 81, 73, 0.1)';
        isRegulatedAreaDisplay.style.borderColor = 'var(--danger)';
    } else {
        isRegulatedAreaDisplay.innerHTML = '<span style="color:var(--success);"><i class="fa-solid fa-check"></i> 비조정대상지역</span>';
        isRegulatedAreaDisplay.style.background = 'rgba(46, 160, 67, 0.1)';
        isRegulatedAreaDisplay.style.borderColor = 'var(--success)';
    }

    // 2. 노후도 계산
    let agingText = "알 수 없음 (정보 없음)";
    if (approvalDate && approvalDate !== "알 수 없음" && approvalDate.length >= 4) {
        const currentYear = new Date().getFullYear();
        // Extract 4 digits year from string
        const yearMatch = approvalDate.match(/\d{4}/);
        if (yearMatch) {
            const approvedYear = parseInt(yearMatch[0], 10);
            const age = currentYear - approvedYear;
            agingText = `${age}년차 (사용승인: ${approvedYear}년)`;
        }
    }
    agingDisplay.innerHTML = agingText;
}

// 입력 정보가 수동으로 변경될 때 노후도 자동 재계산
document.getElementById('approvalDate').addEventListener('change', (e) => {
    if(currentCaseData) {
        currentCaseData.approval_date = e.target.value;
        calculateAutoFields(currentCaseData.address, e.target.value);
    }
});

document.getElementById('propertyType').addEventListener('change', (e) => {
    if(currentCaseData) {
        currentCaseData.property_type = e.target.value;
    }
});

// 2. 9단계 심층 분석 시작
startBtn.addEventListener('click', async () => {
    if (!currentCaseData) return;

    // UI 상태 업데이트
    secondaryInputScreen.style.display = 'none';
    finalReport.classList.add('hidden');
    loadingState.style.display = 'block';
    
    let houseCountStr = document.getElementById('houseCount').value;
    let houseCount = 0;
    if (houseCountStr.includes("1")) houseCount = 1;
    else if (houseCountStr.includes("2")) houseCount = 2;
    else if (houseCountStr.includes("3")) houseCount = 3;

    const madangsUrlEl = document.getElementById('madangsUrl');
    const requestData = {
        ...currentCaseData,
        case_number: caseNumberInput.value.trim(),
        address_hint: currentCaseData.address || "",
        property_type: document.getElementById('propertyType').value,
        house_count: houseCount,
        investor_type: document.getElementById('investorType').value,
        investment_duration: document.getElementById('investmentDuration').value,
        target_return_rate: parseFloat(document.getElementById('targetReturnRate').value) || 20.0,
        is_regulated_area: document.getElementById('isRegulatedArea').value === 'true',
        calculated_aging: agingDisplay.innerText,
        madangs_url: madangsUrlEl ? madangsUrlEl.value.trim() : ""
    };

    try {
        let response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        let data = await response.json();
        
        if (response.ok && data.status === "processing") {
            const taskId = data.task_id;
            // 폴링 루프 (5초 간격)
            while (true) {
                await new Promise(resolve => setTimeout(resolve, 5000));
                try {
                    const statusRes = await fetch(`/api/analyze/status/${taskId}`);
                    if (!statusRes.ok) continue;
                    const statusData = await statusRes.json();
                    
                    if (statusData.status !== "processing") {
                        data = statusData;
                        break;
                    }
                } catch (err) {
                    console.error("Polling error:", err);
                }
            }
        }

        loadingState.style.display = 'none';

        if (data.status === "success") {
            renderFinalReport(data.data.analysis, data.data);
            finalReport.classList.remove('hidden');
            
            // 이미지 로드 처리 (전경사진, 위치도, 내부구조도)
            const safeCaseNum = requestData.case_number;
            
            
                                    // 1. 전경사진, 위치도, 내부구조도 캐러셀
            const carousel = document.getElementById('imageCarousel');
            const placeholderEl = document.getElementById('imagePlaceholder');
            const scrollHint = document.getElementById('scrollHint');
            
            const imgPhoto = document.getElementById('resultImagePhoto');
            const imgMap = document.getElementById('resultImageMap');
            const imgStruct = document.getElementById('resultImageStructure');
            
            if (carousel && placeholderEl) {
                let loadedCount = 0;
                let errorCount = 0;
                
                const checkDisplay = () => {
                    if (loadedCount > 0) {
                        carousel.style.display = 'flex';
                        placeholderEl.style.display = 'none';
                        if (loadedCount > 1 && scrollHint) {
                            scrollHint.style.display = 'block'; // 2장 이상이면 스크롤 안내
                        }
                    } else if (loadedCount + errorCount === 3) {
                        placeholderEl.innerHTML = `<i class="fa-solid fa-image-slash" style="font-size: 3rem; color: var(--danger); margin-bottom: 10px;"></i><p style="color: var(--danger); font-size: 0.9rem;">사진을 불러올 수 없습니다.</p>`;
                    }
                };

                const onLoad = () => { loadedCount++; checkDisplay(); };
                const onError = (e) => { 
                    if(e.target && e.target.parentElement) {
                        e.target.parentElement.style.display = 'none'; // 에러난 사진 컨테이너 숨김
                    }
                    errorCount++; 
                    checkDisplay(); 
                };

                imgPhoto.onload = onLoad;
                imgMap.onload = onLoad;
                imgStruct.onload = onLoad;
                
                imgPhoto.onerror = onError;
                imgMap.onerror = onError;
                imgStruct.onerror = onError;


                imgPhoto.src = `/api/download_photo/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
                imgMap.src = `/api/download_map/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
                imgStruct.src = `/api/download_structure/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
            }


            // 3. 내부구조도
            const structureEl = document.getElementById('structureImage');
            const structurePlaceholder = document.getElementById('structurePlaceholder');
            if (structureEl && structurePlaceholder) {
                structureEl.src = `/api/download_structure/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
                structureEl.onload = () => {
                    structureEl.style.display = 'block';
                    structurePlaceholder.style.display = 'none';
                };
            }

            // 다운로드 버튼 이벤트 처리
            const downloadBtn = document.getElementById('downloadBtn');
            if (downloadBtn) {
                const newBtn = downloadBtn.cloneNode(true);
                downloadBtn.parentNode.replaceChild(newBtn, downloadBtn);
                newBtn.addEventListener('click', async () => {
                    const originalText = newBtn.innerText;
                    newBtn.innerText = "생성 중...";
                    newBtn.disabled = true;
                    try {
                        const response = await fetch(`/api/download/${encodeURIComponent(safeCaseNum)}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ markdown: data.data.analysis || "내용이 없습니다." })
                        });
                        
                        if (!response.ok) throw new Error("서버 에러");
                        
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `${safeCaseNum}_분석보고서.docx`;
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                        window.URL.revokeObjectURL(url);
                    } catch (e) {
                        console.error(e);
                        alert("Word 문서 생성 및 다운로드 중 오류가 발생했습니다.");
                    } finally {
                        newBtn.innerText = originalText;
                        newBtn.disabled = false;
                    }
                });
            }

            const downloadPdfBtn = document.getElementById('downloadPdfBtn');
            if (downloadPdfBtn) {
                const newPdfBtn = downloadPdfBtn.cloneNode(true);
                downloadPdfBtn.parentNode.replaceChild(newPdfBtn, downloadPdfBtn);
                newPdfBtn.addEventListener('click', () => {
                    const element = document.getElementById('finalReport');
                    const buttonsContainer = document.getElementById('downloadButtonsContainer');
                    const scrollHint = document.getElementById('scrollHint');
                    
                    try {
                        if (typeof html2pdf === 'undefined') {
                            alert("PDF 라이브러리를 불러오지 못했습니다. 페이지를 새로고침 해주세요.");
                            return;
                        }
                        
                        // 숨길 요소들 임시 숨김 처리
                        if(buttonsContainer) buttonsContainer.style.display = 'none';
                        if(scrollHint) scrollHint.style.display = 'none';
                        
                        const opt = {
                            margin:       [10, 10, 10, 10],
                            filename:     `${safeCaseNum}_화면캡쳐.pdf`,
                            image:        { type: 'jpeg', quality: 0.98 },
                            html2canvas:  { scale: 2, useCORS: true, backgroundColor: '#13141c' },
                            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
                        };
                        
                        html2pdf().set(opt).from(element).save().then(() => {
                            // 캡쳐 완료 후 다시 표시
                            if(buttonsContainer) buttonsContainer.style.display = 'flex';
                            if(scrollHint) scrollHint.style.display = 'block';
                        }).catch(err => {
                            console.error("PDF 캡쳐 에러:", err);
                            if(buttonsContainer) buttonsContainer.style.display = 'flex';
                            if(scrollHint) scrollHint.style.display = 'block';
                            alert("PDF 캡쳐에 실패했습니다.");
                        });
                    } catch (e) {
                        console.error(e);
                        if(buttonsContainer) buttonsContainer.style.display = 'flex';
                        if(scrollHint) scrollHint.style.display = 'block';
                    }
                });
            }

            const viewIssuesBtn = document.getElementById('viewIssuesBtn');
            if (viewIssuesBtn) {
                const newIssuesBtn = viewIssuesBtn.cloneNode(true);
                viewIssuesBtn.parentNode.replaceChild(newIssuesBtn, viewIssuesBtn);
                
                const extractRegionKeyword = (addr) => {
                    if (!addr) return '';
                    const guDongMatch = addr.match(/([가-힣]+구\s+[가-힣0-9]+(?:동|읍|면))/);
                    if (guDongMatch) return guDongMatch[1];
                    const dongMatch = addr.match(/([가-힣0-9]+(?:동|읍|면))/);
                    if (dongMatch) return dongMatch[1];
                    const guMatch = addr.match(/([가-힣]+구)/);
                    if (guMatch) return guMatch[1];
                    const parts = addr.split(/\s+/);
                    if (parts.length >= 3) return parts[2];
                    return addr;
                };

                newIssuesBtn.addEventListener('click', () => {
                    const address = (currentCaseData && currentCaseData.address) || '';
                    const region = extractRegionKeyword(address);
                    if (region) {
                        window.open(`/issues.html?region=${encodeURIComponent(region)}`, '_blank');
                    } else {
                        window.open('/issues.html', '_blank');
                    }
                });
            }
            
        } else {
            let errorText = data ? (data.message || '알 수 없는 에러') : '알 수 없는 에러';
            showError(`분석 서버 오류: ${errorText}`);
            secondaryInputScreen.style.display = 'flex';
        }
    } catch (err) {
        console.error(err);
        loadingState.style.display = 'none';
        showError(`통신 오류: ${err.message}`);
        secondaryInputScreen.style.display = 'flex';
    }
});

// 마크다운에서 1~9단계 파싱 및 렌더링
function renderFinalReport(markdownText, caseData = null) {
    if(!markdownText) return;
    
    // 섹션별 분리 로직 (간단한 정규식 또는 split)
    // AI가 # 1. 요약, # 2. 기본정보 형태로 출력하도록 프롬프트를 짰음
    
    // 파싱을 위한 편의 함수 (모든 레벨의 마크다운 헤딩 `#`, `##`, `###` 및 번호 형태 지원)
    const extractSection = (num, text) => {
        // 정규식 1: # 1. 요약 (가장 표준적인 마크다운)
        let regex = new RegExp(`(?:^|\\n)#{1,6}\\s*${num}\\.\\s*[^\\n]*\\n([\\s\\S]*?)(?=(?:^|\\n)#{1,6}\\s*\\d+\\.\\s*|$)`, 'i');
        let match = text.match(regex);
        if(match) return match[1].trim();

        // 정규식 2: 1. 요약 (# 기호가 없는 경우)
        regex = new RegExp(`(?:^|\\n)${num}\\.\\s*[^\\n]*\\n([\\s\\S]*?)(?=(?:^|\\n)\\d+\\.\\s*|$)`, 'i');
        match = text.match(regex);
        if(match) return match[1].trim();
        
        // 정규식 3: **1. 요약** 등 마크다운 기호가 혼재된 경우
        regex = new RegExp(`(?:^|\\n)[#\\*\\s]*${num}\\.\\s*[^\\n]*\\n([\\s\\S]*?)(?=(?:^|\\n)[#\\*\\s]*\\d+\\.\\s*|$)`, 'i');
        match = text.match(regex);
        if(match) return match[1].trim();
        
        return null; // 추출 실패
    };

    // API 에러 처리
    if (markdownText.includes("⚠️ 심층 분석 중 오류 발생")) {
        document.getElementById('report-section-0').innerHTML = `<div style="color:var(--danger); padding: 20px; background: rgba(248, 81, 73, 0.1); border-radius: 8px; border: 1px solid var(--danger);"><strong>API 오류 발생:</strong><br><br>${markdownText}</div>`;
        return;
    }

    // 0. 요약은 "1. 요약"에서 추출
    let rawSummary = extractSection(1, markdownText);
    
    // 만약 전체적으로 추출이 하나도 안 되었다면, 에러 메시지이거나 AI 포맷이 완전히 깨진 경우임
    if (rawSummary === null) {
        document.getElementById('report-section-0').innerHTML = `<div style="color:var(--warning); padding: 20px; background: rgba(255, 165, 0, 0.1); border-radius: 8px; border: 1px solid var(--warning);"><strong>목차 추출 실패 (AI가 지정된 포맷을 따르지 않음). 아래는 AI가 작성한 원본입니다:</strong><br><br>${marked.parse(markdownText)}</div>`;
        return; // 전체 원문만 출력하고 종료
    }
    
    let summaryHtml = marked.parse(rawSummary || "내용이 없습니다.");
    
    let section10Text = extractSection(10, markdownText) || "";

    // Go/Neutral/Danger 추출 (섹션 10에서)
    const badge = document.getElementById('decisionBadge');
    
    if (caseData && caseData.is_ended) {
        // 과거/종결된 사건 표시
        const finalDate = caseData.final_date || "";
        const finalResult = caseData.final_result || caseData.status || "종결";
        badge.innerText = `${finalResult} (${finalDate})`;
        badge.className = 'badge';
        badge.style.fontWeight = 'bold';
        badge.style.fontSize = '1.05rem';
        badge.style.padding = '8px 18px';
        
        if (finalResult.includes("낙찰")) {
            badge.style.background = 'rgba(46, 160, 67, 0.15)';
            badge.style.color = '#2ea043'; // Green
            badge.style.borderColor = '#2ea043';
        } else if (finalResult.includes("변경") || finalResult.includes("대기")) {
            badge.style.background = 'rgba(210, 153, 34, 0.15)';
            badge.style.color = '#d29922'; // Yellow/Orange
            badge.style.borderColor = '#d29922';
        } else {
            // 유찰, 취소, 취하 등
            badge.style.background = 'rgba(248, 81, 73, 0.15)';
            badge.style.color = '#f85149'; // Red
            badge.style.borderColor = '#f85149';
        }
    } else {
        // 정규식을 유연하게 작성 (종결/유찰/낙찰 등 신규 판정도 수용)
        const goMatch = section10Text.match(/투자\s*(?:판정|여부|판단)\s*[:\-]?\s*\[?\s*([^\]\n\r]+)\]?/i);
        if (goMatch) {
            let decision = goMatch[1].trim();
            if(decision.toUpperCase() === 'NEUTRAL') decision = 'Neutral';
            else if(decision.toUpperCase() === 'DANGER') decision = 'Danger';
            else if(decision.toUpperCase() === 'GO') decision = 'GO';
            
            badge.innerText = decision;
            badge.className = 'badge';
            badge.style.fontWeight = 'bold';
            
            if (decision === 'GO' || decision.includes("낙찰")) {
                badge.style.background = 'rgba(46, 160, 67, 0.15)';
                badge.style.color = '#2ea043'; // Green
                badge.style.borderColor = '#2ea043';
            } else if (decision === 'Neutral' || decision.includes("변경") || decision.includes("대기")) {
                badge.style.background = 'rgba(210, 153, 34, 0.15)';
                badge.style.color = '#d29922'; // Yellow/Orange
                badge.style.borderColor = '#d29922';
            } else {
                badge.style.background = 'rgba(248, 81, 73, 0.15)';
                badge.style.color = '#f85149'; // Red
                badge.style.borderColor = '#f85149';
            }
        }
    }

    document.getElementById('report-section-0').innerHTML = summaryHtml;
    
    // 1~4는 2~5에서 추출
    document.getElementById('report-section-1').innerHTML = marked.parse(extractSection(2, markdownText) || "내용이 추출되지 않았습니다.");
    document.getElementById('report-section-2').innerHTML = marked.parse(extractSection(3, markdownText) || "내용이 추출되지 않았습니다.");
    document.getElementById('report-section-3').innerHTML = marked.parse(extractSection(4, markdownText) || "내용이 추출되지 않았습니다.");
    document.getElementById('report-section-4').innerHTML = marked.parse(extractSection(5, markdownText) || "내용이 추출되지 않았습니다.");
    
    // 5~10은 6~11에서 추출 (원문 프롬프트 구조에 맞춰)
    document.getElementById('report-section-5').innerHTML = marked.parse(extractSection(6, markdownText) || "내용이 추출되지 않았습니다.");
    document.getElementById('report-section-6').innerHTML = marked.parse(extractSection(7, markdownText) || "내용이 추출되지 않았습니다.");
    document.getElementById('report-section-7').innerHTML = marked.parse(extractSection(8, markdownText) || "내용이 추출되지 않았습니다.");
    document.getElementById('report-section-8').innerHTML = marked.parse(extractSection(9, markdownText) || "내용이 추출되지 않았습니다.");
    
    // 차트 데이터용 JSON 파싱 (에러 방지 강화)
    let chartData = null;
    let jsonStrMatch = markdownText.match(/```(?:json)?\s*([\s\S]*?)\s*```/i);
    let jsonStr = jsonStrMatch ? jsonStrMatch[1] : markdownText;
    
    // JSON 객체 부분만 긁어내기
    const blockMatch = jsonStr.match(/\{[\s\S]*"chart_data"[\s\S]*\}/i);
    if(blockMatch) {
        try {
            const parsed = JSON.parse(blockMatch[0]);
            if(parsed.chart_data) chartData = parsed.chart_data;
        } catch(e) {
            console.error("JSON 파싱 에러:", e);
        }
    }
    
    // 1. 기본정보 텍스트에서 AI가 찾아낸 사용승인일자가 있다면 UI 업데이트
    const basicInfoText = document.getElementById('report-section-1').innerText;
    const dateMatch = basicInfoText.match(/사용승인일자\s*[:\-]?\s*([0-9]{4}[^ \n]*)/);
    if (dateMatch && (!currentCaseData.approval_date || currentCaseData.approval_date === "알 수 없음")) {
        const foundDate = dateMatch[1].trim();
        document.getElementById('approvalDate').value = foundDate;
        currentCaseData.approval_date = foundDate;
        calculateAutoFields(currentCaseData.address, foundDate);
    }

    // JSON 블록 제거 (```json ... ```)
    section10Text = section10Text.replace(/```json[\s\S]*?```/, '').trim();
    
    // 투자 판정(GO/Neutral/Danger) 부각 처리
    section10Text = section10Text.replace(/\[투자 판정:\s*(GO|Neutral|Danger)\]/ig, (match, p1) => {
        let color = "var(--danger, red)"; // Default to red
        if (p1.toUpperCase() === "GO") color = "var(--danger, red)"; // User specifically requested "빨간색 진한 글씨로 부각시켜줘"
        else if (p1.toUpperCase() === "NEUTRAL") color = "var(--warning, orange)";
        else if (p1.toUpperCase() === "DANGER") color = "var(--danger, red)";
        
        return `<span style="color: ${color}; font-weight: bold; font-size: 1.5rem; display: block; margin-bottom: 15px; border-bottom: 2px solid ${color}; padding-bottom: 5px;">${match.toUpperCase()}</span>`;
    });
    
    const section9El = document.getElementById('report-section-9');
    if(section9El) {
        // marked.parse를 통과하면 일부 스타일이 사라질 수 있으므로, 판정 태그는 파싱 이후에 치환하거나 marked 설정에서 허용해야 함
        // marked.js 기본 설정은 인라인 HTML을 허용함
        section9El.innerHTML = marked.parse(section10Text);
    }
    
    // 차트 렌더링
    if(chartData) {
        renderInfographics(chartData);
    }
}

function showError(msg) {
    errorMsg.innerText = msg;
}

function formatNumber(numStr) {
    if (!numStr) return "0";
    return Number(numStr).toLocaleString();
}

function toggleHouseCount() {
    const pType = document.getElementById('propertyType').value;
    const hContainer = document.getElementById('houseCountContainer');
    if (pType.includes('주택') || pType.includes('아파트') || pType.includes('빌라')) {
        hContainer.style.display = 'flex';
    } else {
        hContainer.style.display = 'none';
    }
}

// 금액 축약 포맷터 (만 단위)
function formatNumberMan(num) {
    if (!num) return "0";
    return Math.round(num / 10000).toLocaleString() + "만";
}

// 인포그래픽 렌더링 함수
function renderInfographics(data) {
    if(!data) return;

    const salePrice = data.conservative_sale_price || 0;
    const targetProfit = data.target_profit || 0;
    const cgTax = data.capital_gains_tax || 0;
    const capex = data.capex_and_eviction || 0;
    const interest = data.interest_and_acq_tax || 0;
    const maxBidPrice = data.max_bidding_price || 0;

    // 1. Waterfall Chart (추천 입찰가 역산)
    const waterfallContainer = document.getElementById('dynamic-waterfall-chart');
    if(waterfallContainer) {
        waterfallContainer.style.display = 'block';
        const maxVal = salePrice || 1;
        
        waterfallContainer.innerHTML = `
            <h5 class="infographic-title"><i class="fa-solid fa-chart-bar"></i> 한계 입찰가 역산 워터폴 시뮬레이션</h5>
            <div class="waterfall-chart">
                ${createWaterfallRow('보수적 매도가', salePrice, maxVal, 'bar-start')}
                ${createWaterfallRow('목표 수익 (-)', targetProfit, maxVal, 'bar-deduction')}
                ${createWaterfallRow('양도소득세 (-)', cgTax, maxVal, 'bar-deduction')}
                ${createWaterfallRow('CAPEX/명도 (-)', capex, maxVal, 'bar-deduction')}
                ${createWaterfallRow('금융/취득세 (-)', interest, maxVal, 'bar-deduction')}
                ${createWaterfallRow('한계 상한가 (=)', maxBidPrice, maxVal, 'bar-final')}
            </div>
        `;
        
        // 애니메이션 트릭을 위해 잠시 0%로 뒀다가 풀기 (브라우저 리플로우 후)
        setTimeout(() => {
            const bars = waterfallContainer.querySelectorAll('.waterfall-bar');
            bars.forEach(bar => {
                const targetWidth = bar.getAttribute('data-width');
                bar.style.width = targetWidth;
            });
        }, 100);
    }

    // 2. Sensitivity Analysis (민감도 분석 슬라이더)
    const sensitivityContainer = document.getElementById('dynamic-sensitivity-chart');
    if(sensitivityContainer) {
        sensitivityContainer.style.display = 'block';
        
        sensitivityContainer.innerHTML = `
            <h5 class="infographic-title"><i class="fa-solid fa-sliders"></i> 낙찰가에 따른 실질(Net) 수익금 시뮬레이터</h5>
            <div class="sensitivity-panel">
                <div class="slider-group">
                    <div class="slider-header">
                        <span>시뮬레이션 입찰가</span>
                        <span id="sliderDisplayVal" class="slider-value">${formatNumberMan(maxBidPrice)}원</span>
                    </div>
                    <input type="range" id="bidSlider" 
                           min="${maxBidPrice * 0.8}" 
                           max="${Math.min(salePrice * 0.95, maxBidPrice * 1.2)}" 
                           value="${maxBidPrice}" step="1000000">
                </div>
                <div class="sensitivity-result">
                    예상 Net 수익금: <br><span id="netProfitDisplay">${formatNumberMan(targetProfit)}원</span>
                </div>
            </div>
        `;
        
        const slider = document.getElementById('bidSlider');
        const sliderDisplay = document.getElementById('sliderDisplayVal');
        const netProfitDisplay = document.getElementById('netProfitDisplay');
        
        if(slider) {
            slider.addEventListener('input', (e) => {
                const currentBid = parseInt(e.target.value, 10);
                sliderDisplay.innerText = formatNumberMan(currentBid) + "원";
                // Net 수익금 = 매도가 - 현재입찰가 - 양도세 - CAPEX - 제세공과
                const currentProfit = salePrice - currentBid - cgTax - capex - interest;
                netProfitDisplay.innerText = formatNumberMan(currentProfit) + "원";
                if(currentProfit < 0) {
                    netProfitDisplay.style.color = "var(--danger)";
                    netProfitDisplay.style.textShadow = "0 0 10px var(--danger)";
                } else {
                    netProfitDisplay.style.color = "#fff";
                    netProfitDisplay.style.textShadow = "0 0 10px var(--neon-purple)";
                }
            });
        }
    }

    // 3. Exit Flowchart (출구 전략)
    const exitContainer = document.getElementById('dynamic-exit-flowchart');
    if(exitContainer) {
        exitContainer.style.display = 'block';
        const stTax = data.short_term_tax_rate || 77;
        const ltTax = data.long_term_tax_rate || 20;
        
        exitContainer.innerHTML = `
            <h5 class="infographic-title"><i class="fa-solid fa-code-branch"></i> 타임라인별 Exit 전략 모델</h5>
            <div class="flowchart">
                <div class="flow-node highlight">
                    <h5>낙찰 및 명도</h5>
                    <p>상한가: ${formatNumberMan(maxBidPrice)}</p>
                </div>
                <div class="flow-arrow"><i class="fa-solid fa-arrow-right"></i></div>
                <div class="flow-node">
                    <h5>단기 매도 (1년 내)</h5>
                    <p>양도세율: ${stTax}%</p>
                    <p>기대수익: Low</p>
                </div>
                <div class="flow-arrow"><i class="fa-solid fa-arrow-right"></i></div>
                <div class="flow-node">
                    <h5>전월세 임대 셋팅</h5>
                    <p>보증금 회수 (투자금 방어)</p>
                </div>
                <div class="flow-arrow"><i class="fa-solid fa-arrow-right"></i></div>
                <div class="flow-node highlight">
                    <h5>일반 과세 매도 (2년 후)</h5>
                    <p>양도세율: ${ltTax}%</p>
                    <p>기대수익: High</p>
                </div>
            </div>
        `;
    }
}

function createWaterfallRow(label, value, maxVal, colorClass) {
    const pct = Math.max(2, (value / maxVal) * 100);
    return `
        <div class="waterfall-row">
            <div class="waterfall-label">${label}</div>
            <div class="waterfall-bar-container">
                <div class="waterfall-bar ${colorClass}" data-width="${pct}%" style="width: 0%;"></div>
                <div class="waterfall-value">${formatNumberMan(value)}</div>
            </div>
        </div>
    `;
}

window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    const caseParam = params.get('case');
    console.log("[Auto-Analyze] DOMContentLoaded caseParam:", caseParam);
    if (caseParam && typeof caseNumberInput !== 'undefined' && caseNumberInput) {
        caseNumberInput.value = caseParam;
        if (typeof searchCaseBtn !== 'undefined' && searchCaseBtn && !searchCaseBtn.disabled) {
            isAutoAnalyze = true;
            console.log("[Auto-Analyze] Setting isAutoAnalyze = true and triggering searchCaseBtn.click()");
            searchCaseBtn.click();
        }
    }
});
