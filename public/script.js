// --- Authentication ---
document.addEventListener('DOMContentLoaded', () => {
    const overlay = document.getElementById('loginOverlay');
    const pwdInput = document.getElementById('passwordInput');
    const loginBtn = document.getElementById('loginBtn');

    // 영구 localStorage 자동 로그인 캐시 즉시 폐기 (새 탭·재접속 시 항상 비밀번호 입력 필수)
    try {
        localStorage.removeItem('agy_auth_exp');
        localStorage.removeItem('agy_admin_key');
        localStorage.removeItem('agy_admin_exp');
    } catch (e) {}

    if (sessionStorage.getItem('agy_session_v2') === 'active') {
        sessionStorage.setItem('auth_token', 'verified');
        document.documentElement.classList.add('session-authenticated');
        overlay.classList.add('hidden');
    } else {
        sessionStorage.removeItem('auth_token');
        sessionStorage.removeItem('admin_board_key');
        sessionStorage.removeItem('is_admin_verified');
        sessionStorage.removeItem('agy_admin_session_v2');
        document.documentElement.classList.remove('session-authenticated');
        overlay.classList.remove('hidden');
    }

    if (sessionStorage.getItem('agy_admin_session_v2') === 'active' && sessionStorage.getItem('admin_board_key')) {
        sessionStorage.setItem('is_admin_verified', '1');
        adminAuthKey = sessionStorage.getItem('admin_board_key') || '';
    }

    // Fetch and display daily visitor count
    fetch('/api/visitor_count')
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                const el = document.getElementById('visitorCountValue');
                if(el) el.innerText = data.count;
            }
        })
        .catch(err => console.error("Failed to fetch visitor count:", err));


    const attemptLogin = async () => {
        const pwd = pwdInput.value.trim();
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
                try {
                    localStorage.removeItem('agy_auth_exp');
                    localStorage.removeItem('agy_admin_key');
                    localStorage.removeItem('agy_admin_exp');
                } catch (e) {}
                sessionStorage.setItem('agy_session_v2', 'active');
                sessionStorage.setItem('auth_token', 'verified');
                if (data.user_type === 'admin') {
                    sessionStorage.setItem('admin_board_key', pwd);
                    sessionStorage.setItem('is_admin_verified', '1');
                    sessionStorage.setItem('agy_admin_session_v2', 'active');
                    sessionStorage.removeItem('member_auth_pin');
                    sessionStorage.setItem('member_can_analyze', '1');
                    adminAuthKey = pwd;
                    if (typeof updateAdminUI === 'function') updateAdminUI();
                } else {
                    sessionStorage.removeItem('admin_board_key');
                    sessionStorage.removeItem('is_admin_verified');
                    sessionStorage.removeItem('agy_admin_session_v2');
                    sessionStorage.setItem('member_auth_pin', pwd);
                    sessionStorage.setItem('member_can_analyze', data.can_use_rights_analysis ? '1' : '0');
                    sessionStorage.setItem('member_user_name', data.user_name || '');
                    adminAuthKey = '';
                    if (typeof updateAdminUI === 'function') updateAdminUI();
                }
                if (typeof fetchAnalysisAccessConfig === 'function') {
                    await fetchAnalysisAccessConfig();
                } else if (typeof applyAnalysisAccessState === 'function') {
                    applyAnalysisAccessState();
                }
                pwdInput.value = '';
                document.documentElement.classList.add('session-authenticated');
                overlay.classList.add('hidden');
                if (data.message && (data.user_type === 'member' || data.user_type === 'admin')) {
                    alert(data.message);
                }
                if (window.pendingAutoCaseParam && typeof caseNumberInput !== 'undefined' && caseNumberInput && typeof searchCaseBtn !== 'undefined' && searchCaseBtn) {
                    const lockedForUser = !isUserAllowedForRightsAnalysis();
                    if (!lockedForUser && !searchCaseBtn.disabled) {
                        caseNumberInput.value = window.pendingAutoCaseParam;
                        window.pendingAutoCaseParam = null;
                        isAutoAnalyze = true;
                        searchCaseBtn.click();
                    }
                }
            } else {
                alert(data.message || '비밀번호가 일치하지 않습니다.');
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

    const lockSessionBtnHeader = document.getElementById('lockSessionBtnHeader');
    if (lockSessionBtnHeader) {
        lockSessionBtnHeader.addEventListener('click', () => {
            performFullSessionLock();
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

    if (!isUserAllowedForRightsAnalysis()) {
        applyAnalysisAccessState();
        showError((window.analysisAccessState && window.analysisAccessState.message) || "현재 권리분석은 관리자 및 지정 허용 회원만 이용할 수 있습니다.");
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
            body: JSON.stringify({
                case_number: caseNumber,
                admin_key: getEffectiveAdminKey(),
                user_pin: getEffectiveMemberPin()
            })
        });
        const data = await response.json();
        if (data && data.status === "restricted") {
            window.analysisAccessState = {
                ...(window.analysisAccessState || {}),
                access_mode: data.access_mode || 'admin_only',
                admin_only: Boolean(data.admin_only),
                member_allowed: false,
                message: data.message || "권리분석 이용 제한 중입니다."
            };
            applyAnalysisAccessState();
            showError(data.message || "현재 권리분석은 관리자 및 지정 허용 회원만 이용할 수 있습니다.");
            return;
        }

        if (response.ok && data.status === "success") {
            const results = data.data;
            if (results && results.length > 0) {
                const subMatch = caseNumber.match(/(?:\(|\[|물건\s*)(\d{1,2})(?:\)|\])?\s*$/);
                const reqItemNo = data.requested_item_no || (subMatch ? subMatch[1] : "");
                const hasParenthesis = Boolean(data.has_sub_number) || Boolean(reqItemNo) || /\(\d+\)/.test(caseNumber);
                const mustSelectManually = hasParenthesis || results.length > 1;

                renderAddressList(results, {
                    mustSelectManually,
                    requestedItemNo: reqItemNo,
                    hasParenthesis,
                });
                secondaryInputScreen.style.display = 'flex';
                
                let targetBtn = null;
                const btns = addressListContainer.querySelectorAll('.address-btn');
                
                // 지번(예: 24-27)까지 포함한 전체 주소 토큰 + (물건번호) 정밀 가중치 매칭
                const hintStr = (window.addressHintParam || "").trim();
                const hintTokens = hintStr ? hintStr.split(/\s+/).filter(Boolean) : [];
                if (reqItemNo || hintTokens.length > 0) {
                    let bestMatchIndex = 0;
                    let bestScore = -999999;
                    for (let i = 0; i < results.length; i++) {
                        let score = 0;
                        const item = results[i];
                        const addr = item.address || "";
                        const raw = item.raw_text || "";
                        const itemNo = String(item.item_no || "").trim();

                        if (reqItemNo) {
                            if (item.exact_item_match || itemNo === String(reqItemNo)) {
                                score += 2000;
                            } else if (itemNo && itemNo !== String(reqItemNo)) {
                                score -= 2000;
                            }
                        }

                        for (const t of hintTokens) {
                            if (addr.includes(t) || raw.includes(t)) {
                                // 본번-부번(예: 24-27) 일치 시 최우선 가중치 부여
                                if (/^\d+(-\d+)?$/.test(t)) {
                                    score += 250;
                                } else {
                                    score += 35;
                                }
                            }
                        }

                        if (score > bestScore) {
                            bestScore = score;
                            bestMatchIndex = i;
                        }
                    }
                    if (bestScore > 0 && btns[bestMatchIndex]) {
                        targetBtn = btns[bestMatchIndex];
                    }
                }
                
                if (!targetBtn && btns.length > 0) {
                    targetBtn = btns[0];
                }
                
                if (targetBtn) {
                    targetBtn.click();
                }

                // [핵심] 사건번호 뒤 괄호(물건번호)가 있거나 동일 사건번호 물건이 복수(2건 이상)일 때는
                // 바로 권리분석을 자동 실행하지 않고 사용자가 직접 물건을 확인·선택한 뒤 시작하도록 보장!
                if (mustSelectManually) {
                    if (typeof isAutoAnalyze !== 'undefined') {
                        isAutoAnalyze = false;
                    }
                    setTimeout(() => {
                        secondaryInputScreen.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 150);
                } else if (typeof isAutoAnalyze !== 'undefined' && isAutoAnalyze && results.length === 1) {
                    isAutoAnalyze = false;
                    setTimeout(() => {
                        if (startBtn && !startBtn.disabled) {
                            startBtn.click();
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
        const isLockedForUser = !isUserAllowedForRightsAnalysis();
        searchCaseBtn.disabled = isLockedForUser;
    }
});

// 주소 리스트 렌더링 (관할법원 · 사건/물건번호 · 용도 · 지번주소 · 감정가/최저가/면적 명확 표시)
function renderAddressList(results, meta = {}) {
    addressListContainer.innerHTML = '';

    if (meta.mustSelectManually) {
        const guideBanner = document.createElement('div');
        guideBanner.style.cssText = 'padding: 13px 16px; margin-bottom: 6px; border-radius: 10px; background: linear-gradient(135deg, rgba(0, 240, 255, 0.14), rgba(187, 0, 255, 0.14)); border: 1px solid rgba(0, 240, 255, 0.55); color: #f8fafc; font-size: 0.94rem; line-height: 1.55; text-align: left;';
        const reasonTxt = results.length > 1
            ? `동일 사건번호(또는 복수 물건번호·타 관할법원) 물건이 <strong>총 ${results.length}건</strong> 조회되었습니다.`
            : `괄호 물건번호가 포함된 사건(<strong>${meta.requestedItemNo ? '(' + meta.requestedItemNo + ')번 물건' : '지정 물건'}</strong>)이 조회되었습니다.`;
        guideBanner.innerHTML = `<i class="fa-solid fa-hand-pointer" style="color:var(--neon-blue); margin-right:6px;"></i> ${reasonTxt} 아래 목록에서 <strong>분석할 정확한 물건을 확인·선택</strong>하신 후 하단의 <strong>[9단계 심층 권리분석 시작]</strong> 버튼을 눌러주세요.`;
        addressListContainer.appendChild(guideBanner);
    }

    results.forEach((item, index) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'address-btn';
        btn.style.cssText = 'padding: 16px; background: rgba(0,0,0,0.45); border: 1px solid var(--glass-border); border-radius: 10px; color: #fff; text-align: left; cursor: pointer; transition: all 0.2s;';

        const courtBadge = item.court
            ? `<span style="display:inline-block; padding:2px 8px; border-radius:5px; background:rgba(0,240,255,0.16); border:1px solid rgba(0,240,255,0.45); color:#67e8f9; font-size:0.8rem; font-weight:700; margin-right:6px;">${item.court}</span>`
            : '';
        const caseLabel = item.case_no_full || (item.item_no ? `${caseNumberInput.value.replace(/\(\d+\)\s*$/, '').trim()}(${item.item_no})` : `물건 ${index + 1}`);
        const exactBadge = item.exact_item_match
            ? `<span style="display:inline-block; padding:2px 8px; border-radius:5px; background:rgba(16,185,129,0.22); border:1px solid #10b981; color:#6ee7b7; font-size:0.78rem; font-weight:800; margin-left:6px;">🎯 요청 물건번호 일치</span>`
            : '';
        const propBadge = item.property_type
            ? `<span style="display:inline-block; padding:2px 8px; border-radius:5px; background:rgba(187,0,255,0.18); border:1px solid rgba(187,0,255,0.45); color:#e9d5ff; font-size:0.78rem; font-weight:700; margin-left:6px;">${item.property_type}</span>`
            : '';
        const statusBadge = item.status
            ? `<span style="display:inline-block; padding:2px 8px; border-radius:5px; background:rgba(245,158,11,0.18); border:1px solid rgba(245,158,11,0.45); color:#fde68a; font-size:0.78rem; font-weight:700; margin-left:6px;">${item.status}</span>`
            : '';

        const areaParts = [];
        if (item.building_area) areaParts.push(`건물 ${item.building_area}`);
        else if (item.pyeong) areaParts.push(`${item.pyeong}평`);
        if (item.land_area) areaParts.push(`토지 ${item.land_area}`);
        const areaDisplay = areaParts.length > 0 ? areaParts.join(' / ') : '면적 상세조회';

        btn.innerHTML = `
            <div style="display:flex; align-items:center; flex-wrap:wrap; gap:4px; margin-bottom:7px;">
                ${courtBadge}
                <strong style="font-size:1.02rem; color:#f8fafc;">${caseLabel}</strong>
                ${propBadge}
                ${statusBadge}
                ${exactBadge}
            </div>
            <div style="font-size:1.06rem; font-weight:700; color:#ffffff; margin-bottom:6px;">📍 ${item.address || '주소 정보 없음'}</div>
            <div style="font-size:0.88rem; color:var(--text-muted); line-height:1.5;">
                감정가: <b style="color:#f1f5f9;">${formatNumber(item.appraised_value)}원</b> |
                최저가: <b style="color:#38bdf8;">${formatNumber(item.minimum_value)}원</b> |
                면적: <b style="color:#10b981;">${areaDisplay}</b> |
                승인일: ${item.approval_date || '상세분석 시 확인'}
                ${item.auction_date ? ' | 매각기일: ' + item.auction_date : ''}
            </div>
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
                btn.style.background = 'rgba(0,0,0,0.45)';
            }
        });

        btn.addEventListener('click', () => {
            document.querySelectorAll('.address-btn').forEach(b => {
                b.classList.remove('selected');
                b.style.borderColor = 'var(--glass-border)';
                b.style.background = 'rgba(0,0,0,0.45)';
            });
            btn.classList.add('selected');
            btn.style.borderColor = 'var(--neon-purple)';
            btn.style.background = 'rgba(187, 0, 255, 0.22)';
            
            // 데이터 설정 및 선택된 물건번호 동기화
            currentCaseData = item;
            if (item.case_no_full) {
                caseNumberInput.value = item.case_no_full;
            }
            
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

    if (!isUserAllowedForRightsAnalysis()) {
        loadingState.style.display = 'none';
        applyAnalysisAccessState();
        showError((window.analysisAccessState && window.analysisAccessState.message) || "현재 권리분석은 관리자 및 지정 허용 회원만 이용할 수 있습니다.");
        return;
    }

    const madangsUrlEl = document.getElementById('madangsUrl');
    const requestData = {
        ...currentCaseData,
        case_number: (currentCaseData.case_no_full || caseNumberInput.value).trim(),
        address_hint: currentCaseData.address || "",
        myauction_idx: currentCaseData.myauction_idx || "",
        item_no: currentCaseData.item_no || "",
        court: currentCaseData.court || "",
        property_type: document.getElementById('propertyType').value,
        house_count: houseCount,
        investor_type: document.getElementById('investorType').value,
        investment_duration: document.getElementById('investmentDuration').value,
        target_return_rate: parseFloat(document.getElementById('targetReturnRate').value) || 20.0,
        is_regulated_area: document.getElementById('isRegulatedArea').value === 'true',
        calculated_aging: agingDisplay.innerText,
        madangs_url: madangsUrlEl ? madangsUrlEl.value.trim() : "",
        admin_key: getEffectiveAdminKey(),
        user_pin: getEffectiveMemberPin()
    };

    try {
        let response = await fetch('/api/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestData)
        });

        let data = await response.json();
        if (data && data.status === "restricted") {
            loadingState.style.display = 'none';
            window.analysisAccessState = {
                ...(window.analysisAccessState || {}),
                access_mode: data.access_mode || 'admin_only',
                admin_only: Boolean(data.admin_only),
                member_allowed: false,
                message: data.message || "권리분석 이용 제한 중입니다."
            };
            applyAnalysisAccessState();
            showError(data.message || "현재 권리분석은 관리자 및 지정 허용 회원만 이용할 수 있습니다.");
            return;
        }
        
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

                if (safeCaseNum.includes('-')) {
                    const photos = data.data.photos || [];
                    imgPhoto.src = photos[0] || `/api/download_photo/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
                    imgMap.src = photos[1] || photos[0] || `/api/download_map/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
                    imgStruct.src = photos[2] || photos[0] || `/api/download_structure/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
                } else {
                    imgPhoto.src = `/api/download_photo/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
                    imgMap.src = `/api/download_map/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
                    imgStruct.src = `/api/download_structure/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
                }
            }


            // 3. 내부구조도
            const structureEl = document.getElementById('structureImage');
            const structurePlaceholder = document.getElementById('structurePlaceholder');
            if (structureEl && structurePlaceholder) {
                if (safeCaseNum.includes('-')) {
                    const photos = data.data.photos || [];
                    structureEl.src = photos[2] || photos[0] || `/api/download_structure/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
                } else {
                    structureEl.src = `/api/download_structure/${encodeURIComponent(safeCaseNum)}?t=${new Date().getTime()}`;
                }
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
                
                const convertImagesToBase64 = async (container) => {
                    if (!container) return;
                    const imgs = container.querySelectorAll('img');
                    const promises = Array.from(imgs).map(async (img) => {
                        if (!img.src || img.src.startsWith('data:')) return;
                        try {
                            img.crossOrigin = 'anonymous';
                            const res = await fetch(img.src, { mode: 'cors' });
                            if (res.ok) {
                                const blob = await res.blob();
                                const reader = new FileReader();
                                await new Promise((resolve) => {
                                    reader.onloadend = () => {
                                        img.src = reader.result;
                                        resolve();
                                    };
                                    reader.onerror = () => resolve();
                                    reader.readAsDataURL(blob);
                                });
                            }
                        } catch (e) {
                            console.warn("Cross-origin image base64 conversion skipped:", e);
                        }
                    });
                    await Promise.all(promises);
                };

                newPdfBtn.addEventListener('click', async () => {
                    const element = document.getElementById('finalReport');
                    const buttonsContainer = document.getElementById('downloadButtonsContainer');
                    const scrollHint = document.getElementById('scrollHint');
                    
                    const origBtnText = newPdfBtn.innerHTML;
                    newPdfBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> PDF 변환 중...';
                    newPdfBtn.disabled = true;

                    try {
                        if (typeof html2pdf === 'undefined') {
                            window.print();
                            return;
                        }
                        
                        // 숨길 요소들 임시 숨김 처리 & 좌우 대칭 A4 규격 최적화 모드 적용
                        if (buttonsContainer) buttonsContainer.style.display = 'none';
                        if (scrollHint) scrollHint.style.display = 'none';
                        if (element) {
                            element.classList.add('pdf-capture-mode');
                            element.scrollLeft = 0;
                        }

                        // 이미지 CORS Canvas 오염 방지를 위해 Base64 사전 변환
                        await convertImagesToBase64(element);
                        
                        const opt = {
                            margin:       [6, 6, 6, 6],
                            filename:     `${safeCaseNum}_권리분석리포트.pdf`,
                            image:        { type: 'jpeg', quality: 0.98 },
                            html2canvas:  { 
                                scale: 2, 
                                useCORS: true, 
                                allowTaint: true,
                                backgroundColor: '#13141c', 
                                letterRendering: true, 
                                scrollX: 0, 
                                scrollY: 0,
                                imageTimeout: 15000 
                            },
                            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
                        };
                        
                        await html2pdf().set(opt).from(element).save();
                    } catch (e) {
                        console.error("PDF 캡쳐 에러:", e);
                        window.print();
                    } finally {
                        if (element) element.classList.remove('pdf-capture-mode');
                        if (buttonsContainer) buttonsContainer.style.display = 'flex';
                        if (scrollHint) scrollHint.style.display = 'block';
                        newPdfBtn.innerHTML = origBtnText;
                        newPdfBtn.disabled = false;
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
        const romanMap = ["", "I|Ⅰ", "II|Ⅱ", "III|Ⅲ", "IV|Ⅳ", "V|Ⅴ", "VI|Ⅵ", "VII|Ⅶ", "VIII|Ⅷ", "IX|Ⅸ", "X|Ⅹ"];
        const numStr = `(?:${num}|${romanMap[num]})`;
        
        // 1. '# 1. 요약' 등 헤딩(#)이 명확히 있는 경우 (다음 '#' 헤딩 전까지 추출)
        const regex = new RegExp(`(?:^|\\n)#+\\s*${numStr}\\.\\s*[^\\n]*\\n([\\s\\S]*?)(?=(?:^|\\n)#+\\s*\\d+|(?:^|\\n)#+\\s*[Ⅰ-ⅩIVX]+\\.|$)`, 'i');
        const match = text.match(regex);
        if (match && match[1].trim() !== '') {
            return match[1].trim();
        }
        
        // 2. Fallback: AI가 '#' 기호를 빼먹고 '1. 요약' 형태로만 출력한 경우 (키워드 검사로 일반 번호매기기와 구분)
        const keywords = "(?:요약|기본|물리|권리|시세|수익|입지|추천|출구|대출|절세|최종|결론)";
        const fallbackRegex = new RegExp(`(?:^|\\n)${numStr}\\.\\s*${keywords}[^\\n]*\\n([\\s\\S]*?)(?=(?:^|\\n)\\d+\\.\\s*${keywords}|(?:^|\\n)[Ⅰ-ⅩIVX]+\\.\\s*${keywords}|$)`, 'i');
        const fallbackMatch = text.match(fallbackRegex);
        if (fallbackMatch && fallbackMatch[1].trim() !== '') {
            return fallbackMatch[1].trim();
        }
        
        return null;
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
    let sec4Html = marked.parse(extractSection(4, markdownText) || "내용이 추출되지 않았습니다.");
    if (caseData) {
        const pdfs = caseData.downloaded_pdfs || [];
        const hasMulgunPdf = pdfs.includes('매각물건명세서.pdf') || Boolean(caseData.hug_mulgun_pdf_verified);
        const isHug = Boolean(caseData.hug_waived) || (caseData.risks || []).some(r => String(r).includes('HUG'));
        if (hasMulgunPdf || isHug) {
            const pdfUrl = `/api/download_court_doc/${encodeURIComponent(caseData.case_number || '')}/${encodeURIComponent('매각물건명세서.pdf')}`;
            const pdfBtnHtml = hasMulgunPdf
                ? `<a href="${pdfUrl}" target="_blank" rel="noopener" style="display:inline-flex; align-items:center; gap:6px; padding:6px 12px; border-radius:8px; background:rgba(56,189,248,0.2); border:1px solid #0284c7; color:#7dd3fc; font-size:0.82rem; font-weight:700; text-decoration:none;"><i class="fa-solid fa-file-pdf" style="color:#f87171;"></i> 법원 매각물건명세서.pdf 원본 열람</a>`
                : '';
            const hugBannerHtml = isHug
                ? `<div style="margin-bottom:14px; padding:14px 16px; border-radius:10px; background:linear-gradient(135deg, rgba(16,185,129,0.16), rgba(6,95,70,0.24)); border:1px solid #10b981; color:#ecfdf5;">
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:6px;">
                        <div style="font-weight:800; color:#34d399; font-size:0.96rem;">
                            <i class="fa-solid fa-circle-check"></i> [HUG 대항력포기 물건] 법원 매각물건명세서.pdf 및 문건접수 제출 확인 완료 (인수 보증금 0원)
                        </div>
                        ${pdfBtnHtml}
                    </div>
                    <div style="font-size:0.85rem; color:#d1fae5; line-height:1.55;">
                        <strong>법원 제출 확인 근거:</strong> ${caseData.hug_waiver_evidence || '주택도시보증공사(HUG) 잔존 임차보증금반환채권 포기 및 주택임차권등기 말소동의 확약서 법원 제출 확인'}
                    </div>
                </div>`
                : `<div style="margin-bottom:12px; padding:10px 14px; border-radius:8px; background:rgba(15,23,42,0.75); border:1px solid rgba(56,189,248,0.35); display:flex; justify-content:space-between; align-items:center; gap:10px; flex-wrap:wrap;">
                    <span style="font-size:0.85rem; color:#bae6fd; font-weight:700;"><i class="fa-solid fa-file-shield" style="color:#38bdf8;"></i> 법원 매각물건명세서.pdf 원본 자동 추출·대조 완료</span>
                    ${pdfBtnHtml}
                </div>`;
            sec4Html = hugBannerHtml + sec4Html;
        }
    }
    document.getElementById('report-section-3').innerHTML = sec4Html;
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
    
    // 투자 판정(GO/Neutral/Danger/대기(WAIT)) 부각 처리
    section10Text = section10Text.replace(/\[투자 판정:\s*(GO|Neutral|Danger|WAIT|대기\(WAIT\)|대기)\]/ig, (match, p1) => {
        let color = "var(--danger, red)";
        const upper = p1.toUpperCase();
        if (upper === "GO") color = "var(--danger, red)";
        else if (upper === "NEUTRAL" || upper.includes("WAIT") || upper.includes("대기")) color = "var(--warning, orange)";
        else if (upper === "DANGER") color = "var(--danger, red)";
        
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
    const hContainer = document.getElementById('houseCountContainer');
    if (hContainer) {
        hContainer.style.display = 'flex';
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
    const addressHintParam = params.get('addressHint');
    if (addressHintParam) {
        window.addressHintParam = addressHintParam;
    }
    const investorTypeParam = params.get('investorType');

    if (investorTypeParam && document.getElementById('investorType')) {
        if (investorTypeParam === 'corporate' || investorTypeParam === '법인') {
            document.getElementById('investorType').value = '법인';
        } else if (investorTypeParam === 'business' || investorTypeParam === '매매사업자') {
            document.getElementById('investorType').value = '매매사업자';
        } else if (investorTypeParam === 'individual' || investorTypeParam === '개인') {
            document.getElementById('investorType').value = '개인';
        }
    }

    const targetYieldParam = params.get('targetYield');
    if (targetYieldParam && document.getElementById('targetReturnRate')) {
        document.getElementById('targetReturnRate').value = targetYieldParam;
    }

    const investTermParam = params.get('investTerm');
    if (investTermParam && document.getElementById('investmentDuration')) {
        if (investTermParam === 'long' || investTermParam.includes('장기')) {
            document.getElementById('investmentDuration').value = '장기(3년, 임대전략)';
        } else {
            document.getElementById('investmentDuration').value = '단기(6개월)';
        }
    }

    const houseCountParam = params.get('houseCount');
    if (houseCountParam && document.getElementById('houseCount')) {
        let valToSet = '무주택';
        if (houseCountParam === '1') valToSet = '1주택';
        else if (houseCountParam === '2') valToSet = '2주택';
        else if (houseCountParam === '3') valToSet = '3주택 이상';
        
        document.getElementById('houseCount').value = valToSet;
    }

    const isRegulatedParam = params.get('isRegulated');
    if (isRegulatedParam && document.getElementById('isRegulatedArea')) {
        const isReg = (isRegulatedParam === 'yes' || isRegulatedParam === 'true');
        document.getElementById('isRegulatedArea').value = isReg ? 'true' : 'false';
        const displayEl = document.getElementById('isRegulatedAreaDisplay');
        if (displayEl) {
            displayEl.innerText = isReg ? '조정대상지역' : '비조정대상지역';
            displayEl.style.color = isReg ? '#ef4444' : '#10b981';
        }
    }

    // Initialize Inquiry Board, Notice, and Rights Analysis Access Control
    initInquiryBoard();
    initNoticeSystem();
    initAnalysisAccessControl().then(() => {
        console.log("[Auto-Analyze] DOMContentLoaded caseParam:", caseParam);
        if (caseParam && typeof caseNumberInput !== 'undefined' && caseNumberInput) {
            caseNumberInput.value = caseParam;
            const isTabAuthed = sessionStorage.getItem('agy_session_v2') === 'active';
            const lockedForUser = !isUserAllowedForRightsAnalysis();
            if (!isTabAuthed) {
                window.pendingAutoCaseParam = caseParam;
            } else if (lockedForUser) {
                window.pendingAutoCaseParam = caseParam;
                showError((window.analysisAccessState && window.analysisAccessState.message) || "현재 권리분석은 관리자 및 지정 허용 회원 전용 모드로 제한되어 있습니다.");
            } else if (typeof searchCaseBtn !== 'undefined' && searchCaseBtn && !searchCaseBtn.disabled) {
                isAutoAnalyze = true;
                console.log("[Auto-Analyze] Setting isAutoAnalyze = true and triggering searchCaseBtn.click()");
                searchCaseBtn.click();
            }
        }
    });
});

/* ----------------- Inquiry Board Interactive Logic ----------------- */
let currentViewingInquiryId = null;
let currentPendingPinInquiryId = null;
let currentViewingInquiryData = null;
let adminAuthKey = (sessionStorage.getItem('agy_admin_session_v2') === 'active') ? (sessionStorage.getItem('admin_board_key') || '') : '';
let cachedPins = {}; // in-memory cache for pins entered in this session
window.analysisAccessState = {
    access_mode: 'all',
    admin_only: false,
    restricted: false,
    allowed_user_ids: [],
    allowed_user_names: [],
    member_allowed: false,
    message: ''
};

function getEffectiveAdminKey() {
    if (!isAdminSessionActive()) return '';
    return adminAuthKey || sessionStorage.getItem('admin_board_key') || '';
}

function getEffectiveMemberPin() {
    return sessionStorage.getItem('member_auth_pin') || '';
}

function isUserAllowedForRightsAnalysis() {
    if (isAdminSessionActive()) return true;
    const state = window.analysisAccessState || {};
    const mode = state.access_mode || (state.admin_only ? 'admin_only' : 'all');
    if (mode === 'all') return true;
    if (mode === 'selected') {
        return Boolean(state.member_allowed) || sessionStorage.getItem('member_can_analyze') === '1';
    }
    return false;
}

function isAdminSessionActive() {
    const ssKey = sessionStorage.getItem('admin_board_key') || '';
    if (ssKey && sessionStorage.getItem('is_admin_verified') === '1' && sessionStorage.getItem('agy_admin_session_v2') === 'active') {
        return true;
    }
    return false;
}

function performAdminLogout() {
    adminAuthKey = '';
    sessionStorage.removeItem('admin_board_key');
    sessionStorage.removeItem('is_admin_verified');
    sessionStorage.removeItem('agy_admin_session_v2');
    try {
        localStorage.removeItem('agy_admin_key');
        localStorage.removeItem('agy_admin_exp');
        localStorage.removeItem('agy_auth_exp');
    } catch (e) {}
    updateAdminUI();
    applyAnalysisAccessState();
}

function performFullSessionLock() {
    adminAuthKey = '';
    sessionStorage.removeItem('agy_session_v2');
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('admin_board_key');
    sessionStorage.removeItem('is_admin_verified');
    sessionStorage.removeItem('agy_admin_session_v2');
    sessionStorage.removeItem('member_auth_pin');
    sessionStorage.removeItem('member_can_analyze');
    sessionStorage.removeItem('member_user_name');
    try {
        localStorage.removeItem('agy_auth_exp');
        localStorage.removeItem('agy_admin_key');
        localStorage.removeItem('agy_admin_exp');
    } catch (e) {}
    if (typeof updateAdminUI === 'function') updateAdminUI();
    if (typeof applyAnalysisAccessState === 'function') applyAnalysisAccessState();
    document.documentElement.classList.remove('session-authenticated');
    const loginOverlayEl = document.getElementById('loginOverlay');
    if (loginOverlayEl) loginOverlayEl.classList.remove('hidden');
    const pwdInputEl = document.getElementById('passwordInput');
    if (pwdInputEl) {
        pwdInputEl.value = '';
        setTimeout(() => pwdInputEl.focus(), 50);
    }
}

function initInquiryBoard() {
    const boardModal = document.getElementById('inquiryBoardModal');
    const openBtnLogin = document.getElementById('openBoardBtnLogin');
    const openSignupBtnLogin = document.getElementById('openSignupBtnLogin');
    const openBtnHeader = document.getElementById('openBoardBtnHeader');
    const closeBtn = document.getElementById('closeBoardModalBtn');
    const showWriteBtn = document.getElementById('showWriteFormBtn');
    const cancelWriteBtn = document.getElementById('cancelWriteBtn');
    const backToListBtn = document.getElementById('backToListBtn');
    const inqForm = document.getElementById('inquiryForm');
    const commentForm = document.getElementById('commentForm');
    const pinModal = document.getElementById('pinModal');
    const cancelPinBtn = document.getElementById('cancelPinBtn');
    const confirmPinBtn = document.getElementById('confirmPinBtn');
    const adminLoginModal = document.getElementById('adminLoginModal');
    const boardAdminBtn = document.getElementById('boardAdminBtn');
    const cancelAdminBtn = document.getElementById('cancelAdminBtn');
    const confirmAdminBtn = document.getElementById('confirmAdminBtn');
    const deleteInqBtn = document.getElementById('deleteInqBtn');
    const approveInqBtn = document.getElementById('approveInqBtn');

    if (openBtnLogin) openBtnLogin.addEventListener('click', () => openBoard());
    if (openSignupBtnLogin) openSignupBtnLogin.addEventListener('click', () => {
        openBoard();
        showWriteView();
    });
    if (openBtnHeader) openBtnHeader.addEventListener('click', () => openBoard());
    if (closeBtn) closeBtn.addEventListener('click', () => closeBoard());

    if (showWriteBtn) showWriteBtn.addEventListener('click', () => showWriteView());
    if (cancelWriteBtn) cancelWriteBtn.addEventListener('click', () => showListView());
    if (backToListBtn) backToListBtn.addEventListener('click', () => { showListView(); fetchInquiries(); });

    if (inqForm) inqForm.addEventListener('submit', handleInquirySubmit);
    if (commentForm) commentForm.addEventListener('submit', handleCommentSubmit);

    // Email verification listeners
    const sendCodeBtn = document.getElementById('sendEmailCodeBtn');
    const verifyCodeBtn = document.getElementById('verifyEmailCodeBtn');
    if (sendCodeBtn) sendCodeBtn.addEventListener('click', handleSendEmailCode);
    if (verifyCodeBtn) verifyCodeBtn.addEventListener('click', handleVerifyEmailCode);

    // Password validation real-time listener
    const inqPinInput = document.getElementById('inqPin');
    if (inqPinInput) {
        inqPinInput.addEventListener('input', handlePinValidationInput);
    }

    // PIN modal
    if (cancelPinBtn) cancelPinBtn.addEventListener('click', () => { pinModal.style.display = 'none'; });
    if (confirmPinBtn) confirmPinBtn.addEventListener('click', handlePinConfirm);
    const pinInput = document.getElementById('pinModalInput');
    if (pinInput) {
        pinInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handlePinConfirm();
        });
    }

    // Admin login modal
    if (boardAdminBtn) boardAdminBtn.addEventListener('click', () => {
        if (isAdminSessionActive()) {
            if (confirm("관리자 모드가 이미 활성화되어 있습니다. 관리자 로그아웃 하시겠습니까?")) {
                performAdminLogout();
                alert("관리자 모드에서 로그아웃 되었습니다.");
                fetchInquiries();
            }
        } else {
            adminLoginModal.style.display = 'flex';
            document.getElementById('adminKeyModalInput').value = '';
            document.getElementById('adminKeyModalInput').focus();
        }
    });
    if (cancelAdminBtn) cancelAdminBtn.addEventListener('click', () => { adminLoginModal.style.display = 'none'; });
    if (confirmAdminBtn) confirmAdminBtn.addEventListener('click', handleAdminLogin);
    const adminKeyInput = document.getElementById('adminKeyModalInput');
    if (adminKeyInput) {
        adminKeyInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') handleAdminLogin();
        });
    }

    if (deleteInqBtn) deleteInqBtn.addEventListener('click', handleDeleteInquiry);
    if (approveInqBtn) approveInqBtn.addEventListener('click', handleApproveUser);

    updateAdminUI();
}

function updateAdminUI() {
    const adminBtn = document.getElementById('boardAdminBtn');
    const dbCenterBtn = document.getElementById('openAdminCenterBtnBoard');
    const adminBadge = document.getElementById('adminBadgeIndicator');
    const deleteBtn = document.getElementById('deleteInqBtn');
    const approveBtn = document.getElementById('approveInqBtn');

    if (isAdminSessionActive()) {
        if (adminBtn) adminBtn.innerHTML = '<i class="fa-solid fa-crown"></i> 관리자(ON)';
        if (dbCenterBtn) dbCenterBtn.style.display = 'inline-flex';
        if (adminBadge) adminBadge.style.display = 'inline-block';
        if (deleteBtn) deleteBtn.style.display = 'inline-block';
        if (approveBtn && currentViewingInquiryData) {
            approveBtn.style.display = 'inline-block';
            if (currentViewingInquiryData.is_approved) {
                approveBtn.innerHTML = '<i class="fa-solid fa-check"></i> 승인완료됨';
                approveBtn.style.opacity = '0.6';
                approveBtn.disabled = true;
            } else {
                approveBtn.innerHTML = '<i class="fa-solid fa-user-check"></i> 👑 회원 승인';
                approveBtn.style.opacity = '1.0';
                approveBtn.disabled = false;
            }
        }
    } else {
        if (adminBtn) adminBtn.innerHTML = '<i class="fa-solid fa-user-shield"></i> 관리자 로그인';
        if (dbCenterBtn) dbCenterBtn.style.display = 'none';
        if (adminBadge) adminBadge.style.display = 'none';
        if (deleteBtn) deleteBtn.style.display = 'none';
        if (approveBtn) approveBtn.style.display = 'none';
    }
    if (typeof updateNoticeAdminBtnVisibility === 'function') {
        updateNoticeAdminBtnVisibility();
    }
}

function openBoard() {
    const modal = document.getElementById('inquiryBoardModal');
    if (modal) {
        modal.style.display = 'flex';
        showListView();
        fetchInquiries();
    }
}

function closeBoard() {
    const modal = document.getElementById('inquiryBoardModal');
    if (modal) modal.style.display = 'none';
}

function showListView() {
    document.getElementById('boardListView').style.display = 'block';
    document.getElementById('boardWriteView').style.display = 'none';
    document.getElementById('boardDetailView').style.display = 'none';
    currentViewingInquiryData = null;
}

function showWriteView() {
    document.getElementById('boardListView').style.display = 'none';
    document.getElementById('boardWriteView').style.display = 'block';
    document.getElementById('boardDetailView').style.display = 'none';
    document.getElementById('inquiryForm').reset();
    document.getElementById('inqIsSecret').checked = true;
    isEmailVerified = false;
    if (emailVerifyCountdown) clearInterval(emailVerifyCountdown);
    const box = document.getElementById('emailCodeBox');
    if (box) box.style.display = 'none';
    const badge = document.getElementById('emailVerifySuccessBadge');
    if (badge) badge.style.display = 'none';
    const inqEmail = document.getElementById('inqEmail');
    if (inqEmail) inqEmail.readOnly = false;
    const sendBtn = document.getElementById('sendEmailCodeBtn');
    if (sendBtn) {
        sendBtn.style.display = 'inline-flex';
        sendBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> 인증번호 받기';
        sendBtn.disabled = false;
    }
    const hintEl = document.getElementById('pinValidationHint');
    if (hintEl) {
        hintEl.style.color = '#94a3b8';
        hintEl.innerHTML = '<i class="fa-solid fa-circle-info"></i> 영문 알파벳, 숫자, 특수문자를 모두 포함하여 6자리 이상 입력';
    }
}

function showDetailView() {
    document.getElementById('boardListView').style.display = 'none';
    document.getElementById('boardWriteView').style.display = 'none';
    document.getElementById('boardDetailView').style.display = 'block';
}

async function fetchInquiries() {
    const tbody = document.getElementById('boardTableBody');
    if (!tbody) return;

    try {
        const adminParam = isAdminSessionActive() ? `&admin_key=${encodeURIComponent(adminAuthKey)}` : '';
        const res = await fetch(`/api/board/inquiries?limit=30${adminParam}`);
        const json = await res.json();

        if (json.status === 'success') {
            const items = json.data.items;
            if (items.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:35px; color:#94a3b8;">등록된 신청/문의글이 없습니다. 첫 번째 가입 신청을 남겨보세요!</td></tr>`;
                return;
            }

            let html = '';
            items.forEach(item => {
                let statusBadge = '<span class="board-badge badge-pending">승인대기</span>';
                if (item.is_approved) {
                    statusBadge = '<span class="board-badge badge-approved"><i class="fa-solid fa-check"></i> 승인완료</span>';
                } else if (item.status === 'rejected') {
                    statusBadge = '<span class="board-badge" style="background:rgba(239,68,68,0.2); color:#fca5a5; border:1px solid rgba(239,68,68,0.4);">반려됨</span>';
                } else if (item.status === 'revoked' || item.status === 'blocked') {
                    statusBadge = '<span class="board-badge" style="background:rgba(239,68,68,0.2); color:#fca5a5; border:1px solid rgba(239,68,68,0.4);">승인취소</span>';
                } else if (item.has_admin_reply) {
                    statusBadge = '<span class="board-badge badge-replied"><i class="fa-solid fa-check-double"></i> 답변완료</span>';
                }
                
                const secretIcon = item.is_secret ? '<i class="fa-solid fa-lock" style="color:var(--neon-blue); margin-right:5px;"></i>' : '';
                const dateStr = item.created_at ? item.created_at.substring(0, 10) : '-';

                html += `
                    <tr onclick="onInquiryRowClick(${item.id}, ${item.is_secret})" style="cursor:pointer;">
                        <td>${statusBadge}</td>
                        <td style="font-weight:500; color:#f8fafc;">${secretIcon}${item.title}</td>
                        <td style="color:#94a3b8;">${item.author}</td>
                        <td style="color:#64748b; font-size:0.85rem;">${dateStr}</td>
                        <td style="text-align:center; color:var(--neon-blue); font-weight:bold;">${item.comment_count || 0}</td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        } else {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:20px; color:#ef4444;">오류: ${json.message}</td></tr>`;
        }
    } catch (e) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding:20px; color:#ef4444;">게시글을 불러오는 중 네트워크 오류가 발생했습니다.</td></tr>`;
    }
}

function onInquiryRowClick(id, isSecret) {
    currentViewingInquiryId = id;

    if (adminAuthKey || !isSecret || cachedPins[id]) {
        loadInquiryDetail(id, cachedPins[id] || '');
    } else {
        currentPendingPinInquiryId = id;
        document.getElementById('pinModal').style.display = 'flex';
        document.getElementById('pinModalInput').value = '';
        document.getElementById('pinModalInput').focus();
    }
}

function handlePinConfirm() {
    const pin = document.getElementById('pinModalInput').value.trim();
    if (!pin) {
        alert("비밀번호(PIN)를 입력해주세요.");
        return;
    }
    document.getElementById('pinModal').style.display = 'none';
    cachedPins[currentPendingPinInquiryId] = pin;
    loadInquiryDetail(currentPendingPinInquiryId, pin);
}

async function loadInquiryDetail(id, pin) {
    try {
        const payload = { pin: pin || "", admin_key: adminAuthKey || "" };
        const res = await fetch(`/api/board/inquiries/${id}/view`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const json = await res.json();

        if (json.status === 'success') {
            const data = json.data;
            currentViewingInquiryData = data;
            showDetailView();

            document.getElementById('detailTitle').innerText = data.title;
            document.getElementById('detailAuthor').innerText = data.author;
            document.getElementById('detailDate').innerText = data.created_at;
            document.getElementById('detailContent').innerText = data.content;

            const contactEl = document.getElementById('detailContact');
            if (data.contact) {
                contactEl.innerText = `(연락처: ${data.contact})`;
            } else {
                contactEl.innerText = '';
            }

            const badgeEl = document.getElementById('detailBadge');
            if (data.is_approved) {
                badgeEl.className = 'board-badge badge-approved';
                badgeEl.innerHTML = '<i class="fa-solid fa-check"></i> 회원 승인완료';
            } else if (data.comments.some(c => c.is_admin)) {
                badgeEl.className = 'board-badge badge-replied';
                badgeEl.innerHTML = '<i class="fa-solid fa-check-double"></i> 답변완료';
            } else {
                badgeEl.className = 'board-badge badge-pending';
                badgeEl.innerHTML = '대기중';
            }

            // Comments
            const commentList = document.getElementById('commentListContainer');
            document.getElementById('commentCount').innerText = data.comments.length;

            if (data.comments.length === 0) {
                commentList.innerHTML = `<div style="text-align:center; padding:20px; color:#94a3b8; font-size:0.9rem;">등록된 답변이나 안내가 없습니다. 관리자 확인 후 승인 및 답변을 남깁니다.</div>`;
            } else {
                let cHtml = '';
                data.comments.forEach(c => {
                    const isAdminCard = c.is_admin ? 'admin-reply' : '';
                    const adminTag = c.is_admin ? '<span class="board-badge badge-admin"><i class="fa-solid fa-crown"></i> 관리자 안내</span>' : '';
                    cHtml += `
                        <div class="comment-card ${isAdminCard}">
                            <div class="comment-header">
                                <div><b style="color:#fff;">${c.author}</b> ${adminTag}</div>
                                <div>${c.created_at}</div>
                            </div>
                            <div class="comment-body">${c.content}</div>
                        </div>
                    `;
                });
                commentList.innerHTML = cHtml;
            }

            updateAdminUI();
        } else {
            if (json.is_secret) {
                alert("비밀번호가 일치하지 않습니다. 다시 확인해주세요.");
                delete cachedPins[id];
            } else {
                alert("오류: " + json.message);
            }
        }
    } catch (e) {
        alert("상세 조회를 가져오는 중 오류가 발생했습니다: " + e.message);
    }
}

let isEmailVerified = false;
let emailVerifyCountdown = null;

function handlePinValidationInput(e) {
    const val = e.target.value.trim();
    const hintEl = document.getElementById('pinValidationHint');
    if (!hintEl) return;

    const hasLetter = /[A-Za-z]/.test(val);
    const hasDigit = /\d/.test(val);
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~`]/.test(val);
    const hasLength = val.length >= 6;

    if (hasLetter && hasDigit && hasSpecial && hasLength) {
        hintEl.style.color = '#34d399';
        hintEl.innerHTML = '<i class="fa-solid fa-circle-check"></i> 사용 가능한 안전한 비밀번호입니다 (영문+숫자+특수문자 6자 이상 충족)';
    } else {
        hintEl.style.color = '#f59e0b';
        hintEl.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> 영문 알파벳, 숫자, 특수문자를 모두 포함하여 6자리 이상이어야 합니다.';
    }
}

async function handleSendEmailCode() {
    const emailInput = document.getElementById('inqEmail');
    const email = emailInput ? emailInput.value.trim().toLowerCase() : '';
    if (!email || !email.includes('@') || !email.includes('.')) {
        alert("올바른 이메일 주소를 입력해주세요.");
        return;
    }

    const sendBtn = document.getElementById('sendEmailCodeBtn');
    sendBtn.disabled = true;
    sendBtn.innerText = '발송 중...';

    try {
        const res = await fetch('/api/auth/send_verification_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const json = await res.json();

        if (json.status === 'success') {
            alert(json.message);
            document.getElementById('emailCodeBox').style.display = 'block';
            document.getElementById('inqEmailCode').focus();
            
            if (json.demo_code) {
                document.getElementById('inqEmailCode').value = json.demo_code;
            }

            let timeLeft = 600;
            const timerEl = document.getElementById('emailVerifyTimer');
            if (emailVerifyCountdown) clearInterval(emailVerifyCountdown);
            emailVerifyCountdown = setInterval(() => {
                timeLeft--;
                if (timeLeft <= 0) {
                    clearInterval(emailVerifyCountdown);
                    timerEl.innerText = "만료됨";
                } else {
                    const m = Math.floor(timeLeft / 60);
                    const s = timeLeft % 60;
                    timerEl.innerText = `${m}:${s < 10 ? '0' : ''}${s}`;
                }
            }, 1000);
        } else {
            alert("발송 실패: " + json.message);
        }
    } catch (e) {
        alert("인증번호 발송 중 네트워크 오류가 발생했습니다.");
    } finally {
        sendBtn.disabled = false;
        sendBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> 재발송';
    }
}

async function handleVerifyEmailCode() {
    const email = document.getElementById('inqEmail').value.trim().toLowerCase();
    const code = document.getElementById('inqEmailCode').value.trim();

    if (!code || code.length !== 6) {
        alert("6자리 인증코드를 정확히 입력해주세요.");
        return;
    }

    try {
        const res = await fetch('/api/auth/verify_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, code })
        });
        const json = await res.json();

        if (json.status === 'success') {
            isEmailVerified = true;
            if (emailVerifyCountdown) clearInterval(emailVerifyCountdown);
            document.getElementById('emailCodeBox').style.display = 'none';
            document.getElementById('emailVerifySuccessBadge').style.display = 'block';
            document.getElementById('inqEmail').readOnly = true;
            document.getElementById('sendEmailCodeBtn').style.display = 'none';
            alert("이메일 실명 인증이 완료되었습니다!");
        } else {
            alert("인증 실패: " + json.message);
        }
    } catch (e) {
        alert("인증 처리 중 네트워크 오류가 발생했습니다.");
    }
}

async function handleInquirySubmit(e) {
    e.preventDefault();
    const author = document.getElementById('inqAuthor').value.trim();
    const pin = document.getElementById('inqPin').value.trim();
    const emailInput = document.getElementById('inqEmail');
    const email = emailInput ? emailInput.value.trim().toLowerCase() : '';
    const phoneInput = document.getElementById('inqPhone');
    const phone = phoneInput ? phoneInput.value.trim() : '';
    const title = document.getElementById('inqTitle').value.trim();
    const content = document.getElementById('inqContent').value.trim();
    const isSecret = document.getElementById('inqIsSecret').checked;

    if (!author || !pin || !title || !content || !email) {
        alert("신청자 실명, 사용할 비밀번호, 이메일, 제목, 신청 내용을 모두 입력해주세요.");
        return;
    }

    // 1. 이메일 인증 여부 검증
    if (!isEmailVerified) {
        alert("이메일 실명 인증을 먼저 완료해주세요.\n[인증번호 받기]를 누르신 후 이메일로 발송된 6자리 번호를 인증해야 합니다.");
        return;
    }

    // 2. 비밀번호 복잡도 유효성 검사 (영문+숫자+특수문자 6자 이상)
    const hasLetter = /[A-Za-z]/.test(pin);
    const hasDigit = /\d/.test(pin);
    const hasSpecial = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~`]/.test(pin);
    if (!hasLetter || !hasDigit || !hasSpecial || pin.length < 6) {
        alert("비밀번호는 영문 알파벳, 숫자, 특수문자를 모두 포함하여 최소 6자리 이상이어야 합니다.");
        document.getElementById('inqPin').focus();
        return;
    }

    const contact = phone ? `${email} / ${phone}` : email;

    try {
        const res = await fetch('/api/board/inquiries', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ author, pin, contact, email, phone, title, content, is_secret: isSecret })
        });
        const json = await res.json();

        if (json.status === 'success') {
            alert("가입 및 문의 신청이 성공적으로 등록되었습니다!\n관리자 승인 후 본인이 설정한 비밀번호로 로그인하실 수 있습니다.");
            cachedPins[json.id] = pin;
            showListView();
            fetchInquiries();
        } else {
            alert("등록 실패: " + json.message);
        }
    } catch (err) {
        alert("등록 중 네트워크 오류가 발생했습니다.");
    }
}

async function handleCommentSubmit(e) {
    e.preventDefault();
    if (!currentViewingInquiryId) return;

    const content = document.getElementById('commentContentInput').value.trim();
    if (!content) {
        alert("댓글 내용을 입력해주세요.");
        return;
    }

    const pin = cachedPins[currentViewingInquiryId] || "";
    try {
        const res = await fetch(`/api/board/inquiries/${currentViewingInquiryId}/comments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                content,
                pin,
                admin_key: adminAuthKey || "",
                is_secret: true
            })
        });
        const json = await res.json();

        if (json.status === 'success') {
            document.getElementById('commentContentInput').value = '';
            loadInquiryDetail(currentViewingInquiryId, pin);
        } else {
            alert("댓글 등록 실패: " + json.message);
        }
    } catch (err) {
        alert("댓글 등록 중 네트워크 오류가 발생했습니다.");
    }
}

async function handleAdminLogin() {
    const key = document.getElementById('adminKeyModalInput').value.trim();
    if (!key) {
        alert("관리자 인증번호를 입력해주세요.");
        return;
    }

    try {
        const res = await fetch('/api/board/admin/verify', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ admin_key: key })
        });
        const json = await res.json();

        if (json.status === 'success') {
            try {
                localStorage.removeItem('agy_auth_exp');
                localStorage.removeItem('agy_admin_key');
                localStorage.removeItem('agy_admin_exp');
            } catch (e) {}
            adminAuthKey = key;
            sessionStorage.setItem('admin_board_key', key);
            sessionStorage.setItem('is_admin_verified', '1');
            sessionStorage.setItem('agy_admin_session_v2', 'active');
            sessionStorage.setItem('agy_session_v2', 'active');
            sessionStorage.setItem('auth_token', 'verified');
            document.documentElement.classList.add('session-authenticated');
            const loginOverlayEl = document.getElementById('loginOverlay');
            if (loginOverlayEl) loginOverlayEl.classList.add('hidden');
            document.getElementById('adminKeyModalInput').value = '';
            document.getElementById('adminLoginModal').style.display = 'none';
            showError("");
            updateAdminUI();
            applyAnalysisAccessState();
            alert("관리자 인증이 완료되었습니다. 권리분석 제한 설정 제어 및 관리자 전용 권리분석 이용이 가능합니다.");
            if (window.pendingAutoCaseParam && caseNumberInput && searchCaseBtn && !searchCaseBtn.disabled) {
                caseNumberInput.value = window.pendingAutoCaseParam;
                window.pendingAutoCaseParam = null;
                isAutoAnalyze = true;
                searchCaseBtn.click();
            }
            if (currentViewingInquiryId) {
                loadInquiryDetail(currentViewingInquiryId, '');
            } else {
                fetchInquiries();
            }
        } else {
            alert("관리자 인증번호가 일치하지 않습니다.");
            document.getElementById('adminKeyModalInput').value = '';
        }
    } catch (err) {
        alert("인증 처리 중 오류가 발생했습니다.");
    }
}

async function handleApproveUser() {
    if (!currentViewingInquiryId || !adminAuthKey) return;
    if (!confirm(`'${currentViewingInquiryData?.author}' 회원의 가입을 승인하시겠습니까?\n승인 시 해당 회원이 설정한 비밀번호로 즉시 로그인이 가능해집니다.`)) return;

    try {
        const res = await fetch(`/api/board/inquiries/${currentViewingInquiryId}/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ admin_key: adminAuthKey })
        });
        const json = await res.json();

        if (json.status === 'success') {
            alert(json.message);
            loadInquiryDetail(currentViewingInquiryId, '');
        } else {
            alert("승인 실패: " + json.message);
        }
    } catch (err) {
        alert("승인 처리 중 오류가 발생했습니다: " + err.message);
    }
}

async function handleDeleteInquiry() {
    if (!currentViewingInquiryId) return;
    if (!confirm("정말로 이 신청/문의글을 삭제하시겠습니까?")) return;

    const pin = cachedPins[currentViewingInquiryId] || "";
    try {
        const res = await fetch(`/api/board/inquiries/${currentViewingInquiryId}?pin=${encodeURIComponent(pin)}&admin_key=${encodeURIComponent(adminAuthKey || '')}`, {
            method: 'DELETE'
        });
        const json = await res.json();
        if (json.status === 'success') {
            alert("삭제되었습니다.");
            showListView();
            fetchInquiries();
        } else {
            alert("삭제 실패: " + json.message);
        }
    } catch (err) {
        alert("삭제 처리 중 오류가 발생했습니다.");
    }
}

// Donation Modal Logic
const openDonationBtn = document.getElementById('openDonationBtn');
const closeDonationModalBtn = document.getElementById('closeDonationModalBtn');
const donationModal = document.getElementById('donationModal');

if (openDonationBtn) {
    openDonationBtn.addEventListener('click', () => {
        if (donationModal) donationModal.style.display = 'flex';
    });
}
if (closeDonationModalBtn) {
    closeDonationModalBtn.addEventListener('click', () => {
        if (donationModal) donationModal.style.display = 'none';
    });
}
if (donationModal) {
    donationModal.addEventListener('click', (e) => {
        if (e.target === donationModal) {
            donationModal.style.display = 'none';
        }
    });
}


/* ----------------- Admin Notice Banner & Modal Logic (유저 공지 알림판 시스템) ----------------- */
let currentNoticeData = null;

async function fetchActiveNotice() {
    try {
        const res = await fetch('/api/notice');
        const json = await res.json();
        if (json.status === 'success' && json.notice && json.notice.is_active) {
            currentNoticeData = json.notice;
            renderNoticeBanner(json.notice);
        } else {
            currentNoticeData = null;
            const banner = document.getElementById('adminNoticeBanner');
            if (banner) banner.style.display = 'none';
        }
    } catch (e) {
        console.warn("공지 불러오기 실패:", e);
    }
}

function renderNoticeBanner(notice) {
    const banner = document.getElementById('adminNoticeBanner');
    const titleEl = document.getElementById('noticeBannerTitle');
    const contentEl = document.getElementById('noticeBannerContent');
    const iconEl = document.getElementById('noticeBannerIcon');
    
    if (!banner || !titleEl || !contentEl) return;

    titleEl.innerText = notice.title;
    contentEl.innerText = notice.content;

    // 공지 유형별 맞춤형 네온 스타일 적용
    if (notice.notice_type === 'urgent') {
        banner.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.22), rgba(185, 28, 28, 0.25))';
        banner.style.borderColor = '#ef4444';
        if (iconEl) {
            iconEl.style.borderColor = '#ef4444';
            iconEl.style.background = 'rgba(239, 68, 68, 0.25)';
            iconEl.innerHTML = '<i class="fa-solid fa-triangle-exclamation" style="color:#f87171;"></i>';
        }
        titleEl.style.color = '#fca5a5';
    } else if (notice.notice_type === 'info') {
        banner.style.background = 'linear-gradient(135deg, rgba(14, 165, 233, 0.18), rgba(59, 130, 246, 0.2))';
        banner.style.borderColor = '#0284c7';
        if (iconEl) {
            iconEl.style.borderColor = '#38bdf8';
            iconEl.style.background = 'rgba(14, 165, 233, 0.2)';
            iconEl.innerHTML = '<i class="fa-solid fa-circle-info" style="color:#38bdf8;"></i>';
        }
        titleEl.style.color = '#bae6fd';
    } else { // warning
        banner.style.background = 'linear-gradient(135deg, rgba(234, 179, 8, 0.16), rgba(239, 68, 68, 0.18))';
        banner.style.borderColor = 'rgba(245, 158, 11, 0.5)';
        if (iconEl) {
            iconEl.style.borderColor = '#f59e0b';
            iconEl.style.background = 'rgba(245, 158, 11, 0.2)';
            iconEl.innerHTML = '<i class="fa-solid fa-bullhorn" style="color:#fbbf24;"></i>';
        }
        titleEl.style.color = '#fef08a';
    }

    banner.style.display = 'block';
    updateNoticeAdminBtnVisibility();
}

function updateNoticeAdminBtnVisibility() {
    const manageBtn = document.getElementById('noticeAdminManageBtn');
    const isAdmin = isAdminSessionActive();
    if (manageBtn) {
        manageBtn.style.display = isAdmin ? 'inline-flex' : 'none';
    }
}

function openNoticeAdminModal() {
    const isAdmin = isAdminSessionActive();
    if (!isAdmin) {
        const adminLoginModal = document.getElementById('adminLoginModal');
        if (adminLoginModal) {
            adminLoginModal.style.display = 'flex';
            const adminInput = document.getElementById('adminKeyModalInput');
            if (adminInput) {
                adminInput.value = '';
                adminInput.focus();
            }
            alert("공지 관리는 관리자 전용 기능입니다. 관리자 인증번호를 먼저 입력해주세요.");
        }
        return;
    }

    const modal = document.getElementById('noticeAdminModal');
    if (!modal) return;

    const titleInput = document.getElementById('adminNoticeTitle');
    const contentInput = document.getElementById('adminNoticeContent');
    const typeSelect = document.getElementById('adminNoticeType');
    const radios = document.getElementsByName('noticeActiveRadio');

    if (currentNoticeData) {
        titleInput.value = currentNoticeData.title || '';
        contentInput.value = currentNoticeData.content || '';
        if (typeSelect) typeSelect.value = currentNoticeData.notice_type || 'warning';
        for (const r of radios) {
            r.checked = (r.value === (currentNoticeData.is_active ? '1' : '0'));
        }
    } else {
        titleInput.value = '🚨 [긴급 안내] 구글 AI 할당량 초과에 따른 권리분석 일시 이용 자제 안내';
        contentInput.value = '현재 구글 AI API 사용량 할당 초과(429 Quota Exceeded)로 인해 권리분석 생성에 제한이 발생하고 있습니다. 안정적인 서비스 정상화 및 쿼터 리셋을 위해 금일(하루 동안) 권리분석 기능 사용을 잠시 자제해 주시기를 부탁드립니다. (※ 지도 검색 및 기본 물건 분석은 정상 이용 가능합니다)';
        if (typeSelect) typeSelect.value = 'warning';
        for (const r of radios) {
            r.checked = (r.value === '1');
        }
    }

    modal.style.display = 'flex';
}

function closeNoticeAdminModal() {
    const modal = document.getElementById('noticeAdminModal');
    if (modal) modal.style.display = 'none';
}

async function handleSaveNoticeAdmin() {
    const effectiveKey = adminAuthKey || sessionStorage.getItem('admin_board_key');
    if (!effectiveKey || !isAdminSessionActive()) {
        alert("관리자 권한이 없습니다.");
        return;
    }

    const title = document.getElementById('adminNoticeTitle').value.trim();
    const content = document.getElementById('adminNoticeContent').value.trim();
    const notice_type = document.getElementById('adminNoticeType').value;
    const radios = document.getElementsByName('noticeActiveRadio');
    let is_active = true;
    for (const r of radios) {
        if (r.checked) is_active = (r.value === '1');
    }

    if (!title) {
        alert("공지 제목을 입력해주세요.");
        return;
    }
    if (!content) {
        alert("공지 상세 내용을 입력해주세요.");
        return;
    }

    try {
        const res = await fetch('/api/admin/notice', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                admin_key: effectiveKey,
                title,
                content,
                notice_type,
                is_active
            })
        });
        const json = await res.json();
        if (json.status === 'success') {
            alert("공지가 성공적으로 저장 및 반영되었습니다!");
            closeNoticeAdminModal();
            fetchActiveNotice();
        } else {
            alert("공지 저장 실패: " + json.message);
        }
    } catch (e) {
        alert("공지 저장 중 네트워크 오류가 발생했습니다: " + e.message);
    }
}

