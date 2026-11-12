import os
import re
import glob
import time
import sqlite3
import io
import sys
import pandas as pd
import numpy as np

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'map_data.db')
SB_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'small_business.db')
DATA_RP_DIR = os.path.join(BASE_DIR, 'data', '실거래가')
FALLBACK_RP_DIR = os.path.join(BASE_DIR, 'realprice')

# Grid size definitions (approx. 250m)
LAT_STEP = 0.00225
LNG_STEP = 0.0028
CURRENT_YEAR = 2026

TARGET_SIDOS = ('서울특별시', '경기도', '인천광역시', '충청남도', '강원특별자치도')


def clean_spaces_fast(s: str) -> str:
    s = s.strip()
    if '  ' in s:
        return ' '.join(s.split())
    return s


def extract_sgg_prefix(sgg: str) -> str:
    parts = sgg.split()
    if len(parts) <= 2:
        return parts[0] if parts else ''
    kept = [parts[0]]
    for p in parts[1:]:
        if p.endswith(('시', '군', '구')):
            kept.append(p)
        else:
            break
    return ' '.join(kept)


def select_latest_molit_files():
    """
    Selects the newest non-empty MOLIT_{시도}_{유형}_{거래유형}_{seq}.csv per (시도, 유형, 거래유형)
    from data/실거래가, falling back to realprice/ when a file is 0-byte or missing.
    """
    selected = {}
    fallbacks_used = []

    def scan_dir(dpath, is_fallback=False):
        if not os.path.exists(dpath):
            return
        for fp in glob.glob(os.path.join(dpath, 'MOLIT_*.csv')):
            sz = os.path.getsize(fp)
            if sz == 0:
                continue
            fn = os.path.basename(fp)
            m = re.match(r'^MOLIT_([^_]+)_([^_]+)_(매매|전월세)_(\d+)\.csv$', fn)
            if not m:
                continue
            sido, ptype, dtype, seq = m.group(1), m.group(2), m.group(3), int(m.group(4))
            key = (sido, ptype, dtype)
            if not is_fallback:
                if key not in selected or seq > selected[key][0]:
                    selected[key] = (seq, fp, sz, False)
            else:
                if key not in selected:
                    selected[key] = (seq, fp, sz, True)
                    fallbacks_used.append((key, fp, sz))

    scan_dir(DATA_RP_DIR, is_fallback=False)
    scan_dir(FALLBACK_RP_DIR, is_fallback=True)
    return selected, fallbacks_used


