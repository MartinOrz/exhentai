# coding=utf-8
__author__ = 'v_mading'

import database.sqls as sql
import re
import urllib.request as request
import urllib.parse as parse
import os
import database.sqls as sql

# CREATE TABLE tb_cosplay (
#     id INTEGER PRIMARY KEY,
#     name VARCHAR(1024),
#     url VARCHAR(1024),
#     img VARCHAR(1024),
#     status INTEGER
# );

# CREATE TABLE tb_mega (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     code INTEGER,
#     url VARCHAR(1024)
# );

# 主页面上的一篇文章地址
article = re.compile('<a href="(http://cosplayjav.pl/\d+/.+?/)">')

# 文章的标题
cos_title = re.compile('<h1 class="post-title">(.+?)</h1>')

# 缩略图地址
cos_img = re.compile('<img width="\d+" height="\d+" src="(.+?)"')

# 文章中的下载地址
cos_download = re.compile('<a class="btn btn-primary" href="(http://cosplayjav.pl/[^"]+)" target="_blank">')

# 由下载地址得到的MEGA URL
mega_url = re.compile('<a href="(https://mega.nz/[^"]+)" class="btn btn-primary btn-download">Download</a>')


# re的find方法----------------------------------------------------------------------------------------------------------
def find_cos_download(_content):
    return cos_download.findall(_content)


def find_mega_url(_content):
    return mega_url.findall(_content)[0]


def find_cos_title(_content):
    return cos_title.findall(_content)[0]


def find_cos_img(_content):
    return cos_img.findall(_content)[0]


# 一些工具方法-----------------------------------------------------------------------------------------------------------
def gen_headers(referer=''):
    """
    生成一个随机的请求头部

    :param referer: 请求头部的referer信息
    :return: 生成的请求头
    """
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 ' + \
                 'Safari/537.36'
    headers = {'User-Agent': user_agent, 'Accept-Language': 'zh-CN,zh;q=0.8', 'Accept-Charset': 'utf-8;q=0.7,*;q=0.7',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Connection': 'keep-alive'}
    return headers


def save_img(src, name, dst):
    """
    将图片保存

    :param src: 图片地址
    :param name 图片名称
    :param dst 保存目录
    :return: 图片保存地址
    """
    # parse.quute会将':'也进行编码，因此需要手动处理引号
    tmp = src.split(':')
    src = tmp[0] + ':' + parse.quote(tmp[1])
    src = src.replace('&amp;', '&')
    suffix = src.split(".")[-1]
    req = request.Request(src, headers=gen_headers(src))
    file_name = os.path.join(dst, name + '.' + suffix)
    if os.path.exists(file_name): # 已经下载过的图片
        return file_name
    response = request.urlopen(req, timeout=120)
    with open(file_name, 'wb') as _file:
        _content = response.read()
        _file.write(_content)
    return file_name


class CosplayJav:
    """
    对应网站上一篇文章的实体类
    """

    def __init__(self):
        self.url = ''    # 文章地址
        self.code = ''   # 编号
        self.title = ''  # 标题
        self.img = ''    # 缩略图地址
        self.megas = []  # mega下载地址

    def create(self, url):
        self.url = url
        req = request.Request(self.url, headers=gen_headers())
        content = request.urlopen(req, timeout=300).read().decode('utf-8', 'ignore')
        self.title = find_cos_title(content)
        print('Find Title: ' + self.title)
        self.code = self.url.split('/')[3]
        self.img = find_cos_img(content)
        downloads = find_cos_download(content)
        for d in downloads:
            if 'type' not in d: # 有时会有type=torrent等，这些非mega链接
                req = request.Request(d, headers=gen_headers())
                content = request.urlopen(req, timeout=300).read().decode('utf-8', 'ignore')
                mega = find_mega_url(content)
                print('Find Mega: ' + mega)
                self.megas.append(mega)


def get_all_javs_from_page(page_num, dst):
    """
    主方法，在一个页面中找到所有文章，并解析这些文章
    :param page_num: 当前的页面页码
    :param dst: 解析结果及图片保存路径
    :return: 失败列表
    """

    page = 'http://cosplayjav.pl/page/' + str(page_num) + '/'
    req = request.Request(page, headers=gen_headers())
    content = request.urlopen(req, timeout=300).read().decode('utf-8', 'ignore')
    urls = set(article.findall(content))

    fails = []
    success = []
    for url in urls:
        try:
            cos = CosplayJav()
            cos.create(url)
            save_img(cos.img, cos.code, dst)
            success.append(cos)
        except Exception as e:
            print(e)
            fails.append(url)
            print('Fail!')
        print('==========================================')
    with open(os.path.join(dst, str(page_num)), 'w', encoding='utf-8') as file:
        for cos in success:
            file.write(str(cos.code) + '\t' + cos.url + '\n')
            file.write(cos.title + '\n')
            file.write('img: ' + cos.img + '\n')
            file.write('---------------------------------------------------------------\n')
            for mega in cos.megas:
                file.write(mega + '\n')
            file.write('\n')
    return fails


def read_file(path):
    with open(path, encoding='utf-8') as file:
        lines = file.readlines()

    status = ('url', 'title', 'img', '--', 'mega', 'blank')
    now = 0

    result = []
    for line in lines:
        if '\n' in line:
            line = line[:-1]
        if status[now % len(status)] == 'url':
            cos = CosplayJav()
            result.append(cos)
            cos.code, cos.url = line.split('\t')
            now += 1
        elif status[now % len(status)] == 'title':
            cos.title = line
            now += 1
        elif status[now % len(status)] == 'img':
            cos.img =line
            now += 1
        elif status[now % len(status)] == '--':
            now += 1
        elif status[now % len(status)] == 'mega':
            if line.startswith('https'):
                cos.megas.append(line)
            else: # 此时已经是blank
                now = 5
                now += 1
    return result


def insert_cos(cos_list):
    datas = [(cos.code, cos.title, cos.url, cos.img, 0) for cos in cos_list]
    columns = ('id', 'name', 'url', 'img', 'status')
    sql.insert(r'g:\cosplayjav.db', 'tb_cosplay', datas, columns)

if __name__ == '__main__':
    i = 1
    while i < 239:
        path = os.path.join(r'g:\doo', str(i))
        # with open(path, encoding='utf-8') as file:
        #     for line in file:
        #         if '881' in line:
        #             print(i)
        #             break
        r = read_file(path)
        insert_cos(r)
        i += 1
    # with open(r'E:\cosplayjav.txt', encoding='utf-8') as file:
    #     lines = file.readlines()
    #
    # names = []
    # for line in lines:
    #     if (not line.startswith('https')) and len(line.strip()) > 0:
    #         names.append(line)
    #
    # columns = ['name']
    # inserts = []
    # for name in names:
    #     inserts.append(["'" + name + "'"])
    #     if len(inserts) >= 50:
    #         sql.insert(r'E:\cosplayjav.db', 'tb_cosplayjav', inserts, columns)
    #         inserts = []
    # if len(inserts) > 0:
    #     sql.insert(r'E:\cosplayjav.db', 'tb_cosplayjav', inserts, columns)