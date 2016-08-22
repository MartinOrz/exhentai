__author__ = 'v_mading'

from downloader.comicdownloader import connect_to_exhentai, gen_headers
import re
import urllib.request as request

# http://exhentai.org/g/928316/439db23022/
gallery = re.compile('http://exhentai.org/g/[a-z0-9]+/[a-z0-9]+/')


def find_galleries(_content):
    return gallery.findall(_content)


if __name__ == '__main__':
    memberId, passHash = connect_to_exhentai('mdlovewho', 'ma199141')
    url = 'http://exhentai.org'
    req = request.Request(url, headers=gen_headers(memberId, passHash))
    content = request.urlopen(req, timeout=60).read().decode('utf-8')

    length = 0
    for g in find_galleries(content):
        print(g)
        length += 1
    print(length)


