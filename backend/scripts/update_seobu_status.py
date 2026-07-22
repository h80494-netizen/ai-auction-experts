import sqlite3

DB_PATH = 'backend/data/map_data.db'

def update_status():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Update subways table
    cursor.execute("UPDATE subways SET status='개발예정' WHERE line='서부경전철'")
    
    # Update subway_lines table
    cursor.execute("UPDATE subway_lines SET status='개발예정' WHERE line='서부경전철'")
    
    conn.commit()
    conn.close()
    print("Status updated successfully for 서부경전철.")

if __name__ == '__main__':
    update_status()
