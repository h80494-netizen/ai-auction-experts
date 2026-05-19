import sqlite3, os
c = sqlite3.connect('data/map_data.db').cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='population_grids'")
res = c.fetchone()
if res:
    print('Rows:', c.execute('SELECT COUNT(*) FROM population_grids').fetchone()[0])
else:
    print('Table not found')
