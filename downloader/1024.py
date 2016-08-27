# coding=utf-8
__author__ = 'v_mading'

import re
import os
import urllib.request as request
import urllib.parse as parse

# url_pattern
# <h3><a href="htm_data/22/1604/336906.html" id="a_ajax_336906">[04.17] GAS-307 爆乳とホテルにしけ込んでモミモミ 撮りおろしハメ撮りSPECIAL Torrent-1.32 G</a></h3>
url_pattern = re.compile('<h3><a href="([^"]+)" id="a_ajax_\d+">([^<]+)</a></h3>')


root_url = 'http://1024.hegongchang.shiksha/pw/thread.php?fid=5&page='

class CosplayJav:

    def __init__(self):
        self.url = ''
        self.code = ''
        self.name = ''
        self.img = ''
        self.megas = []

    def create(self, url):
        self.url = url
        req = request.Request(self.url, headers=gen_headers())
        content = request.urlopen(req, timeout=300).read().decode('utf-8', 'ignore')
        self.name = findCosTitle(content)
        print('Find Title: ' + self.name)
        self.code = self.url.split('/')[3]
        self.img = findImg(content)
        downloads = findCosplayjavUrl(content)
        for d in downloads:
            if 'type' not in d:
                req = request.Request(d, headers=gen_headers())
                content = request.urlopen(req, timeout=300).read().decode('utf-8', 'ignore')
                mega = findMegaUrl(content)
                print('Find Mega: ' + mega)
                self.megas.append(mega)



def get_all_javs_from_page(pageNo, dst):
    req = request.Request(get_page(pageNo), headers=gen_headers())
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
    with open(os.path.join(dst, str(pageNo)), 'w', encoding='utf-8') as file:
        for cos in success:
            file.write(str(cos.code) + '\t' + cos.url + '\n')
            file.write(cos.name + '\n')
            file.write('img: ' + cos.img + '\n')
            file.write('---------------------------------------------------------------\n')
            for mega in cos.megas:
                file.write(mega + '\n')
            file.write('\n')
    return fails


def get_page(pageNo):
    return 'http://cosplayjav.pl/page/' + str(pageNo) + '/'


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


def find_url(name, _content):
    target = url_pattern.findall(_content)
    result = []
    for t in target:
        if name in t[1]:
            result.append(t)
    return result


def findCosplayjavUrl(_content):
    return cosdownload.findall(_content)


def findMegaUrl(_content):
    return megaurl.findall(_content)[0]


def findCosTitle(_content):
    return costitle.findall(_content)[0]


def findImg(_content):
    return cosimg.findall(_content)[0]


def getRest(url):
    return url.split('/')[3]


def save_img(src, name, dst):
    """
    将图片保存

    :param src: 图片地址
    :param name 图片名称
    :param dst 保存目录
    :return: 图片保存地址
    """
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


def readFile(path):
    with open(path, encoding='utf-8') as file:
        lines = file.readlines()
    result = {}
    now = []
    for line in lines:
        if not line.strip():
            if now:
                result[now[0]] = now
            now = []
        else:
            now.append(line)
    return result

def getFiles(do, dst):
    with open(do, encoding='utf-8') as file:
        lines = file.readlines()
    with open(dst, 'w', encoding='utf-8') as file:
        i = 0
        for line in lines:
            i += 1
            try:
                req = request.Request(line, headers=gen_headers())
                content = request.urlopen(req, timeout=300).read().decode('utf-8', 'ignore')
                title = findCosTitle(content)
                file.write(title + '\n')
                downloads = findCosplayjavUrl(content)
                for d in downloads:
                    req = request.Request(d, headers=gen_headers())
                    content = request.urlopen(req, timeout=300).read().decode('utf-8', 'ignore')
                    mega = findMegaUrl(content)
                    file.write(mega + '\n')
                file.write('\n')
                print(title)
            except:
                print(str(i) + ' fail!\n')

if __name__ == '__main__':
    i = 141
    while i < 239:
        fails = get_all_javs_from_page(i, r'D:\doo')
        with open(r'd:\doo\fail', 'a', encoding='utf-8') as file:
            for fail in fails:
                file.write(fail + '\n')
        i += 1

    # url = 'http://cosplayjav.pl/21799/imageset-kurumint-%E6%96%B0%E3%83%BBcos-309/'
    # cos = CosplayJav()
    # cos.create(url)
    # save_img(cos.img, cos.code, r'd:\doo')

    # src = 'http://cosplayjav.pl/wp-content/uploads/2016/08/IMAGESET-NTR%E5%B0%91%E5%A5%B3-Oreimo-Gokou-Ruri-Kuroneko-cosplay-UNCENSORED.jpg'
    # save_img(src, '1', r'd:\doo')