function initNoticeSystem() {
    const closeBannerBtn = document.getElementById('closeNoticeBannerBtn');
    if (closeBannerBtn) {
        closeBannerBtn.addEventListener('click', () => {
            const banner = document.getElementById('adminNoticeBanner');
            if (banner) banner.style.display = 'none';
        });
    }

    const openNoticeBtnHeader = document.getElementById('openNoticeBtnHeader');
    if (openNoticeBtnHeader) {
        openNoticeBtnHeader.addEventListener('click', () => {
            const isAdmin = isAdminSessionActive();
            if (isAdmin) {
                openNoticeAdminModal();
            } else {
                if (currentNoticeData && currentNoticeData.is_active) {
                    const banner = document.getElementById('adminNoticeBanner');
                    if (banner) {
                        banner.style.display = 'block';
                        banner.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                    alert(`📢 [공지 안내]\n\n제목: ${currentNoticeData.title}\n\n${currentNoticeData.content}`);
                } else {
                    alert("📢 현재 등록된 진행 중인 공지사항이 없습니다.");
                }
            }
        });
    }

    const manageBtn = document.getElementById('noticeAdminManageBtn');
    if (manageBtn) {
        manageBtn.addEventListener('click', () => openNoticeAdminModal());
    }

    const closeAdminModalBtn = document.getElementById('closeNoticeAdminModalBtn');
    if (closeAdminModalBtn) closeAdminModalBtn.addEventListener('click', closeNoticeAdminModal);

    const cancelAdminModalBtn = document.getElementById('cancelNoticeAdminBtn');
    if (cancelAdminModalBtn) cancelAdminModalBtn.addEventListener('click', closeNoticeAdminModal);

    const saveAdminBtn = document.getElementById('saveNoticeAdminBtn');
    if (saveAdminBtn) saveAdminBtn.addEventListener('click', handleSaveNoticeAdmin);

    fetchActiveNotice();
}

// 🛡️ 장시간 유휴/방치 시 Cloudflare 터널 및 서버 세션 단절 방지 하트비트
(function() {
    async function sendHeartbeat() {
        try {
            await fetch('/api/ping', { method: 'GET', cache: 'no-store' });
        } catch (e) {}
    }
    setInterval(sendHeartbeat, 30000);
    setTimeout(sendHeartbeat, 2000);
})();




/* ----------------- 관리자 및 지정회원 전용 권리분석 이용제한 시스템 ----------------- */
async function fetchAnalysisAccessConfig() {
    try {
        const memberPin = getEffectiveMemberPin();
        const q = memberPin ? `?user_pin=${encodeURIComponent(memberPin)}` : '';
        const res = await fetch(`/api/analysis_access_config${q}`, { cache: 'no-store' });
        const json = await res.json();
        if (json.status === 'success') {
            window.analysisAccessState = {
                access_mode: json.access_mode || (json.admin_only ? 'admin_only' : 'all'),
                admin_only: Boolean(json.admin_only),
                restricted: Boolean(json.restricted),
                allowed_user_ids: json.allowed_user_ids || [],
                allowed_user_names: json.allowed_user_names || [],
                allowed_count: json.allowed_count || 0,
                member_allowed: Boolean(json.member_allowed),
                message: json.message || '현재 권리분석은 관리자 및 지정 허용 회원만 이용할 수 있습니다.',
                updated_at: json.updated_at || ''
            };
            if (memberPin && typeof json.member_allowed === 'boolean') {
                sessionStorage.setItem('member_can_analyze', json.member_allowed ? '1' : '0');
            }
        }
    } catch (e) {
        console.warn("권리분석 접근 설정 조회 실패:", e);
    }
    applyAnalysisAccessState();
}

function applyAnalysisAccessState() {
    const state = window.analysisAccessState || { access_mode: 'all', admin_only: false, message: '' };
    const mode = state.access_mode || (state.admin_only ? 'admin_only' : 'all');
    const isAdmin = isAdminSessionActive();
    const isAllowed = isUserAllowedForRightsAnalysis();
    const restrictBanner = document.getElementById('analysisRestrictionBanner');
    const restrictText = document.getElementById('analysisRestrictionText');
    const adminBanner = document.getElementById('adminModeActiveBanner');
    const adminStatusLbl = document.getElementById('adminModeStatusLabel');
    const adminSubText = document.getElementById('adminModeSubText');
    const headerCtrlBtn = document.getElementById('adminAccessControlBtnHeader');

    if (restrictText && state.message) {
        restrictText.innerText = state.message;
    }

    if (!isAllowed) {
        if (restrictBanner) restrictBanner.style.display = 'block';
        if (adminBanner) adminBanner.style.display = 'none';
        if (caseNumberInput) {
            caseNumberInput.disabled = true;
            caseNumberInput.placeholder = mode === 'selected'
                ? '🎯 지정 허용 회원 전용 모드로 제한 중 (관리자 지정 회원만 권리분석 가능)'
                : '🔒 관리자 전용 모드로 이용 제한 중 (관리자 로그인 필요)';
        }
        if (searchCaseBtn) searchCaseBtn.disabled = true;
        if (secondaryInputScreen) secondaryInputScreen.style.display = 'none';
        if (headerCtrlBtn) {
            headerCtrlBtn.innerHTML = '<i class="fa-solid fa-lock"></i> 관리자 로그인 (제한중)';
            headerCtrlBtn.style.background = 'rgba(239, 68, 68, 0.25)';
            headerCtrlBtn.style.borderColor = '#ef4444';
            headerCtrlBtn.style.color = '#fca5a5';
        }
    } else {
        if (restrictBanner) restrictBanner.style.display = 'none';
        if (caseNumberInput) {
            caseNumberInput.disabled = false;
            caseNumberInput.placeholder = '사건번호 (예: 2024타경5020)';
        }
        if (searchCaseBtn) searchCaseBtn.disabled = false;

        if (isAdmin) {
            if (adminBanner) adminBanner.style.display = 'flex';
            if (adminStatusLbl && adminSubText) {
                if (mode === 'admin_only') {
                    adminStatusLbl.innerText = '🔒 현재 [관리자 1인만 권리분석 가능] 제한 ON';
                    adminSubText.innerText = '일반 회원의 권리분석은 차단되어 있으며, 관리자 권한으로 정상 이용 중입니다.';
                } else if (mode === 'selected') {
                    const cnt = state.allowed_count || (state.allowed_user_ids || []).length || 0;
                    const namesPreview = (state.allowed_user_names || []).slice(0, 5).join(', ');
                    adminStatusLbl.innerText = `🎯 현재 [지정 회원(${cnt}명) + 관리자만 권리분석 허용] 모드 ON`;
                    adminSubText.innerText = cnt > 0
                        ? `지정 허용 회원(${namesPreview}${cnt > 5 ? ' 외' : ''}) 및 관리자만 권리분석 창을 열 수 있습니다.`
                        : '현재 지정된 허용 회원이 0명이므로 관리자만 열람 가능합니다. [이용제한 설정]에서 회원을 지정하세요.';
                } else {
                    adminStatusLbl.innerText = '🔓 현재 [전체 승인 회원 권리분석 허용] 모드';
                    adminSubText.innerText = '우측 [이용제한 설정] 버튼으로 지정 회원 전용 또는 관리자 전용 모드로 전환할 수 있습니다.';
                }
            }
            if (headerCtrlBtn) {
                headerCtrlBtn.innerHTML = mode === 'admin_only'
                    ? '<i class="fa-solid fa-user-lock"></i> 권리분석 제한(관리자전용)'
                    : (mode === 'selected'
                        ? `<i class="fa-solid fa-user-check"></i> 권리분석 제한(지정회원 ${state.allowed_count || 0}명)`
                        : '<i class="fa-solid fa-sliders"></i> 권리분석 제한설정');
                headerCtrlBtn.style.background = mode === 'admin_only'
                    ? 'rgba(239, 68, 68, 0.28)'
                    : (mode === 'selected' ? 'rgba(56, 189, 248, 0.24)' : 'rgba(16, 185, 129, 0.2)');
                headerCtrlBtn.style.borderColor = mode === 'admin_only'
                    ? '#ef4444'
                    : (mode === 'selected' ? '#0284c7' : '#10b981');
                headerCtrlBtn.style.color = mode === 'admin_only'
                    ? '#fca5a5'
                    : (mode === 'selected' ? '#7dd3fc' : '#6ee7b7');
            }
        } else {
            if (adminBanner) adminBanner.style.display = 'none';
            if (headerCtrlBtn) {
                headerCtrlBtn.innerHTML = '<i class="fa-solid fa-user-shield"></i> 관리자 모드';
                headerCtrlBtn.style.background = 'rgba(187, 0, 255, 0.16)';
                headerCtrlBtn.style.borderColor = 'var(--neon-purple)';
                headerCtrlBtn.style.color = '#e9d5ff';
            }
        }
    }
}

function promptAdminLoginModal() {
    const adminLoginModal = document.getElementById('adminLoginModal');
    const adminInput = document.getElementById('adminKeyModalInput');
    if (adminLoginModal) {
        adminLoginModal.style.display = 'flex';
        if (adminInput) {
            adminInput.value = '';
            adminInput.removeAttribute('readonly');
            adminInput.focus();
        }
    }
}

async function loadMembersIntoRestrictionModal() {
    const listEl = document.getElementById('modalSelectedMembersList');
    const countSpan = document.getElementById('modalSelectedCountSpan');
    const key = getEffectiveAdminKey();
    if (!listEl || !key) return;
    try {
        const res = await fetch('/api/admin/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ admin_key: key })
        });
        const json = await res.json();
        if (json.status === 'success') {
            const activeUsers = (json.data || []).filter(u => (u.status || 'active') === 'active');
            if (activeUsers.length === 0) {
                listEl.innerHTML = '<span style="font-size:0.78rem; color:#64748b;">승인된 정상 정회원이 없습니다.</span>';
                if (countSpan) countSpan.innerText = '(0명 선택됨)';
                return;
            }
            const updateModalCount = () => {
                const checkedCnt = listEl.querySelectorAll('input.modal-member-rights-chk:checked').length;
                if (countSpan) countSpan.innerText = `(${checkedCnt}명 선택됨 / 전체 ${activeUsers.length}명)`;
            };
            listEl.innerHTML = activeUsers.map(u => {
                const checked = u.can_use_rights_analysis ? 'checked' : '';
                return `<label style="display:inline-flex; align-items:center; gap:5px; padding:4px 9px; border-radius:14px; background:rgba(30,41,59,0.9); border:1px solid rgba(56,189,248,0.3); color:#f8fafc; font-size:0.8rem; cursor:pointer;">
                    <input type="checkbox" class="modal-member-rights-chk" value="${u.id}" ${checked}>
                    <span>${u.username}</span>
                </label>`;
            }).join('');
            listEl.querySelectorAll('input.modal-member-rights-chk').forEach(chk => {
                chk.addEventListener('change', () => {
                    updateModalCount();
                    const selRadio = document.querySelector('input[name="analysisAccessModeRadio"][value="selected"]');
                    if (selRadio && chk.checked) selRadio.checked = true;
                });
            });
            updateModalCount();
        }
    } catch (e) {
        console.warn("정회원 목록 로드 실패:", e);
    }
}

