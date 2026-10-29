import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

DB_LIST = [
    ("map_data.db", os.path.join(BASE_DIR, "backend", "data", "map_data.db")),
    ("small_business.db", os.path.join(BASE_DIR, "backend", "data", "small_business.db")),
]


def export_schema():
    out_lines = [
        "-- ============================================================================",
        "-- AI Auction Expert 2.0 - Integrated SQLite Database Schema (schema.sql)",
        "-- Runtime DB Paths:",
        "--   1. backend/data/map_data.db       (경공매, 실거래가, 공시지가, 네이버시세, 공간레이어)",
        "--   2. backend/data/small_business.db (소상공인 상권 정보 데이터베이스)",
        "-- ============================================================================\n",
    ]

    for db_label, db_path in DB_LIST:
        if not os.path.exists(db_path):
            continue
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        out_lines.append("-- ############################################################################")
        out_lines.append(f"-- DATABASE: {db_label} ({size_mb:.1f} MB)")
        out_lines.append("-- ############################################################################\n")

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(
            "SELECT type, name, sql FROM sqlite_master "
            "WHERE sql IS NOT NULL AND name NOT LIKE 'sqlite_%' "
            "ORDER BY CASE type WHEN 'table' THEN 1 WHEN 'index' THEN 2 ELSE 3 END, name"
        )
        rows = cur.fetchall()
        for obj_type, obj_name, sql in rows:
            if obj_type == "table":
                try:
                    c2 = conn.cursor()
                    c2.execute(f'SELECT COUNT(*) FROM "{obj_name}"')
                    cnt = c2.fetchone()[0]
                    out_lines.append(f"-- Table: {obj_name} (Rows: {cnt:,})")
                except Exception:
                    out_lines.append(f"-- Table: {obj_name}")
            out_lines.append(sql.strip() + ";\n")
        conn.close()

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines))
    print(f"Exported schema to {OUT_PATH}")


if __name__ == "__main__":
    export_schema()