def build_offline_geocoder(conn):
    """
    Builds a multi-level offline spatial lookup dictionary (exact lot -> exact road ->
    building name -> road street -> legal dong/ri -> sigungu) from map_data.db & small_business.db.
    """
    t0 = time.time()
    lot_coords = {}
    bldg_coords = {}
    road_exact = {}
    road_street_acc = {}
    dong_acc = {}
    sgg_acc = {}

    def add_acc(d, key, lat, lng):
        if not key:
            return
        cur = d.get(key)
        if cur is None:
            d[key] = [lat, lng, 1]
        else:
            cur[0] += lat
            cur[1] += lng
            cur[2] += 1

    cur = conn.cursor()

    # 1. realprice_addr_cache
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='realprice_addr_cache'")
        if cur.fetchone():
            for addr, lat, lng in cur.execute("SELECT address, lat, lng FROM realprice_addr_cache WHERE lat IS NOT NULL AND lng IS NOT NULL"):
                if addr and lat > 30 and lng > 120:
                    lot_coords[clean_spaces_fast(addr)] = (float(lat), float(lng))
    except Exception:
        pass

    # 2. auctions
    try:
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auctions'")
        if cur.fetchone():
            for addr, lat, lng in cur.execute("SELECT address, lat, lng FROM auctions WHERE lat IS NOT NULL AND lng IS NOT NULL"):
                if not addr:
                    continue
                lat, lng = float(lat), float(lng)
                if lat <= 30 or lng <= 120:
                    continue
                clean = clean_spaces_fast(addr.split('(')[0].split('[')[0].split(',')[0])
                lot_coords[clean] = (lat, lng)
                parts = clean.split()
                if len(parts) >= 3:
                    dong_end = -1
                    for i, p in enumerate(parts):
                        if p.endswith(('동', '읍', '면', '리', '가')):
                            dong_end = i
                    if dong_end >= 1:
                        add_acc(dong_acc, ' '.join(parts[:dong_end + 1]), lat, lng)
                        if dong_end >= 2 and parts[dong_end].endswith('리'):
                            add_acc(dong_acc, ' '.join(parts[:dong_end]), lat, lng)
                    add_acc(sgg_acc, extract_sgg_prefix(clean), lat, lng)
    except Exception:
        pass

    # 3. small_business.db (Sequential scan without idx_sb_lat_lng random I/O!)
    if os.path.exists(SB_DB_PATH):
        sb_conn = sqlite3.connect(SB_DB_PATH)
        sb_cur = sb_conn.cursor()
        placeholders = ','.join(['?'] * len(TARGET_SIDOS))
        # Unary +lat / +lng prevents SQLite from choosing idx_sb_lat_lng random seeks!
        q = f"""
            SELECT sido_name, sigungu_name, dong_name, lot_addr, road_addr, building_name, lat, lng
            FROM small_business
            WHERE sido_name IN ({placeholders})
              AND +lat > 33 AND +lng > 124
        """
        for sido, sigungu, dong, lot_addr, road_addr, bldg_name, lat, lng in sb_cur.execute(q, TARGET_SIDOS):
            lat = float(lat)
            lng = float(lng)
            if lot_addr:
                la = clean_spaces_fast(lot_addr)
                if la not in lot_coords:
                    lot_coords[la] = (lat, lng)
                if ' 산 ' in la:
                    la_nosan = la.replace(' 산 ', ' 산')
                    if la_nosan not in lot_coords:
                        lot_coords[la_nosan] = (lat, lng)
                lparts = la.split()
                if len(lparts) >= 3:
                    last_tok = lparts[-1]
                    if last_tok[0].isdigit() or (last_tok.startswith('산') and len(last_tok) > 1):
                        dong_full = ' '.join(lparts[:-1])
                        add_acc(dong_acc, dong_full, lat, lng)
                        if bldg_name:
                            bn = bldg_name.strip()
                            if bn:
                                bkey = f"{dong_full} {bn}"
                                if bkey not in bldg_coords:
                                    bldg_coords[bkey] = (lat, lng)

            if sido and sigungu and dong:
                add_acc(dong_acc, f"{sido} {sigungu} {dong}", lat, lng)
                add_acc(sgg_acc, f"{sido} {sigungu}", lat, lng)

            if road_addr:
                ra = clean_spaces_fast(road_addr)
                if ra not in road_exact:
                    road_exact[ra] = (lat, lng)
                rparts = ra.split()
                if len(rparts) >= 3:
                    # Find road token ending with 로/길
                    sgg_p = extract_sgg_prefix(ra)
                    for tok in rparts[1:]:
                        if tok.endswith(('로', '길')):
                            add_acc(road_street_acc, f"{sgg_p}|{tok}", lat, lng)
                            break
        sb_conn.close()

    road_street = {k: (v[0] / v[2], v[1] / v[2]) for k, v in road_street_acc.items()}
    dong_centers = {k: (v[0] / v[2], v[1] / v[2]) for k, v in dong_acc.items()}
    sgg_centers = {k: (v[0] / v[2], v[1] / v[2]) for k, v in sgg_acc.items()}

    print(
        f"[Geocoder] Built in {time.time() - t0:.1f}s | "
        f"lot={len(lot_coords):,}, road_exact={len(road_exact):,}, bldg={len(bldg_coords):,}, "
        f"street={len(road_street):,}, dong={len(dong_centers):,}, sgg={len(sgg_centers):,}",
        flush=True
    )
    return lot_coords, bldg_coords, road_exact, road_street, dong_centers, sgg_centers


def clean_num_series(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(',', '', regex=False).str.strip(), errors='coerce')


