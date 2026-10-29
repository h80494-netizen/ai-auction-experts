-- ============================================================================
-- AI Auction Expert 2.0 - Integrated SQLite Database Schema (schema.sql)
-- Runtime DB Paths:
--   1. backend/data/map_data.db       (경공매, 실거래가, 공시지가, 네이버시세, 공간레이어)
--   2. backend/data/small_business.db (소상공인 상권 정보 데이터베이스)
-- ============================================================================

-- ############################################################################
-- DATABASE: map_data.db (651.8 MB)
-- ############################################################################

-- Table: admin_notices (Rows: 3)
CREATE TABLE admin_notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            notice_type TEXT DEFAULT 'warning',
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT
        );

-- Table: approved_users (Rows: 10)
CREATE TABLE approved_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            contact TEXT,
            pin_hash TEXT NOT NULL,
            inquiry_id INTEGER,
            status TEXT DEFAULT 'active',
            approved_at TEXT NOT NULL
        );

-- Table: auctions (Rows: 31,210)
CREATE TABLE auctions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            case_no TEXT,
            sale_type TEXT,
            property_type TEXT,
            address TEXT,
            appraisal_price REAL,
            min_price REAL,
            min_bid_rate REAL,
            lat REAL,
            lng REAL,
            area_size REAL,
            subway_dist REAL,
            univ_dist REAL,
            ind_dist REAL,
            elite_school TEXT,
            households INTEGER,
            land_size REAL,
            min_price_per_pyeong REAL,
            special_notes TEXT,
            official_land_price REAL,
            sale_date TEXT
        );

-- Table: board_comments (Rows: 11)
CREATE TABLE board_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    inquiry_id INTEGER NOT NULL,
                    author TEXT NOT NULL,
                    content TEXT NOT NULL,
                    is_admin INTEGER DEFAULT 0,
                    is_secret INTEGER DEFAULT 1,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (inquiry_id) REFERENCES board_inquiries(id) ON DELETE CASCADE
                );

-- Table: board_inquiries (Rows: 15)
CREATE TABLE board_inquiries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT NOT NULL,
            pin_hash TEXT NOT NULL,
            is_secret INTEGER DEFAULT 1,
            contact TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL
        , is_approved INTEGER DEFAULT 0, approved_at TEXT);

-- Table: board_posts (Rows: 12)
CREATE TABLE board_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        author TEXT NOT NULL,
        password TEXT NOT NULL,
        is_approved INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        category TEXT DEFAULT 'question',
        status TEXT DEFAULT 'pending'
    );

-- Table: bus_stops (Rows: 64,347)
CREATE TABLE bus_stops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                city TEXT,
                lat REAL,
                lng REAL,
                address TEXT
            );

-- Table: commercial_areas (Rows: 1,650)
CREATE TABLE commercial_areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            name TEXT,
            lat REAL,
            lng REAL,
            population INTEGER
        );

-- Table: config (Rows: 1)
CREATE TABLE config (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );

-- Table: crosswalk_segments (Rows: 11,562)
CREATE TABLE crosswalk_segments (
            link_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            min_lat REAL,
            max_lat REAL,
            min_lng REAL,
            max_lng REAL,
            coords_json TEXT
        );

-- Table: deregulation_zones (Rows: 828)
CREATE TABLE deregulation_zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            details TEXT,
            min_lat REAL,
            max_lat REAL,
            min_lng REAL,
            max_lng REAL,
            geojson TEXT
        );

-- Table: detected_issues (Rows: 159)
CREATE TABLE detected_issues (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            source TEXT,
            scanned_date TEXT,
            keywords TEXT,
            status_label TEXT,
            description TEXT,
            url TEXT,
            region TEXT,
            category TEXT,
            importance_stars INTEGER,
            latitude REAL,
            longitude REAL
        );

-- Table: district_units (Rows: 11,261)
CREATE TABLE district_units (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                min_lat REAL,
                max_lat REAL,
                min_lng REAL,
                max_lng REAL,
                geojson TEXT
            );

-- Table: email_verifications (Rows: 0)
CREATE TABLE email_verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            code TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );

-- Table: gyeonggi_dong_population (Rows: 271)
CREATE TABLE gyeonggi_dong_population (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sgg TEXT,
                dong TEXT,
                lat REAL,
                lng REAL,
                population REAL
            );

-- Table: hagwon_polygons (Rows: 387)
CREATE TABLE hagwon_polygons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            count INTEGER,
            coordinates_json TEXT
        );

-- Table: industrial_complexes (Rows: 17,438)
CREATE TABLE industrial_complexes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            lat REAL,
            lng REAL
        );

-- Table: industrial_polygons (Rows: 1,909)
CREATE TABLE industrial_polygons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        polygon_geojson TEXT,
        buffer_geojson TEXT,
        min_lat REAL,
        max_lat REAL,
        min_lng REAL,
        max_lng REAL
    );

-- Table: lodging_polygons (Rows: 1,000)
CREATE TABLE lodging_polygons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            count INTEGER,
            coordinates_json TEXT
        );

