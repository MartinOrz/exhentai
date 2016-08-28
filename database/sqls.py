# coding=utf-8
__author__ = 'v_mading'

import sqlite3
import os
import zipfile
import pickle
from database.datas import Author

# CREATE TABLE tb_artist (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   name VARCHAR(100) UNIQUE,
#   refer VARCHAR(100),
#   text VARCHAR(255),
#   comic_count INTEGER,
#   ratting INTEGER DEFAULT 50);

# CREATE TABLE tb_artist (
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   name VARCHAR(100) UNIQUE,
#   refer VARCHAR(100),
#   text VARCHAR(255),
#   comic_count INTEGER,
#   ratting INTEGER DEFAULT 50);

create_tb_gallery = 'CREATE TABLE tb_gallery (' + \
                    '  id INTEGER PRIMARY KEY AUTOINCREMENT,' + \
                    '  path VARCHAR(100),' + \
                    '  save_path VARCHAR(500),' + \
                    '  name VARCHAR(255),' + \
                    '  name_n VARCHAR(255),' + \
                    '  name_j VARCHAR(255),' + \
                    '  type VARCHAR(20),' + \
                    '  language VARCHAR(50),' + \
                    '  parody VARCHAR(100),' + \
                    '  is_anthology INTEGER,' + \
                    '  translator VARCHAR(100),' + \
                    '  rating INTEGER,' + \
                    '  length INTEGER,' + \
                    '  posted DATETIME,' + \
                    '  anthology VARCHAR(100));'

create_tb_gatoart = 'CREATE TABLE tb_gatoart (' + \
                    '  id INTEGER PRIMARY KEY AUTOINCREMENT,' + \
                    '  comic_path VARCHAR(100),' + \
                    '  comic_name VARCHAR(255),' + \
                    '  comic_id INTEGER,' + \
                    '  author_name VARCHAR(100),' + \
                    '  author_id INTEGER);'


# 基础的sql执行方法===================================================================

def get_sql_with_bracket(data):
    """
    将一个列表中的数据处理为在括号中的列表
    :param data: 需要处理的列表数据
    :return: 处理结果
    """
    result = '('
    for i in range(len(data) - 1):
        result += "'" + str(data[i]) + "', "
    result += "'" + str(data[-1]) + "')"
    return result


def create_table(db, table_create):
    """
    创建一个表
    :param db: 需要操作的数据位置
    :param table_create: 建表语句
    :return: 是否成功
    """
    try:
        cu = sqlite3.connect(db)
        cx = cu.cursor()
        cx.execute(table_create)
        return True
    except Exception as e:
        print('err occurs during create table: ' + str(e))
        return False
    finally:
        if cu:
            cu.close()


def select(db, table, columns=None, condition=None, order_by=None, desc=False, limit=None):
    """
    执行一条select语句
    :param db: 需要操作的数据
    :param table: 需要操作的表名
    :param columns: 需要选取的列
    :param condition: 选取条件
    :param order_by: 排序条件
    :param desc: 是否逆序，只有指定了order_by时才会生效
    :param limit: limit条件
    :return: 查询结果
    """
    sql = 'SELECT '
    if columns:
        sql += get_sql_with_bracket(columns) + ' '
    sql += ' FROM ' + table
    if condition:
        sql += ' WHERE ' + condition
    if order_by:
        sql += ' ORDER BY ' + order_by
    if order_by and desc:
        sql += ' DESC'
    if limit:
        sql += 'LIMIT ' + limit
    try:
        cu = sqlite3.connect(db)
        cx = cu.cursor()
        cx.execute(sql)
        return cx.fetchall()
    except Exception as e:
        print('err occurs during insert values: ' + str(e))
        return None
    finally:
        if cu:
            cu.close()