def resolve_coords_memoized(df: pd.DataFrame, geocoder_pack, global_memo: dict):
    lot_coords, bldg_coords, road_exact, road_street, dong_centers, sgg_centers = geocoder_pack

    sgg_list = df['시군구'].fillna('').astype(str).str.strip().tolist()
    n = len(sgg_list)

    jibun_list = (
        df['번지'].fillna('').astype(str).str.strip().tolist() if '번지' in df.columns
        else (df['지번'].fillna('').astype(str).str.strip().tolist() if '지번' in df.columns else [''] * n)
    )
    road_list = df['도로명'].fillna('').astype(str).str.strip().tolist() if '도로명' in df.columns else [''] * n
    bldg_list = (
        df['단지명'].fillna('').astype(str).str.strip().tolist() if '단지명' in df.columns
        else (df['건물명'].fillna('').astype(str).str.strip().tolist() if '건물명' in df.columns else [''] * n)
    )

    lats = np.full(n, np.nan, dtype=np.float64)
    lngs = np.full(n, np.nan, dtype=np.float64)
    hits = [0, 0, 0, 0, 0, 0, 0]  # miss, lot, road_exact, bldg, street, dong, sgg

    for i in range(n):
        sgg = sgg_list[i]
        if not sgg or sgg == 'nan':
            hits[0] += 1
            continue
        jb = jibun_list[i]
        rd = road_list[i]
        bd = bldg_list[i]

        mkey = (sgg, jb, rd, bd)
        cached = global_memo.get(mkey)
        if cached is not None:
            lats[i], lngs[i], htype = cached
            hits[htype] += 1
            continue

        sgg_norm = clean_spaces_fast(sgg)
        coord = None
        htype = 0
        sgg_pref = None

        # 1. Exact lot address
        if jb and '*' not in jb and jb != 'nan' and jb != '-':
            coord = lot_coords.get(f"{sgg_norm} {jb}")
            if coord is not None:
                htype = 1

        # 2. Exact road address
        if coord is None and rd and rd != 'nan' and rd != '-':
            sgg_pref = extract_sgg_prefix(sgg_norm)
            rd_norm = clean_spaces_fast(rd)
            last_tok = rd_norm.split()[-1]
            if any(ch.isdigit() for ch in last_tok):
                coord = road_exact.get(f"{sgg_pref} {rd_norm}")
                if coord is not None:
                    htype = 2

        # 3. Building / complex name
        if coord is None and bd and bd != 'nan' and bd != '-':
            coord = bldg_coords.get(f"{sgg_norm} {bd}")
            if coord is not None:
                htype = 3

        # 4. Street-level center (handles masked lot numbers '1**' with road names!)
        if coord is None and rd and rd != 'nan' and rd != '-':
            if sgg_pref is None:
                sgg_pref = extract_sgg_prefix(sgg_norm)
            first_rd_tok = rd.split()[0]
            coord = road_street.get(f"{sgg_pref}|{first_rd_tok}")
            if coord is not None:
                htype = 4

        # 5. Legal dong / eup / myeon / ri center
        if coord is None:
            coord = dong_centers.get(sgg_norm)
            if coord is None:
                sp = sgg_norm.split()
                if len(sp) >= 3 and sp[-1].endswith('리'):
                    coord = dong_centers.get(' '.join(sp[:-1]))
            if coord is not None:
                htype = 5

        # 6. Sigungu center fallback
        if coord is None:
            if sgg_pref is None:
                sgg_pref = extract_sgg_prefix(sgg_norm)
            coord = sgg_centers.get(sgg_pref)
            if coord is not None:
                htype = 6

        if coord is not None:
            lats[i], lngs[i] = coord[0], coord[1]
            global_memo[mkey] = (coord[0], coord[1], htype)
            hits[htype] += 1
        else:
            global_memo[mkey] = (np.nan, np.nan, 0)
            hits[0] += 1

    return lats, lngs, hits