function openAnalysisRestrictionModal() {
    if (!isAdminSessionActive()) {
        promptAdminLoginModal();
        return;
    }
    const modal = document.getElementById('analysisRestrictionModal');
    if (!modal) return;
    const state = window.analysisAccessState || { access_mode: 'all', admin_only: false, message: '' };
    const mode = state.access_mode || (state.admin_only ? 'admin_only' : 'all');
    const radios = document.getElementsByName('analysisAccessModeRadio');
    for (const r of radios) {
        r.checked = (r.value === mode);
    }
    const msgInput = document.getElementById('restrictionMessageInput');
    if (msgInput && state.message) {
        msgInput.value = state.message;
    }
    loadMembersIntoRestrictionModal();
    modal.style.display = 'flex';
}

function closeAnalysisRestrictionModal() {
    const modal = document.getElementById('analysisRestrictionModal');
    if (modal) modal.style.display = 'none';
}

async function handleSaveAnalysisRestriction() {
    const key = getEffectiveAdminKey();
    if (!key) {
        alert("관리자 인증이 필요합니다.");
        return;
    }
    const radios = document.getElementsByName('analysisAccessModeRadio');
    let accessMode = 'all';
    for (const r of radios) {
        if (r.checked) accessMode = r.value;
    }
    const checkedIds = Array.from(document.querySelectorAll('input.modal-member-rights-chk:checked'))
        .map(el => parseInt(el.value, 10))
        .filter(n => !isNaN(n));
    const msgInput = document.getElementById('restrictionMessageInput');
    const message = msgInput ? msgInput.value.trim() : '';

    try {
        const res = await fetch('/api/admin/analysis_access_config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                admin_key: key,
                access_mode: accessMode,
                admin_only: accessMode === 'admin_only',
                allowed_user_ids: checkedIds,
                message: message
            })
        });
        const json = await res.json();
        if (json.status === 'success') {
            window.analysisAccessState = {
                access_mode: json.access_mode || accessMode,
                admin_only: Boolean(json.admin_only),
                restricted: Boolean(json.restricted),
                allowed_user_ids: json.allowed_user_ids || checkedIds,
                allowed_user_names: json.allowed_user_names || [],
                allowed_count: json.allowed_count || checkedIds.length,
                member_allowed: Boolean(json.member_allowed),
                message: json.message || message,
                updated_at: json.updated_at || ''
            };
            closeAnalysisRestrictionModal();
            applyAnalysisAccessState();
            alert(json.summary || '권리분석 이용권한 설정이 저장되었습니다.');
        } else {
            alert('설정 저장 실패: ' + (json.message || '오류'));
        }
    } catch (e) {
        alert('설정 저장 중 네트워크 오류: ' + e.message);
    }
}

