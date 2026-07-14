import pandas as pd
try:
    df = pd.read_excel('seoul_projects.xls', engine='xlrd')
    print("Read with xlrd:")
    print(df.head())
except Exception as e:
    print("xlrd error:", e)
    try:
        df = pd.read_html('seoul_projects.xls')[0]
        print("Read with read_html:")
        print(df.head())
    except Exception as e2:
        print("read_html error:", e2)