def parse_single_csv(fp: str, raw_ptype: str, deal_type: str, geocoder_pack, global_memo: dict):
    try:
        df = pd.read_csv(fp, skiprows=15, encoding='cp949', low_memory=False)
    except UnicodeDecodeError:
        df = pd.read_csv(fp, skiprows=15, encoding='utf-8-sig', low_memory=False)

    df.columns = [c.strip() for c in df.columns]
    if '시군구' not in df.columns or len(df) == 0:
        return None, 'missing_sgg_or_empty'

    # Skip duplicate 분양권_전월세 files that contain 매매 columns without 보증금
    if deal_type == '전월세' and not any(c in df.columns for c in ('보증금(만원)', '보증금')):
        return None, 'skipped_duplicate_presale_without_deposit'

    # Exclude cancelled deals (해제사유발생일)
    if '해제사유발생일' in df.columns:
        c_col = df['해제사유발생일'].fillna('-').astype(str).str.strip()
        df = df[c_col.isin(['-', '', 'nan', 'None'])]
        if len(df) == 0:
            return None, 'all_cancelled'

    area_col = None
    for cand in (
        '전용면적(㎡)', '전용/연면적(㎡)', '연면적(㎡)', '건물면적(㎡)',
        '계약면적(㎡)', '계약면적', '대지면적(㎡)', '전용면적', '연면적', '대지면적'
    ):
        if cand in df.columns:
            area_col = cand
            break
    if not area_col:
        return None, 'no_area_col'

    pyeong = clean_num_series(df[area_col]) / 3.30578

    if deal_type == '매매':
        pcol = '거래금액(만원)' if '거래금액(만원)' in df.columns else ('거래금액' if '거래금액' in df.columns else None)
        if not pcol:
            return None, 'no_price_col'
        price = clean_num_series(df[pcol])
        deposit = pd.Series(np.zeros(len(df)), index=df.index)
        rent = pd.Series(np.zeros(len(df)), index=df.index)
        valid_mask = (pyeong > 0.1) & (price > 0)
    else:
        dcol = '보증금(만원)' if '보증금(만원)' in df.columns else '보증금'
        rcol = next((rc for rc in ('월세금(만원)', '월세(만원)', '월세금', '월세') if rc in df.columns), None)
        deposit = clean_num_series(df[dcol]).fillna(0.0)
        rent = clean_num_series(df[rcol]).fillna(0.0) if rcol else pd.Series(np.zeros(len(df)), index=df.index)
        price = pd.Series(np.zeros(len(df)), index=df.index)
        valid_mask = (pyeong > 0.1) & ((deposit > 0) | (rent > 0))

    df = df[valid_mask]
    if len(df) == 0:
        return None, 'no_valid_numeric_rows'

    pyeong_v = pyeong[valid_mask].values
    price_v = price[valid_mask].values
    dep_v = deposit[valid_mask].values
    rent_v = rent[valid_mask].values

    if raw_ptype == '연립다세대':
        ptypes = np.full(len(df), '다세대', dtype=object)
    elif raw_ptype == '단독다가구':
        ptypes = np.full(len(df), '단독', dtype=object)
    elif raw_ptype == '상업업무용':
        if '유형' in df.columns:
            ut = df['유형'].fillna('').astype(str).str.strip().values
            ptypes = np.where(ut == '집합', '상가(집합)', np.where(ut == '일반', '상가(일반)', '상업업무용'))
        else:
            ptypes = np.full(len(df), '상업업무용', dtype=object)
    elif raw_ptype == '공장창고등':
        if '유형' in df.columns:
            ut = df['유형'].fillna('').astype(str).str.strip().values
            ptypes = np.where(ut == '집합', '공장창고(집합)', np.where(ut == '일반', '공장창고(일반)', '공장창고등'))
        else:
            ptypes = np.full(len(df), '공장창고등', dtype=object)
    else:
        ptypes = np.full(len(df), raw_ptype, dtype=object)

    ym_v = pd.to_numeric(df['계약년월'], errors='coerce').fillna(0).astype(np.int32).values if '계약년월' in df.columns else np.zeros(len(df), dtype=np.int32)
    by_v = pd.to_numeric(df['건축년도'], errors='coerce').fillna(0).astype(np.int32).values if '건축년도' in df.columns else np.zeros(len(df), dtype=np.int32)
    fl_v = pd.to_numeric(df['층'], errors='coerce').fillna(0).astype(np.int32).values if '층' in df.columns else np.zeros(len(df), dtype=np.int32)

    lats, lngs, hits = resolve_coords_memoized(df, geocoder_pack, global_memo)
    cmask = ~np.isnan(lats) & ~np.isnan(lngs)

    out_df = pd.DataFrame({
        'property_type': ptypes[cmask],
        'deal_type': deal_type,
        'lat': lats[cmask],
        'lng': lngs[cmask],
        'lat_idx': (lats[cmask] / LAT_STEP).astype(np.int32),
        'lng_idx': (lngs[cmask] / LNG_STEP).astype(np.int32),
        'pyeong': pyeong_v[cmask],
        'price': price_v[cmask],
        'deposit': dep_v[cmask],
        'rent': rent_v[cmask],
        'ym': ym_v[cmask],
        'build_year': by_v[cmask],
        'floor': fl_v[cmask],
    })
    return out_df, hits


