__author__ = 'v_mading'

import database.sqls as sql

# CREATE TABLE tb_cosplayjav (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   name VARCHAR(1024) UNIQUE,
#   url VARCHAR(1024),
#   status INTEGER );

if __name__ == '__main__':
    with open(r'E:\cosplayjav.txt', encoding='utf-8') as file:
        lines = file.readlines()

    names = []
    for line in lines:
        if (not line.startswith('https')) and len(line.strip()) > 0:
            names.append(line)

    columns = ['name']
    inserts = []
    for name in names:
        inserts.append(["'" + name + "'"])
        if len(inserts) >= 50:
            sql.insert(r'E:\cosplayjav.db', 'tb_cosplayjav', inserts, columns)
            inserts = []
    if len(inserts) > 0:
        sql.insert(r'E:\cosplayjav.db', 'tb_cosplayjav', inserts, columns)