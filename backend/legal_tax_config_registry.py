# -*- coding: utf-8 -*-
"""
법규·세무·대출·명도·소액임차인 동적 설정 레지스트리 (Dynamic Legal & Tax Config Registry)
- 하드코딩된 세율/대출한도/수리비/소액임차인 최우선변제 파라미터 사용을 금지하고,
  모든 권리·수익성·세무 산출 및 AI 모델 라우팅이 본 동적 레지스트리(JSON/환경변수 오버라이드 지원)를 참조합니다.
"""

import os
import json
from typing import Dict, Any, List, Tuple


DEFAULT_LEGAL_TAX_REGISTRY: Dict[str, Any] = {
    "version": "2026.11.2",
    "ai_models": {
        "deep_research_agents": [
            "deep-research-max-preview-04-2026",
            "deep-research-pro-preview-12-2025",
        ],
        "gemini_priority": [
            "gemini-3.1-pro-preview",
            "gemini-pro-latest",
            "gemini-2.5-pro",
            "gemini-3.8-flash",
            "gemini-3.6-flash",
            "gemini-3-flash-preview",
            "gemini-2.5-flash",
        ],
        "enable_google_search_grounding": True,
        "max_output_tokens": 16384,
        "temperature": 0.25,
        "api_base_url": "https://generativelanguage.googleapis.com/v1beta/models",
        "interactions_url": "https://generativelanguage.googleapis.com/v1beta/interactions",
        "timeout_seconds": 150,
        "deep_research_max_wait_seconds": 240,
    },
    "regulated_areas": {
        "seoul_keywords": ["강남구", "서초구", "송파구", "용산구"],
        "gyeonggi_keywords": [],
        "overcrowding_control_keywords": [
            "서울", "과천", "성남", "분당", "수정구", "중원구", "수원", "고양",
            "안양", "부천", "의정부", "광명", "군포", "의왕", "하남", "구리",
        ],
    },
    "small_tenant_priority": {
        "residential": [
            {
                "effective_from": "2023-02-14",
                "seoul": {"deposit_max": 165000000, "priority_max": 55000000},
                "overcrowded": {"deposit_max": 145000000, "priority_max": 48000000},
                "metro": {"deposit_max": 85000000, "priority_max": 28000000},
                "other": {"deposit_max": 75000000, "priority_max": 25000000},
            },
            {
                "effective_from": "2021-05-11",
                "seoul": {"deposit_max": 150000000, "priority_max": 50000000},
                "overcrowded": {"deposit_max": 130000000, "priority_max": 43000000},
                "metro": {"deposit_max": 70000000, "priority_max": 23000000},
                "other": {"deposit_max": 60000000, "priority_max": 20000000},
            },
            {
                "effective_from": "2018-09-18",
                "seoul": {"deposit_max": 110000000, "priority_max": 37000000},
                "overcrowded": {"deposit_max": 100000000, "priority_max": 34000000},
                "metro": {"deposit_max": 60000000, "priority_max": 20000000},
                "other": {"deposit_max": 50000000, "priority_max": 17000000},
            },
        ],
        "commercial": [
            {
                "effective_from": "2019-04-02",
                "seoul": {"converted_limit": 900000000, "deposit_max": 65000000, "priority_max": 22000000},
                "overcrowded": {"converted_limit": 690000000, "deposit_max": 55000000, "priority_max": 19000000},
                "metro": {"converted_limit": 540000000, "deposit_max": 38000000, "priority_max": 13000000},
                "other": {"converted_limit": 370000000, "deposit_max": 30000000, "priority_max": 10000000},
            }
        ],
    },
    "acquisition_tax": {
        "non_residential_rate": 0.046,
        "officetel_rate": 0.046,
        "corporate_overcrowded_young_surtax_rate": 0.096,
        "corporate_residential_rate": 0.124,
        "residential_individual": {
            "non_regulated": {
                "0": {"under_600m": 0.011, "600m_to_900m": 0.022, "over_900m": 0.033},
                "1": {"under_600m": 0.011, "600m_to_900m": 0.022, "over_900m": 0.033},
                "2": {"flat": 0.011, "note": "비조정 2주택 기본세율(1~3%) 적용"},
                "3": {"flat": 0.084, "note": "비조정 3주택 이상 중과세율(8.4%) 적용"},
            },
            "regulated": {
                "0": {"under_600m": 0.011, "600m_to_900m": 0.022, "over_900m": 0.033},
                "1": {"flat": 0.011, "note": "일시적 2주택 요건 충족 시 기본세율(1~3%), 미충족 시 8.4%"},
                "2": {"flat": 0.084, "note": "조정대상지역 2주택 중과(8.4%)"},
                "3": {"flat": 0.124, "note": "조정대상지역 3주택 이상 중과(12.4%)"},
            },
        },
        "legal_and_registration_fee_rate": 0.008,
    },
    "exit_tax": {
        "individual_residential_short_under_1yr": 0.77,
        "individual_residential_1_to_2yr": 0.66,
        "individual_non_residential_short_under_1yr": 0.55,
        "individual_non_residential_1_to_2yr": 0.44,
        "individual_general_effective_rate": 0.24,
        "business_dealer_effective_rate": 0.264,
        "corporate_effective_rate": 0.209,
        "corporate_residential_surtax_rate": 0.20,
        "basic_deduction_krw": 2500000,
    },
    "loan_policy": {
        "residential": {
            "non_regulated_ltv": 0.70,
            "regulated_ltv": 0.40,
            "multi_home_regulated_ltv": 0.30,
            "annual_interest_rate": 0.048,
            "dsr_limit": 0.40,
            "tier_caps_krw": {
                "under_15b": 600000000,
                "15b_to_25b": 400000000,
                "over_25b": 200000000,
            },
        },
        "non_residential": {
            "standard_ltv": 0.70,
            "corporate_ltv": 0.75,
            "annual_interest_rate": 0.052,
            "rti_commercial_min": 1.25,
            "rti_residential_rental_min": 1.50,
        },
    },
    "eviction_and_capex": {
        "eviction_per_pyeong_krw": 120000,
        "eviction_min_krw": 2500000,
        "eviction_special_risk_surcharge_krw": 5000000,
        "prompt_formula_base_repair_per_pyeong_krw": 1500000,
        "prompt_formula_age_ratios": {
            "under_10yr": 0.20,
            "under_25yr": 0.50,
            "under_35yr": 0.75,
            "over_35yr": 1.00,
        },
        "holding_months_short": 6,
        "holding_months_long": 36,
        "brokerage_fee_rate": 0.005,
    },
}


