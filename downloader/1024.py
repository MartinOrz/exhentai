# coding=utf-8
__author__ = 'v_mading'

import re
import urllib.request as request

# url_pattern
# <h3><a href="htm_data/22/1604/336906.html" id="a_ajax_336906">[04.17] GAS-307 爆乳とホテルにしけ込んでモミモミ 撮りおろしハメ撮りSPECIAL Torrent-1.32 G</a></h3>
url_pattern = re.compile('<h3><a href="([^"]+)" id="a_ajax_\d+">([^<]+)</a></h3>')

root_url = 'http://1024.hegongchang.shiksha/pw/thread.php?fid=5&page='


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

if __name__ == '__main__':
    result = []
    for i in range(149):
        if i > 0:
            for k in range(5):
                try:
                    req = request.Request(root_url + str(i), headers=gen_headers())
                    content = request.urlopen(req, timeout=300).read().decode('utf-8', 'ignore')
                    tmp = find_url('大泽
                        result.append(t)
                    print('page ' + str(i) + ' done.')
                    break', content)
                    for t in tmp:
                except:
                    print('page ' + str(i) + ' wrong.')
    with open(r'd:\upba', 'w', encoding='utf-8') as file:
        for r in result:
            file.write(r[0] + '\t' + r[1] + '\n')