async function initAnalysisAccessControl() {
    const headerBtn = document.getElementById('adminAccessControlBtnHeader');
    if (headerBtn) {
        headerBtn.addEventListener('click', () => {
            if (isAdminSessionActive()) {
                openAnalysisRestrictionModal();
            } else {
                promptAdminLoginModal();
            }
        });
    }
    const unlockBtn = document.getElementById('unlockAsAdminBtn');
    if (unlockBtn) {
        unlockBtn.addEventListener('click', promptAdminLoginModal);
    }
    const quickOpenBtn = document.getElementById('openRestrictionModalQuickBtn');
    if (quickOpenBtn) {
        quickOpenBtn.addEventListener('click', openAnalysisRestrictionModal);
    }
    const quickLogoutBtn = document.getElementById('logoutAdminQuickBtn');
    if (quickLogoutBtn) {
        quickLogoutBtn.addEventListener('click', () => {
            if (confirm("관리자 모드를 로그아웃 하시겠습니까?")) {
                performAdminLogout();
            }
        });
    }
    const closeBtn = document.getElementById('closeRestrictionModalBtn');
    if (closeBtn) closeBtn.addEventListener('click', closeAnalysisRestrictionModal);
    const cancelBtn = document.getElementById('cancelRestrictionModalBtn');
    if (cancelBtn) cancelBtn.addEventListener('click', closeAnalysisRestrictionModal);
    const saveBtn = document.getElementById('saveRestrictionModalBtn');
    if (saveBtn) saveBtn.addEventListener('click', handleSaveAnalysisRestriction);

    await fetchAnalysisAccessConfig();
}