def get_legal_tax_config() -> Dict[str, Any]:
    """동적 설정 레지스트리 반환 (외부 JSON 설정 파일 및 환경변수 오버라이드 자동 병합)."""
    cfg = json.loads(json.dumps(DEFAULT_LEGAL_TAX_REGISTRY))
    override_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "legal_tax_config.json")
    if os.path.exists(override_path):
        try:
            with open(override_path, "r", encoding="utf-8") as f:
                custom = json.load(f)
            if isinstance(custom, dict):
                for k, v in custom.items():
                    if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                        cfg[k].update(v)
                    else:
                        cfg[k] = v
        except Exception as e:
            print(f"[ConfigRegistry] 설정 오버라이드 로드 경고: {e}")

    env_models = os.getenv("GEMINI_MODEL_PRIORITY", "").strip()
    if env_models:
        cfg["ai_models"]["gemini_priority"] = [m.strip() for m in env_models.split(",") if m.strip()]

    return cfg


def compute_acquisition_tax_rate(
    is_residential: bool,
    investor_type: str,
    house_count: int,
    is_regulated: bool,
    bid_price_krw: int,
    cfg: Dict[str, Any] = None,
    property_type: str = "",
    address: str = "",
) -> Tuple[float, str]:
    """동적 레지스트리 기준 취득세율(지방교육세·농특세 포함) 및 근거 설명을 반환합니다."""
    cfg = cfg or get_legal_tax_config()
    acq = cfg["acquisition_tax"]

    if "오피스텔" in (property_type or ""):
        rate = float(acq.get("officetel_rate", 0.046))
        return rate, f"오피스텔 표준 취득세율 {rate*100:.1f}% (주택수·법인 무관, 주거용 전입 시 주택수 합산 유의)"

    if not is_residential:
        rate = float(acq["non_residential_rate"])
        overcrowded_kws = cfg.get("regulated_areas", {}).get("overcrowding_control_keywords", [])
        is_overcrowded = any(kw in (address or "") for kw in overcrowded_kws)
        if "법인" in (investor_type or "") and is_overcrowded:
            surtax = float(acq.get("corporate_overcrowded_young_surtax_rate", 0.096))
            return rate, (
                f"일반 법인 상가·토지 기본 취득세율 {rate*100:.1f}% 적용 "
                f"(단, 과밀억제권역 내 설립 5년 이내 법인 취득 시 {surtax*100:.1f}% 중과 유의)"
            )
        return rate, f"비주거용(상가·근린시설·숙박·토지·공장 등) 표준 취득세율 {rate*100:.1f}%"

    if "법인" in (investor_type or ""):
        rate = float(acq["corporate_residential_rate"])
        return rate, f"법인 주택 취득 중과세율 {rate*100:.1f}% (규제지역·주택수 무관)"

    reg_key = "regulated" if is_regulated else "non_regulated"
    hc_key = str(min(max(int(house_count or 0), 0), 3))
    table = acq["residential_individual"][reg_key].get(hc_key, {})

    if "flat" in table:
        rate = float(table["flat"])
        note = table.get("note", "주택수·규제지역 기준 세율")
        return rate, f"{note} ({rate*100:.1f}%)"

    if bid_price_krw <= 600_000_000:
        rate = float(table.get("under_600m", 0.011))
    elif bid_price_krw <= 900_000_000:
        rate = float(table.get("600m_to_900m", 0.022))
    else:
        rate = float(table.get("over_900m", 0.033))
    return rate, f"{investor_type} {hc_key}주택({'조정' if is_regulated else '비조정'}) 가액구간 취득세율 ({rate*100:.1f}%)"


