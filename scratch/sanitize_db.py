import sqlite3
import os

db_path = os.path.join('backend', 'data', 'map_data.db')

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='detected_issues'")
    if cursor.fetchone():
        # Update title
        cursor.execute("""
            UPDATE detected_issues
            SET title = REPLACE(title, 'h80494', 'admin_user')
        """)
        cursor.execute("""
            UPDATE detected_issues
            SET title = REPLACE(title, 'spring11!!', '********')
        """)
        
        # Update description
        cursor.execute("""
            UPDATE detected_issues
            SET description = REPLACE(description, 'h80494', 'admin_user')
        """)
        cursor.execute("""
            UPDATE detected_issues
            SET description = REPLACE(description, 'spring11!!', '********')
        """)
        
        conn.commit()
        print("Updated map_data.db successfully.")
    else:
        print("Table 'detected_issues' not found in db.")
    conn.close()
