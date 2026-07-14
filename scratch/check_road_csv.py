import pandas as pd
try:
    df = pd.read_csv('data/road.csv', encoding='cp949', nrows=5)
    print("Columns in road.csv:", df.columns.tolist())
except Exception as e:
    print("Error reading csv:", e)

# Count lines
count = 0
try:
    with open('data/road.csv', 'r', encoding='cp949') as f:
        for line in f:
            count += 1
    print("Total lines in road.csv:", count)
except Exception as e:
    print("Error counting lines:", e)
