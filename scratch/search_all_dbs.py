import os
import sqlite3

def search_db(db_path, query_val):
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            # Get columns
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                cols = [row['name'] for row in cursor.fetchall()]
                
                # Build search query for any column
                where_clauses = []
                params = []
                for col in cols:
                    where_clauses.append(f"CAST({col} AS TEXT) LIKE ?")
                    params.append(f"%{query_val}%")
                
                if where_clauses:
                    sql = f"SELECT * FROM {table} WHERE " + " OR ".join(where_clauses) + " LIMIT 5"
                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
                    if rows:
                        print(f"\n[MATCH] DB: {db_path} | Table: {table} | Found {len(rows)} matching rows:")
                        for row in rows:
                            print("  ", dict(row))
            except Exception as e:
                # print(f"Error querying table {table} in {db_path}: {e}")
                pass
                
        conn.close()
    except Exception as e:
        # print(f"Error connecting to DB {db_path}: {e}")
        pass

def main():
    workspace_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩"
    print("Scanning workspace for SQLite databases...")
    for root, dirs, files in os.walk(workspace_dir):
        for file in files:
            if file.endswith(".db"):
                db_path = os.path.join(root, file)
                search_db(db_path, "6060")

if __name__ == "__main__":
    main()