-- Table: middle_schools (Rows: 1,201)
CREATE TABLE middle_schools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            lat REAL,
            lng REAL,
            special_hs_rate REAL
        );

-- Table: naver_real_estate (Rows: 817,016)
CREATE TABLE naver_real_estate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estate_id TEXT UNIQUE,
            address TEXT,
            price TEXT,
            rent TEXT,
            floor TEXT,
            area TEXT,
            deal_type TEXT,
            type_detail TEXT,
            lat REAL,
            lng REAL,
            estate_type TEXT,
            region TEXT,
            age_info TEXT
        );

-- Table: planning_roads (Rows: 5,191)
CREATE TABLE planning_roads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            present_sn TEXT UNIQUE,
            name TEXT,
            road_class TEXT,
            min_lat REAL,
            max_lat REAL,
            min_lng REAL,
            max_lng REAL,
            geojson TEXT
        );

-- Table: population_500m_grids (Rows: 69,863)
CREATE TABLE population_500m_grids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    grid_code TEXT UNIQUE,
    lat REAL,
    lng REAL,
    residential_pop REAL,
    worker_pop REAL
);

-- Table: population_grids (Rows: 8,571)
CREATE TABLE population_grids (
    grid_id TEXT PRIMARY KEY,
    lat REAL,
    lng REAL,
    avg_population REAL
);

-- Table: realprice_addr_cache (Rows: 2,126)
CREATE TABLE realprice_addr_cache (
            address TEXT PRIMARY KEY,
            lat REAL,
            lng REAL
        );

-- Table: realprice_grids (Rows: 77,961)
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
            sales_count_over_30 INTEGER, sale_price_change_rate REAL, rent_price_change_rate REAL, new_build_price REAL DEFAULT 0, old_build_price REAL DEFAULT 0,
            PRIMARY KEY (lat_idx, lng_idx, property_type)
        );

-- Table: redevelopment_zones (Rows: 3,078)
CREATE TABLE redevelopment_zones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                propel_cd TEXT,
                min_lat REAL,
                max_lat REAL,
                min_lng REAL,
                max_lng REAL,
                geojson TEXT
            );

-- Table: road_cache_grids (Rows: 1,485)
CREATE TABLE road_cache_grids (
        lat_idx INTEGER,
        lng_idx INTEGER,
        PRIMARY KEY (lat_idx, lng_idx)
    );

-- Table: road_cache_segments (Rows: 379,067)
CREATE TABLE road_cache_segments (
        osm_id INTEGER PRIMARY KEY,
        name TEXT,
        highway TEXT,
        width REAL,
        min_lat REAL,
        max_lat REAL,
        min_lng REAL,
        max_lng REAL,
        coords_json TEXT
    );

-- Table: road_segments (Rows: 271,118)
CREATE TABLE road_segments (
            link_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            min_lat REAL,
            max_lat REAL,
            min_lng REAL,
            max_lng REAL,
            coords_json TEXT
        );

-- Table: subway_lines (Rows: 64)
CREATE TABLE subway_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            line TEXT,
            status TEXT,
            coordinates_json TEXT
        );

-- Table: subways (Rows: 1,349)
CREATE TABLE subways (id INTEGER PRIMARY KEY, line TEXT, name TEXT, address TEXT, lat REAL, lng REAL, status TEXT);

-- Table: tourist_density (Rows: 852)
CREATE TABLE tourist_density (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            area_nm TEXT,
            signgu_nm TEXT,
            name TEXT,
            rate REAL,
            lat REAL,
            lng REAL
        );

-- Table: unexecuted_facilities (Rows: 20,674)
CREATE TABLE unexecuted_facilities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            min_lat REAL,
            max_lat REAL,
            min_lng REAL,
            max_lng REAL,
            geojson TEXT,
            gosi_year INTEGER
        );

-- Table: universities (Rows: 975)
CREATE TABLE universities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            address TEXT,
            lat REAL,
            lng REAL
        );

-- Table: zoning_polygons (Rows: 42,993)
CREATE TABLE zoning_polygons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                propel_cd TEXT,
                min_lat REAL,
                max_lat REAL,
                min_lng REAL,
                max_lng REAL,
                geojson TEXT
            );

CREATE INDEX idx_auctions_case_no ON auctions(case_no);

CREATE INDEX idx_auctions_lat_lng ON auctions(lat, lng);

CREATE INDEX idx_auctions_min_rate ON auctions(min_bid_rate);

CREATE INDEX idx_auctions_sale_type ON auctions(sale_type);

CREATE INDEX idx_bus_lat_lng ON bus_stops(lat, lng);

CREATE INDEX idx_bus_stops_lat_lng ON bus_stops(lat, lng);

CREATE INDEX idx_commercial_areas_lat_lng ON commercial_areas(lat, lng);

CREATE INDEX idx_crosswalk_bounds ON crosswalk_segments(max_lat, min_lat, max_lng, min_lng);

CREATE INDEX idx_deregulation_zones_lat ON deregulation_zones (min_lat, max_lat);

CREATE INDEX idx_deregulation_zones_lng ON deregulation_zones (min_lng, max_lng);

CREATE INDEX idx_district_units_bounds ON district_units(max_lat, min_lat, max_lng, min_lng);