def compute_exit_tax_rates(
    is_residential: bool,
    investor_type: str,
    investment_duration: str,
    cfg: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """동적 레지스트리 기준 단기/장기 출구 세율(지방소득세 포함)을 반환합니다."""
    cfg = cfg or get_legal_tax_config()
    ex = cfg["exit_tax"]

    if "법인" in (investor_type or ""):
        base_corp = float(ex["corporate_effective_rate"])
        surtax = float(ex["corporate_residential_surtax_rate"]) if is_residential else 0.0
        eff = base_corp + surtax
        return {
            "effective_rate": eff,
            "short_rate_pct": int(round(eff * 100)),
            "long_rate_pct": int(round(base_corp * 100)),
            "deduction_krw": 0,
            "label": (
                f"법인세 실효세율 약 {eff*100:.1f}% (기본 법인세 + 지방소득세"
                f"{' + 주택/비사업용토지 추가과세 20%p 반영' if is_residential else ''})"
            ),
        }

    if "매매사업자" in (investor_type or ""):
        eff = float(ex["business_dealer_effective_rate"])
        return {
            "effective_rate": eff,
            "short_rate_pct": int(round(eff * 100)),
            "long_rate_pct": int(round(eff * 100)),
            "deduction_krw": int(ex["basic_deduction_krw"]),
            "label": f"부동산 매매사업자 종합소득세 기본세율 구간 (실효 약 {eff*100:.1f}%, 필요경비 폭넓게 인정)",
        }

    is_short = any(k in (investment_duration or "") for k in ["단기", "6개월", "1년"])
    if is_residential:
        short_r = float(ex["individual_residential_short_under_1yr"])
        long_r = float(ex["individual_general_effective_rate"])
    else:
        short_r = float(ex["individual_non_residential_short_under_1yr"])
        long_r = float(ex["individual_general_effective_rate"])

    eff = short_r if is_short else long_r
    return {
        "effective_rate": eff,
        "short_rate_pct": int(round(short_r * 100)),
        "long_rate_pct": int(round(long_r * 100)),
        "deduction_krw": int(ex["basic_deduction_krw"]),
        "label": (
            f"개인 {'1년 내 단기양도 중과세율' if is_short else '2년 이상 보유 일반과세 실효세율'} "
            f"약 {eff*100:.1f}% (지방소득세 10% 포함)"
        ),
    }


def get_small_tenant_threshold(address: str, is_residential: bool = True, cfg: Dict[str, Any] = None) -> Dict[str, Any]:
    """주소 권역에 따른 소액임차인 보증금 상한 및 최우선변제금 기준을 동적 레지스트리에서 반환합니다."""
    cfg = cfg or get_legal_tax_config()
    addr = address or ""
    overcrowded = cfg.get("regulated_areas", {}).get("overcrowding_control_keywords", [])
    if "서울" in addr:
        region_key, region_label = "seoul", "서울특별시"
    elif any(k in addr for k in overcrowded):
        region_key, region_label = "overcrowded", "수도권 과밀억제권역"
    elif any(k in addr for k in ["인천", "부산", "대구", "대전", "광주", "울산", "세종", "용인", "화성", "김포", "파주", "안산"]):
        region_key, region_label = "metro", "광역시·용인·화성·세종·김포 등"
    else:
        region_key, region_label = "other", "기타 지역"

    if is_residential:
        latest = cfg["small_tenant_priority"]["residential"][0]
        tier = latest.get(region_key, latest["other"])
        return {
            "region_label": region_label,
            "effective_from": latest["effective_from"],
            "deposit_max": tier["deposit_max"],
            "priority_max": tier["priority_max"],
            "converted_limit": 0,
        }
    else:
        latest = cfg["small_tenant_priority"]["commercial"][0]
        tier = latest.get(region_key, latest["other"])
        return {
            "region_label": region_label,
            "effective_from": latest["effective_from"],
            "deposit_max": tier["deposit_max"],
            "priority_max": tier["priority_max"],
            "converted_limit": tier["converted_limit"],
        }
