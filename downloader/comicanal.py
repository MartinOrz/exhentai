# coding=utf-8
__author__ = 'mading01'

import downloader.comicdownloader as downloader
import urllib.request as request
import os
import pickle

''' 示例页面 '''
# http://exhentai.org/?page=1&f_doujinshi=on&f_manga=on&f_artistcg=on&f_gamecg=on&f_western=on&f_non-h=on&f_imageset=on&f_cosplay=on&f_asianporn=on&f_misc=on&f_search=scat&f_apply=Apply+Filter


class ComicSearcher:
    """
    爬虫，根据给定的关键字及搜索过滤器获取漫画，获取到的漫画将以Gallery的形式存储在文件中
    """

    ROOT = 'http://exhentai.org/'

    def __init__(self, save_path, member_id, pass_hash):
        self.savePath = save_path
        self.memberId = member_id
        self.passHash = pass_hash
        self.searchWord = ''
        self.filter = {'doujinshi': 0, 'manga': 0, 'artistcg': 0, 'gamecg': 0, 'western': 0, 'non-h': 0, 'imageset': 0,
            'cosplay': 0, 'asianporn': 0, 'misc': 0}
        self.maxFinding = 0
        self.resultList = []
        self.startPage = 0
        self.length = 0
        self.rating = 0

    def set_args(self, _search_word=None, _ratting=0, _filter=None, _max_finding=100, _start_page=0, _length=200,
                 _rating=3):
        if _search_word:
            self.searchWord = _search_word
        if _filter:
            for fil in _filter:
                if fil in self.filter:
                    self.filter[fil] = 1
        self.maxFinding = _max_finding
        self.startPage = _start_page
        self.length = _length
        self.rating = _rating

    def build_url(self, page):
        url = ComicSearcher.ROOT + '?page=' + str(page)
        for fil in self.filter:
            url += '&f_' + fil + '=' + str(self.filter[fil])
        url += '&f_search=' + self.searchWord + '&f_apply=Apply+Filter'
        return url

    def start_analysis(self):
        now_page = self.startPage
        while len(self.resultList) < self.maxFinding:
            url = self.build_url(now_page)
            req = request.Request(url, headers=downloader.gen_headers(self.memberId, self.passHash))
            content = request.urlopen(req).read().decode('utf-8')
            temp_list = downloader.find_galleries(content)
            for _url in temp_list:
                print('------------------------------------------------------------------------------------------')
                gallery = downloader.Gallery(_url, self.memberId, self.passHash)
                gallery.analysis_pages()
                if gallery.rating >= self.rating and gallery.length <= self.length:
                    self.resultList.append(_url)
            now_page += 1
        with open(os.path.join(self.savePath, self.searchWord + '.pkl'), 'wb') as file:
            pickle.dump(self.resultList, file)


if __name__ == '__main__':
    memberId, passHash = downloader.connect_to_exhentai('xxxxxxx', 'xxxxxxx')
    comicSearcher = ComicSearcher(r'd:\test', memberId, passHash)
    comicSearcher.set_args(_search_word='scat', _ratting=4, _start_page=4, _max_finding=30,
                           _filter=['doujinshi', 'manga', 'gamecg', 'cosplay'])
    comicSearcher.start_analysis()

