# coding=utf-8
__author__ = 'v_mading'


class Gallery:
    """
    作品类
    """

    def __init__(self):
        self.id = 0
        self.path = ''
        self.savePath = ''
        self.name = ''
        self.nameN = ''
        self.nameJ = ''
        self.type = ''
        self.language = ''
        self.parody = ''
        self.isAnthology = 0
        self.translator = ''
        self.ratting = 0
        self.length = 0
        self.posted = ''
        self.anthology = ''

    def to_dict(self):
        result = dict()
        result['id'] = self.id
        result['path'] = self.path
        result['savePath'] = self.savePath
        result['name'] = self.name
        result['nameN'] = self.nameN
        result['nameJ'] = self.nameJ
        result['type'] = self.type
        result['language'] = self.language
        result['parody'] = self.parody
        result['isAnthology'] = self.isAnthology
        result['translator'] = self.translator
        result['ratting'] = self.ratting
        result['length'] = self.length
        result['posted'] = self.posted
        result['anthology'] = self.anthology


class Author:
    """
    作者类
    """

    def __init__(self):
        self.id = 0
        self.name = ''
        self.text = ''
        self.comicCount = 0
        self.ratting = 50

    def to_dict(self):
        result = dict()
        result['id'] = self.id
        result['name'] = self.name
        result['text'] = self.text
        result['comicCount'] = self.comicCount
        result['ratting'] = self.ratting
        return result