def aggregate_grids_vectorized(all_df: pd.DataFrame):
    """
    Pure Cython-vectorized Pandas groupby aggregation across all 1.5M+ transactions (~1.5s).
    """
    t0 = time.time()
    keys = ['property_type', 'lat_idx', 'lng_idx']

    # --- 1. SALE AGGREGATION ---
    df_s = all_df[all_df['deal_type'] == '매매'].copy()
    if len(df_s) > 0:
        pp = df_s['price'] / df_s['pyeong']
        py = df_s['pyeong']
        by = df_s['build_year']
        fl = df_s['floor']
        ym = df_s['ym']

        df_s['pp'] = pp
        df_s['u10'] = (py <= 10.0).astype(np.int32)
        df_s['p10_20'] = ((py > 10.0) & (py <= 20.0)).astype(np.int32)
        df_s['p20_30'] = ((py > 20.0) & (py <= 30.0)).astype(np.int32)
        df_s['o30'] = (py > 30.0).astype(np.int32)
        df_s['nb_pp'] = np.where((by > 1900) & ((CURRENT_YEAR - by) <= 5), pp, np.nan)
        df_s['ob_pp'] = np.where((by > 1900) & ((CURRENT_YEAR - by) >= 20), pp, np.nan)
        df_s['lowf_pp'] = np.where((fl >= 1) & (fl <= 3), pp, np.nan)
        df_s['highf_pp'] = np.where(fl >= 10, pp, np.nan)
        # H2 (202605~202610) vs H1 (202511~202604) price change rate
        df_s['h2_pp'] = np.where(ym >= 202605, pp, np.nan)
        df_s['h1_pp'] = np.where((ym > 0) & (ym < 202605), pp, np.nan)

        sale_agg = df_s.groupby(keys, sort=False).agg(
            sale_lat_sum=('lat', 'sum'),
            sale_lng_sum=('lng', 'sum'),
            sale_count=('pp', 'size'),
            avg_price_per_pyeong=('pp', 'median'),
            sales_count_under_10=('u10', 'sum'),
            sales_count_10_to_20=('p10_20', 'sum'),
            sales_count_20_to_30=('p20_30', 'sum'),
            sales_count_over_30=('o30', 'sum'),
            new_build_price=('nb_pp', 'median'),
            old_build_price=('ob_pp', 'median'),
            low_f_med=('lowf_pp', 'median'),
            high_f_med=('highf_pp', 'median'),
            s_h2_med=('h2_pp', 'median'),
            s_h2_cnt=('h2_pp', 'count'),
            s_h1_med=('h1_pp', 'median'),
            s_h1_cnt=('h1_pp', 'count'),
        ).reset_index()
    else:
        sale_agg = pd.DataFrame(columns=keys)

    # --- 2. RENT AGGREGATION ---
    df_r = all_df[all_df['deal_type'] == '전월세'].copy()
    if len(df_r) > 0:
        conv_dep = df_r['deposit'] + df_r['rent'] * 100.0
        dp = np.where(conv_dep > 0, conv_dep / df_r['pyeong'], np.nan)
        ym_r = df_r['ym']

        df_r['dp'] = dp
        df_r['pos_rent'] = np.where(df_r['rent'] > 0, df_r['rent'], np.nan)
        df_r['h2_dp'] = np.where(ym_r >= 202605, dp, np.nan)
        df_r['h1_dp'] = np.where((ym_r > 0) & (ym_r < 202605), dp, np.nan)

        rent_agg = df_r.groupby(keys, sort=False).agg(
            rent_lat_sum=('lat', 'sum'),
            rent_lng_sum=('lng', 'sum'),
            rent_count=('lat', 'size'),
            avg_deposit_per_pyeong=('dp', 'median'),
            avg_rent=('pos_rent', 'median'),
            r_h2_med=('h2_dp', 'median'),
            r_h2_cnt=('h2_dp', 'count'),
            r_h1_med=('h1_dp', 'median'),
            r_h1_cnt=('h1_dp', 'count'),
        ).reset_index()
    else:
        rent_agg = pd.DataFrame(columns=keys)

    # --- 3. MERGE & DERIVED METRICS ---
    m = pd.merge(sale_agg, rent_agg, on=keys, how='outer')

    for col in (
        'sale_lat_sum', 'sale_lng_sum', 'sale_count', 'avg_price_per_pyeong',
        'sales_count_under_10', 'sales_count_10_to_20', 'sales_count_20_to_30', 'sales_count_over_30',
        'new_build_price', 'old_build_price', 'low_f_med', 'high_f_med', 's_h2_cnt', 's_h1_cnt',
        'rent_lat_sum', 'rent_lng_sum', 'rent_count', 'avg_deposit_per_pyeong', 'avg_rent', 'r_h2_cnt', 'r_h1_cnt'
    ):
        if col in m.columns:
            m[col] = m[col].fillna(0.0)
        else:
            m[col] = 0.0

    m['sale_count'] = m['sale_count'].astype(np.int32)
    m['rent_count'] = m['rent_count'].astype(np.int32)
    m['transaction_count'] = m['sale_count'] + m['rent_count']

    m['lat'] = (m['sale_lat_sum'] + m['rent_lat_sum']) / m['transaction_count']
    m['lng'] = (m['sale_lng_sum'] + m['rent_lng_sum']) / m['transaction_count']

    m['jeonse_ratio'] = np.where(
        (m['avg_price_per_pyeong'] > 0) & (m['avg_deposit_per_pyeong'] > 0),
        np.minimum((m['avg_deposit_per_pyeong'] / m['avg_price_per_pyeong']) * 100.0, 200.0),
        0.0
    )

    m['age_premium_ratio'] = np.where(
        (m['new_build_price'] > 0) & (m['old_build_price'] > 0),
        m['new_build_price'] / m['old_build_price'],
        0.0
    )

    m['floor_sensitivity'] = np.where(
        (m['high_f_med'] > 0) & (m['low_f_med'] > 0),
        m['high_f_med'] / m['low_f_med'],
        0.0
    )

    # Sale & Rent change rate (%) where both H1 and H2 have >= 2 deals
    s_valid = (m['s_h2_cnt'] >= 2) & (m['s_h1_cnt'] >= 2) & (m['s_h1_med'] > 0) & m['s_h2_med'].notna()
    s_rate = np.where(s_valid, np.clip(np.round(((m['s_h2_med'] - m['s_h1_med']) / m['s_h1_med']) * 100.0, 2), -60.0, 120.0), np.nan)
    m['sale_price_change_rate'] = pd.Series(s_rate).where(~ np.isnan(s_rate), None)

    r_valid = (m['r_h2_cnt'] >= 2) & (m['r_h1_cnt'] >= 2) & (m['r_h1_med'] > 0) & m['r_h2_med'].notna()
    r_rate = np.where(r_valid, np.clip(np.round(((m['r_h2_med'] - m['r_h1_med']) / m['r_h1_med']) * 100.0, 2), -60.0, 120.0), np.nan)
    m['rent_price_change_rate'] = pd.Series(r_rate).where(~ np.isnan(r_rate), None)

    ordered_cols = [
        'lat_idx', 'lng_idx', 'property_type', 'lat', 'lng',
        'avg_price_per_pyeong', 'avg_deposit_per_pyeong', 'avg_rent',
        'jeonse_ratio', 'transaction_count', 'sale_count', 'rent_count',
        'age_premium_ratio', 'floor_sensitivity',
        'sales_count_under_10', 'sales_count_10_to_20', 'sales_count_20_to_30', 'sales_count_over_30',
        'sale_price_change_rate', 'rent_price_change_rate', 'new_build_price', 'old_build_price'
    ]
    for int_col in ('lat_idx', 'lng_idx', 'transaction_count', 'sale_count', 'rent_count',
                    'sales_count_under_10', 'sales_count_10_to_20', 'sales_count_20_to_30', 'sales_count_over_30'):
        m[int_col] = m[int_col].astype(int)

    records = list(m[ordered_cols].itertuples(index=False, name=None))
    print(f"[Aggregate] Built {len(records):,} 250m grid rows in {time.time() - t0:.1f}s", flush=True)
    return records


