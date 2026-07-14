import sqlite3

def main():
    db_path = 'backend/data/map_data.db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Update Naebang station coordinates
    # We found id=381 is the one. Let's make sure it updates the correct record.
    cur.execute('''
        UPDATE subways
        SET address = '서울 서초구 방배동 875-15',
            lat = 37.487618,
            lng = 126.993547
        WHERE id = 381
    ''')
    
    conn.commit()
    print("Naebang station coordinates updated in DB successfully!")
    
    # 2. Print updated row to verify
    cur.execute("SELECT id, line, name, address, lat, lng FROM subways WHERE id = 381")
    print("Updated Naebang station row:")
    print(cur.fetchone())
    
    conn.close()

if __name__ == '__main__':
    main()