def insert(db, table, datas, columns=None):
    """
    向数据库中插入新的数据
    :param db: 需要操作的数据库
    :param table: 需要操作的表名
    :param datas: 需要插入的数据，二维列表格式
    :param columns: 要插入的列名，为None时是插入所有列
    :return: 是否成功
    """
    sql = 'INSERT OR IGNORE INTO ' + table
    if columns:
        sql += ' ' + get_sql_with_bracket(columns)
    sql += ' VALUES '
    for data in datas:
        sql += get_sql_with_bracket(data) + ', '
    sql = sql[:-2] + ';'
    try:
        cu = sqlite3.connect(db)
        cx = cu.cursor()
        cx.execute(sql)
        cu.commit()
        return True
    except Exception as e:
        print('err occurs during insert values: ' + str(e))
        print('sql: ' + sql)
        return False
    finally:
        if cu:
            cu.close()


def do_sql_without_return(db, sql):
    """
    执行一条没有返回值的sql语句
    :param db: 需要插入的db
    :param sql: 需要执行的sql
    :return: 是否成功
    """
    try:
        cu = sqlite3.connect(db)
        cx = cu.cursor()
        cx.execute(sql)
        cu.commit()
        print('SQL DONE')
        return True
    except Exception as e:
        print('err occurs during insert values: ' + str(e))
        return False
    finally:
        if cu:
            cu.close()


# 具体的sql执行方法===================================================================

def insert_authors(db, authors):
    """
    插入作者的数据列表
    :param db: 需要插入的数据库
    :param authors: 插入的数据列表
    :return: None
    """
    inserts = []
    columns = ('name', 'text', 'comic_count', 'ratting')
    for author in authors:
        inserts.append(("'" + author.name + "'", "'" + author.text + "'",
                        author.comicCount, author.ratting))
        if len(inserts) >= 100:
            insert(db, 'tb_artist', inserts, columns)
            inserts = []
    if len(inserts) > 0:
        insert(db, 'tb_artist', inserts, columns)


# 具体的操作内容======================================================================

def scan_authors(root_path, db):
    """
    扫描根目录，插入作者信息
    :param root_path: 需要扫描的根目录
    :param db: 需要插入的数据库
    :return: None
    """
    author_dict = dict()
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.zip'):
                zfile = zipfile.ZipFile(os.path.join(root, file), 'r')
                content = zfile.read(zfile.namelist()[-1])
                dic = pickle.loads(content)
                for artist in dic['artist']:
                    author = Author()
                    author.name = artist
                    author.comicCount = 1
                    if artist not in author_dict:
                        author_dict[artist] = author
                    else:
                        author_dict[artist].comicCount += 1

    authors = []
    for author_name in author_dict:
        authors.append(author_dict[author_name])
    print('scan authors done:', len(authors))

    insert_authors(db, authors)


def update_author_name(author_file, db):
    """
    更新作者的名称信息
    :param author_file: 作者名称信息文件
    :param db: 需要插入的数据库
    :return: None
    """
    with open(author_file, encoding='utf-8') as file:
        lines = file.readlines()
    sql = 'UPDATE tb_artist SET text = (CASE name '
    where = 'WHERE name IN ('

    updates = sql
    wherecl = where
    count = 0
    for line in lines:
        data = line[:-1].split('\t')
        if len(data) > 1 and data[1]:
            updates += "WHEN '" + data[0] + "' THEN '" + data[1].replace("'", "''") + "' "
            wherecl += "'" + data[0] + "', "
        count += 1
        if count == 50:
            updates += "END) "
            updates += wherecl[:-2] + ');'
            wherecl = where
            do_sql_without_return(db, updates)
            updates = sql
            count = 0

    if count > 0:
        updates += "END) "
        updates += wherecl[:-2] + ');'
        do_sql_without_return(db, updates)


if __name__ == '__main__':
    with open(r'E:\comic\manga\artist', encoding='utf-8') as file:
        lines = file.readlines()

    columns = ['name']
    inserts = []
    for line in lines:
        artist = line.split(' ')[0]
        inserts.append(["'" + artist + "'"])
        if len(inserts) >= 50:
            insert(r'E:\comic\exhentai.db', 'tb_artist', inserts, columns)
            inserts = []
    if len(inserts) > 0:
        insert(r'E:\comic\exhentai.db', 'tb_artist', inserts, columns)