def main():
    t_total = time.time()
    print(f"=== MOLIT 실거래가 격자 오버레이 통합 적재 시작 ===", flush=True)
    print(f"Target DB: {DB_PATH}", flush=True)

    conn_ro = sqlite3.connect(DB_PATH, timeout=30.0)
    geocoder_pack = build_offline_geocoder(conn_ro)
    conn_ro.close()

    selected, fallbacks = select_latest_molit_files()
    print(f"Selected {len(selected)} latest MOLIT CSV files (fallbacks used: {len(fallbacks)})", flush=True)
    for fb_key, fb_fp, fb_sz in fallbacks:
        print(f"  [Fallback] {fb_key} -> {os.path.basename(fb_fp)} ({fb_sz:,} bytes)", flush=True)

    dfs = []
    global_memo = {}
    hit_totals = [0, 0, 0, 0, 0, 0, 0]

    for (sido, ptype, dtype), (seq, fp, sz, is_fb) in sorted(selected.items()):
        t_f = time.time()
        sub_df, info = parse_single_csv(fp, ptype, dtype, geocoder_pack, global_memo)
        if sub_df is None:
            print(f"  [SKIP] {os.path.basename(fp)} -> {info}", flush=True)
        else:
            dfs.append(sub_df)
            for idx_h in range(7):
                hit_totals[idx_h] += info[idx_h]
            print(f"  [OK] {os.path.basename(fp)} ({'FB' if is_fb else 'NEW'}): {len(sub_df):,} rows ({time.time()-t_f:.1f}s)", flush=True)

    if not dfs:
        raise RuntimeError("No valid MOLIT CSV files were parsed!")

    all_df = pd.concat(dfs, ignore_index=True)
    print(
        f"\nTotal geocoded transactions: {len(all_df):,} "
        f"(lot={hit_totals[1]:,}, road_exact={hit_totals[2]:,}, bldg={hit_totals[3]:,}, "
        f"street={hit_totals[4]:,}, dong={hit_totals[5]:,}, sgg={hit_totals[6]:,}, missed={hit_totals[0]:,})",
        flush=True
    )

    records = aggregate_grids_vectorized(all_df)

    # Atomic swap in map_data.db (preserves all other tables!)
    t_db = time.time()
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.execute("PRAGMA busy_timeout = 60000;")
    cur = conn.cursor()
    cur.execute("BEGIN IMMEDIATE;")
    try:
        cur.execute("DROP TABLE IF EXISTS realprice_grids;")
        cur.execute("""
            CREATE TABLE realprice_grids (
                lat_idx INTEGER,
                lng_idx INTEGER,
                property_type TEXT,
                lat REAL,
                lng REAL,
                avg_price_per_pyeong REAL,
                avg_deposit_per_pyeong REAL,
                avg_rent REAL,
                jeonse_ratio REAL,
                transaction_count INTEGER,
                sale_count INTEGER,
                rent_count INTEGER,
                age_premium_ratio REAL,
                floor_sensitivity REAL,
                sales_count_under_10 INTEGER,
                sales_count_10_to_20 INTEGER,
                sales_count_20_to_30 INTEGER,
                sales_count_over_30 INTEGER,
                sale_price_change_rate REAL,
                rent_price_change_rate REAL,
                new_build_price REAL DEFAULT 0,
                old_build_price REAL DEFAULT 0,
                PRIMARY KEY (lat_idx, lng_idx, property_type)
            );
        """)
        cur.executemany("""
            INSERT INTO realprice_grids VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            );
        """, records)
        cur.execute("CREATE INDEX idx_realprice_grids_type_lat_lng ON realprice_grids(property_type, lat, lng);")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS realprice_addr_cache (
                address TEXT PRIMARY KEY,
                lat REAL,
                lng REAL
            );
        """)
        conn.commit()
    except Exception:
        conn.rollback()
        conn.close()
        raise

    print(f"DB swap & spatial index committed in {time.time() - t_db:.1f}s!", flush=True)
    print("\n=== Updated realprice_grids Summary ===", flush=True)
    for row in cur.execute("""
        SELECT property_type, COUNT(*), SUM(transaction_count), SUM(sale_count), SUM(rent_count),
               ROUND(AVG(CASE WHEN avg_price_per_pyeong > 0 THEN avg_price_per_pyeong END), 1),
               ROUND(AVG(CASE WHEN avg_deposit_per_pyeong > 0 THEN avg_deposit_per_pyeong END), 1),
               COUNT(sale_price_change_rate), COUNT(rent_price_change_rate)
        FROM realprice_grids
        GROUP BY property_type
        ORDER BY property_type
    """):
        print(f"  {row}", flush=True)
    conn.close()
    print(f"\nCompleted successfully in {time.time() - t_total:.1f}s!", flush=True)


if __name__ == '__main__':
    main()