CREATE INDEX idx_du_max_lat ON district_units(max_lat);

CREATE INDEX idx_du_max_lng ON district_units(max_lng);

CREATE INDEX idx_du_min_lat ON district_units(min_lat);

CREATE INDEX idx_du_min_lng ON district_units(min_lng);

CREATE INDEX idx_ind_poly_bounds ON industrial_polygons(min_lat, max_lat, min_lng, max_lng);

CREATE INDEX idx_industrial_complexes_lat_lng ON industrial_complexes(lat, lng);

CREATE INDEX idx_mid_lat_lng ON middle_schools(lat, lng);

CREATE INDEX idx_middle_schools_lat_lng ON middle_schools(lat, lng);

CREATE INDEX idx_naver_coords ON naver_real_estate(lat, lng);

CREATE INDEX idx_naver_deal_type ON naver_real_estate(deal_type);

CREATE INDEX idx_naver_estate_id ON naver_real_estate(estate_id);

CREATE INDEX idx_naver_region_type ON naver_real_estate(region, estate_type);

CREATE INDEX idx_naver_region_type_coords ON naver_real_estate(region, estate_type, lat, lng);

CREATE INDEX idx_naver_type_coords ON naver_real_estate(estate_type, lat, lng);

CREATE INDEX idx_planning_roads_bounds ON planning_roads(max_lat, min_lat, max_lng, min_lng);

CREATE INDEX idx_planning_roads_class ON planning_roads(road_class);

CREATE INDEX idx_planning_roads_max_lat ON planning_roads(max_lat);

CREATE INDEX idx_planning_roads_max_lng ON planning_roads(max_lng);

CREATE INDEX idx_planning_roads_min_lat ON planning_roads(min_lat);

CREATE INDEX idx_planning_roads_min_lng ON planning_roads(min_lng);

CREATE INDEX idx_pop_lat ON population_grids(lat);

CREATE INDEX idx_pop_lng ON population_grids(lng);

CREATE INDEX idx_population_500m_grids_lat_lng ON population_500m_grids(lat, lng);

CREATE INDEX idx_population_grids_lat_lng ON population_grids(lat, lng);

CREATE INDEX idx_redevelopment_zones_bounds ON redevelopment_zones(max_lat, min_lat, max_lng, min_lng);

CREATE INDEX idx_redevelopment_zones_max_lat ON redevelopment_zones(max_lat);

CREATE INDEX idx_redevelopment_zones_max_lng ON redevelopment_zones(max_lng);

CREATE INDEX idx_redevelopment_zones_min_lat ON redevelopment_zones(min_lat);

CREATE INDEX idx_redevelopment_zones_min_lng ON redevelopment_zones(min_lng);

CREATE INDEX idx_road_bounds ON road_segments(max_lat, min_lat, max_lng, min_lng);

CREATE INDEX idx_road_cache_bounds ON road_cache_segments(max_lat, min_lat, max_lng, min_lng);

CREATE INDEX idx_road_segments_composite ON road_cache_segments(min_lat, max_lat, min_lng, max_lng);

CREATE INDEX idx_subways_lat_lng ON subways(lat, lng);

CREATE INDEX idx_uf_max_lat ON unexecuted_facilities(max_lat);

CREATE INDEX idx_uf_max_lng ON unexecuted_facilities(max_lng);

CREATE INDEX idx_uf_min_lat ON unexecuted_facilities(min_lat);

CREATE INDEX idx_uf_min_lng ON unexecuted_facilities(min_lng);

CREATE INDEX idx_universities_lat_lng ON universities(lat, lng);

CREATE INDEX idx_zoning_polygons_bounds ON zoning_polygons(max_lat, min_lat, max_lng, min_lng);

CREATE INDEX idx_zoning_polygons_max_lat ON zoning_polygons(max_lat);

CREATE INDEX idx_zoning_polygons_max_lng ON zoning_polygons(max_lng);

CREATE INDEX idx_zoning_polygons_min_lat ON zoning_polygons(min_lat);

CREATE INDEX idx_zoning_polygons_min_lng ON zoning_polygons(min_lng);

-- ############################################################################
-- DATABASE: small_business.db (979.5 MB)
-- ############################################################################

-- Table: small_business (Rows: 2,691,377)
CREATE TABLE small_business (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bizes_id TEXT,
            name TEXT,
            branch TEXT,
            cat_large_code TEXT,
            cat_large_name TEXT,
            cat_medium_code TEXT,
            cat_medium_name TEXT,
            cat_small_code TEXT,
            cat_small_name TEXT,
            inds_code TEXT,
            inds_name TEXT,
            sido_code TEXT,
            sido_name TEXT,
            sigungu_code TEXT,
            sigungu_name TEXT,
            dong_code TEXT,
            dong_name TEXT,
            road_addr TEXT,
            lot_addr TEXT,
            building_name TEXT,
            floor_info TEXT,
            ho_info TEXT,
            lng REAL,
            lat REAL
        );

CREATE INDEX idx_sb_cat_large ON small_business(cat_large_name);

CREATE INDEX idx_sb_lat_lng ON small_business(lat, lng);
