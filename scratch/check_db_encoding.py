import sqlite3

db_path = 'backend/data/map_data.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Get raw bytes of address from a few Gyeonggi/Incheon rows
c.execute('SELECT case_no, address, CAST(address AS BLOB) FROM auctions LIMIT 15')
for case_no, addr_str, addr_bytes in c.fetchall():
    print(f"Case: {case_no}")
    print(f"  As string: {addr_str}")
    print(f"  As hex: {addr_bytes.hex() if addr_bytes else 'None'}")
    
    # Let's try decoding from CP949 or UTF-8 if they were read incorrectly
    if addr_bytes:
        try:
            print(f"  Decoded from cp949: {addr_bytes.decode('cp949', errors='replace')}")
        except Exception as e:
            print(f"  cp949 error: {e}")
        try:
            # Let's try decoding from utf-8
            print(f"  Decoded from utf-8: {addr_bytes.decode('utf-8', errors='replace')}")
        except Exception as e:
            print(f"  utf-8 error: {e}")
            
conn.close()
