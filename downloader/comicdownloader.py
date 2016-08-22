# coding=utf-8
__author__ = 'mading01'

import urllib.request as request
import pickle
import codecs
import urllib.parse as parse
import urllib.error
import http.cookiejar as cookie
import queue
import threading
import time
import re
import os
import PIL.Image as Image
from numpy import array

# 用到的页面地址 =========================================================================================================

''' 登陆页面 '''
loginPage = 'https://forums.e-hentai.org/index.php?act=Login&CODE=01'

''' 里站主页 '''
exhentaiRoot = 'http://exhentai.org/'

''' 示例页面，应用filter后的搜索结果地址 '''
# http://exhentai.org/?f_doujinshi=0&f_manga=0&f_artistcg=0&f_gamecg=0&f_western=0&f_non-h=0&f_imageset=0&f_cosplay=1&f_asianporn=0&f_misc=0&f_search=&f_apply=Apply+Filter


# 用到的正则表达式编译结果，及用用正则寻找匹配的函数=============================================================================

# http://exhentai.org/g/837492/04c9db1aa5/
gallery = re.compile('http[s]*://exhentai.org/g/\d+/[^/]+/')

# <td onclick="document.location=this.firstChild.href"><a href="http://exhentai.org/g/897485/fef0313621/?p=1" onclick="return false">2</a></td>
page = re.compile('<td onclick="document.location=this.firstChild.href"><a \S+ onclick="return false">(\d+)</a></td>')

# <div id="gdc"><a href="http://exhentai.org/manga">
type = re.compile('<div id="gdc"><a href="http[s]*://exhentai\.org/([a-z-]+)">')

# <h1 id="gn">Princess Leia (Star Wars) **Alexandria the Red**</h1>
name_n = re.compile('<h1 id="gn">([^<]*)</h1>')

# <h1 id="gj">[日暮企画 (日暮りん)] デリバリーナースメイド</h1>
name_j = re.compile('<h1 id="gj">([^<]*)</h1>')

# <div id="td_language:chinese" class="gt" style="opacity:1.0">
language = re.compile('<div id="td_language:([^"]+)"')

# <div id="td_parody:kantai_collection" class="gt" style="opacity:1.0">
parody = re.compile('<div id="td_parody:([^"]+)"')

# <div id="td_group:sky_junction" class="gt" style="opacity:1.0">
group = re.compile('<div id="td_group:([^"]+)"')

# <div id="td_artist:100yen_locker" class="gt" style="opacity:1.0">
artist = re.compile('<div id="td_artist:([^"]+)"')

# <div id="td_male:bbm" class="gt" style="opacity:1.0">
male_tag = re.compile('<div id="td_male:([^"]+)"')

# <div id="td_female:bbm" class="gt" style="opacity:1.0">
female_tag = re.compile('<div id="td_female:([^"]+)"')

# <tr><td class="gdt1">Posted:</td><td class="gdt2">2015-12-02 03:38</td></tr>
posted = re.compile('<td class="gdt1">Posted:</td><td class="gdt2">(\d{4}-\d{2}-\d{2} \d{2}:\d{2})</td>')

# td_anthology
anthology = re.compile('td_anthology')

# 汉化组
translator = re.compile('[『|\(|\[|【]([^『^\(^\[^【]+[汉|漢]化[^』^\]^\)^】]*)[』|\]|\)|】]')

# var original_rating = 1.29;
rating = re.compile('<span id="rating_count">(\d+)</span>')

# <tr><td class="gdt1">Length:</td><td class="gdt2">26 pages</td></tr>
length = re.compile('<tr><td class="gdt1">Length:</td><td class="gdt2">(\d+) pages</td></tr>')

# <a href="http://exhentai.org/s/6f93ca0d83/837940-38">
pic = re.compile('<a href="(http[s]*://exhentai\.org/s/[^/]+/\d+-\d+)"><img')

# <div id="i3"><a onclick="return load_image(53, 'bc2ffa02b0')" href="http://exhentai.org/s/bc2ffa02b0/837902-53"><img id="img" src="http://182.235.21.79:2550/h/9669c3b4861d5d716265cd66f624673e620c07c2-64353-1200-675-jpg/keystamp=1438335300-6d55c19fba/a_03_05_01Z.jpg" style="height: 675px; width: 1200px; max-width: 1192px; max-height: 671px;"></a></div>
img = re.compile('<div id="i3"><a onclick="[^"]+" href="[^"]+">\s*<img id="img" src="([^"]+)"')

# <div id="i4"><div>001.jpg :: 1061 x 1506 :: 125.0 KB</div>
img_info = re.compile('<div id="i4"><div>[^:]+:: (\d+) x (\d+) :: (\S+) ([KM]*B)</div>')

# <a href="#" onclick="return nl('1642-399918')">Click here if the image fails loading</a>
another_source = re.compile('<a href="#".*?onclick="return nl\(([^\)]+)\)">Click here if the image fails loading</a>')

# <a href="http://exhentai.org/fullimg.php?gid=719020&page=1&key=520c7cc3d6">Download original 2194 x 3000 1.38 MB source</a>
original_source = re.compile('<a href="([^"]+)">Download original (\d+) x (\d+) ([\d\.]+) (\S+) source</a>')


def find_galleries(input_content):
    """
    获取页面中所有的gallery内容。
    gallery指的是类似http://exhentai.org/g/837492/04c9db1aa5/这样的链接内容。

    :param input_content: 需要解析的页面内容
    :return: 解析结果，数组形式，其中包含所有解析出的内容
    """
    return gallery.findall(input_content)


def find_pages(input_content):
    """
    获取所有的页码页。
    页码指的是<td onclick="sp(1)">这样的一段内容，其指出了一共有多少页码。

    :param input_content: 需要解析的页面内容
    :return: 最大的页码值
    """
    pages = [int(x) for x in page.findall(input_content)]
    if not pages:
        return 1
    return max(pages) + 1


def find_type(input_content):
    """
    从gallery中获取类型信息
    :param input_content: 需要解析的页面内容
    :return: 类型信息
    """
    return type.findall(input_content)[0]


def find_name_n(input_content):
    """
    从gallery中获取n类型的名称。n类型名称为英文名

    :param input_content: 需要解析的页面内容
    :return: 解析结果
    """
    return name_n.findall(input_content)[0]


def find_name_j(input_content):
    """
    从gallery中获取j类型的名称。j类型名称为日文名

    :param input_content: 需要解析的页面内容
    :return: 解析结果
    """
    return name_j.findall(input_content)[0]


def find_language(input_content):
    """
    从gallery中获取语言。对于原生日语内容，则返回'default'。
    :param input_content: 需要解析的页面内容
    :return: 解析结果
    """
    tmp = language.findall(input_content)
    if tmp:
        return tmp[0]
    else:
        return 'default'


def find_parody(input_content):
    """
    从gallery中获取同人的作品。如果是原创作品则返回'original'。
    :param input_content: 需要解析的页面内容
    :return: 解析结果
    """
    tmp = parody.findall(input_content)
    if tmp:
        return tmp[0]
    else:
        return 'original'


def find_group(input_content):
    """
    从gallery中获取group信息。group即是指作者所在的同人社团。没有则返回'none'
    :param input_content: 需要解析的页面内容
    :return: 解析结果
    """
    tmp = group.findall(input_content)
    if tmp:
        return tmp[0]
    else:
        return 'none'


def find_artist(input_content):
    """
    从gallery中获取所有的作者信息。作者可能有多个，因此返回的是列表形式。没有则返回空列表。
    :param input_content: 需要解析的页面内容
    :return: 解析结果
    """
    return artist.findall(input_content)


def find_male_tag(input_content):
    """
    从gallery中获取所有的男性标签。返回为列表形式。没有则为空列表。
    :param input_content: 需要解析的页面内容
    :return: 解析结果
    """
    return male_tag.findall(input_content)


def find_female_tag(input_content):
    """
    从gallery中获取所有的女性标签。返回为列表形式。没有则为空列表。
    :param input_content: 需要解析的页面内容
    :return: 解析结果
    """
    return female_tag.findall(input_content)


def find_posted(input_content):
    """
    从gallery中获取发表时间
    :param input_content: 需要解析的页面内容
    :return: 解析结果
    """
    return posted.findall(input_content)[0]


def find_anthology(input_content):
    """
    判断是否是杂志。
    :param input_content: 需要解析的页面内容
    :return: True 如果是杂志，否则为False
    """
    return len(anthology.findall(input_content)) > 0


def find_translator(input_content):
    """
    获取汉化组。没有则返回None
    :param input_content: 需要解析的页面内容
    :return: 解析结果
    """
    tmp = translator.findall(input_content)
    if tmp:
        return tmp[0]
    else:
        return None


def find_rating(input_content):
    """
    从gallery中获取评分。评分即为rating

    :param input_content: 需要解析的页面内容
    :return: 评分结果
    """
    return int(rating.findall(input_content)[0])


def find_length(input_content):
    """
    从gallery中获取长度信息，即有多少页

    :param input_content: 需要解析的页面内容
    :return: 作品长度
    """
    return length.findall(input_content)[0]


def find_pics(input_content):
    """
    从gallery中解析出所有的图片页面地址

    :param input_content: 需要解析的页面内容
    :return: 列表形式的图片页面地址
    """
    return pic.findall(input_content)


def find_img(input_content):
    """
    从某个图面页面中获取图片的具体地址

    :param input_content:  需要解析的页面内容
    :return: 解析出的图片地址
    """
    return img.findall(input_content)[0]


def find_img_info(input_content):
    """
    从某个图片页面中获取图片的信息。用以检查下载的图片是否正确

    :param input_content: 需要解析的页面内容
    :return: ImageInfo实体信息
    """
    result = img_info.findall(input_content)[0]
    if result[3] == 'KB':
        size = float(result[2])
    elif result[3] == 'B':
        size = float(result[2]) / 1024
    else:
        size = float(result[2]) * 1024
    return ImageInfo(int(result[0]), int(result[1]), size)


def find_another_img(input_content):
    """
    当图片下载失败的时候尝试换个图源

    :param input_content: 需要解析的页面内容
    :return: 新图源的页面后缀
    """
    return another_source.findall(input_content)[0][1:-1]


def find_original_source(input_content):
    """
    尝试寻找原始图源（更清晰）
    :param input_content:  需要解析的页面内容
    :return: 原图地址信息和图片信息
    """
    ori = original_source.findall(input_content)
    if not ori:
        return None
    result = ori[0]
    path = result[0].replace('&amp;', '&')
    if result[4] == 'KB':
        size = float(result[3])
    elif result[3] == 'B':
        size = float(result[3]) / 1024
    else:
        size = float(result[3]) * 1024
    img = ImageInfo(int(result[1]), int(result[2]), size)
    return path, img


# 工具方法，主要提供对exhentai的连接服务 ====================================================================================

def connect_to_exhentai(username, password):
    """ 连接到exhentai。
        登录里站时，需要先登录表站，然后使用表站的cookie访问里站的页面，即可正常访问里站。

        returns:
            - member_id: 用于生成header
            - pass_hash: 用于生成header
    """
    cj = cookie.CookieJar()
    opener = request.build_opener(request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]
    data = parse.urlencode({'returntype': 8, 'CookieDate': 1, 'b': 'd', 'bt': 'pone',
                            'UserName': username, 'PassWord': password}).encode(encoding='UTF8')
    opener.open(loginPage, data)
    for c in cj:
        if c.name == 'ipb_member_id':
            member_id = c.value
        if c.name == 'ipb_pass_hash':
            pass_hash = c.value

    return member_id, pass_hash


def gen_headers(member_id, pass_hash, referer=''):
    """
    生成一个随机的请求头部

    :param member_id: 用户id，在登录之后可以获取到
    :param pass_hash: 用户密码的hash值，在登录之后可以得到
    :param referer: 请求头部的referer信息
    :return: 生成的请求头
    """
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 ' + \
                 'Safari/537.36'
    h_cookie = 'nw=1;ipb_member_id=' + member_id + ';ipb_pass_hash=' + pass_hash + ';'
    headers = {'User-Agent': user_agent, 'Accept-Language': 'zh-CN,zh;q=0.8', 'Accept-Charset': 'utf-8;q=0.7,*;q=0.7',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Connection': 'keep-alive',
               'Cookie': h_cookie}
    return headers


# 文件相关的工具方法 ======================================================================================================

def save_img(src_page, src, save_path, ori=None):
    """
    将图片保存

    :param src_page: 解析图片地址的页面地址
    :param src: 图片地址
    :param is_ori: 是否下载的是原图
    :return: 图片保存地址
    """
    if '?' in src_page:
        img_name = src_page.split("?")[0].split("-")[-1]
    else:
        img_name = src_page.split("-")[-1]
    src = src.replace('&amp;', '&')
    suffix = src.split(".")[-1]
    if len(img_name) == 1:
        img_name = '00' + img_name
    elif len(img_name) == 2:
        img_name = '0' + img_name
    if ori: # 下载原图
        ori = ori.replace('&amp;', '&')
        img_name += '_ori'
        req = request.Request(ori, headers=gen_headers(memberId, passHash, src))
    else:
        req = src
    file_name = os.path.join(save_path, img_name + '.' + suffix)
    if os.path.exists(file_name): # 已经下载过的图片
        return file_name
    response = request.urlopen(req, timeout=120)
    with open(file_name, 'wb') as _file:
        _content = response.read()
        _file.write(_content)
    return file_name


def del_img(file_name):
    """
    将图片删除。删除前会线检查图片是否存在。

    :param file_name: 要删除的图片地址
    :return: None
    """
    if os.path.exists(file_name):
        os.remove(file_name)


def count_img_hash(file_name):
    """
    使用差分哈希方法计算图像的哈希值
    :param file_name: 需要计算的文件名
    :return: 得出的哈希值
    """
    _image = Image.open(file_name)
    _image = _image.resize((9, 8))
    _image = array(_image.convert('L'))
    result = 0
    for line in _image:
        now = -1
        for num in line:
            num = int(num)
            if now >= 0:
                result = (result << 1) + (1 if num - now > 0 else 0)
            now = num
    return result


def clean_dir(root_path):
    for root, dirs, files in os.walk(root_path):
        for file in files:
            file = os.path.join(root, file)
            size = os.path.getsize(file)
            if size == 0 or size in [142, 143]: # 142是403gif的大小
                os.remove(file)

# 用于记录信息的函数 ======================================================================================================

LOG_LEVELS = ['info ', 'warn ', 'error', 'fatal']  # log级别

NOW_LEVEL = 0  # 当前的log级别


def log(info_mode, *args):
    """
    按格式输出信息。

    :param info_mode: 输出头部，格式为[info_mode]:
    :param args: 输出的内容
    :return: None
    """
    if info_mode >= NOW_LEVEL:
        print('[' + LOG_LEVELS[info_mode] + ']:', end=' ')
        for arg in args:
            print(arg, end=' ')
        print('')


# 承载下载信息的类 =======================================================================================================

class Gallery:
    """
    一个画集，即具体下载的一部作品。
    """

    def __init__(self, rpath, member_id, pass_hash):
        """
        初始化函数。gallery以基本路径作为基础，包含了以下参数：

        - rootPath: 路径，形式为 http://exhentai.org/g/837492/04c9db1aa5/
        - member_id: 用户id
        - pass_hash: 用户密码hash，以上参数用以读取url内容
        - attributeCode: 特征码，即837492这样的数字
        - attributeStr: 特征字符串，即04c9db1aa5这一串
        - type: 作品类型
        - posted: 发布时间
        - name_j: 日文名称
        - name_n: 英文名称
        - name: 作品名称，取日文名，如无日文名则取英文名
        - language: 作品语言
        - parody: 同人作品
        - group: 同人社团
        - artist: 作者
        - male_tag: 男性标签
        - female_tag: 女性标签
        - is_anthology: 是否是杂志
        - translator: 汉化组
        - rating: 评分，取平均值
        - length: 作品长度，即共有多少图片
        - pages: 页码，即此画集包含多少页页面
        - imgList: 所有图片的地址列表
        - originList: 所有原图的地址信息

        :param rpath: gallery的基本路径
        :param member_id: e站用户id
        :param pass_hash: e站用户密码哈希值
        :return: 类型实例
        """
        self.rootPath = rpath

        self.member_id = member_id
        self.pass_hash = pass_hash

        temp_list = rpath.split('/')
        self.attributeCode = temp_list[4]
        self.attributeStr = temp_list[5]
        self.type = ''
        self.posted = ''
        self.name_j = ''
        self.name_n = ''
        self.name = ''
        self.language = ''
        self.parody = ''
        self.group = ''
        self.artist = []
        self.male_tag = []
        self.female_tag = []
        self.is_anthology = False
        self.translator = ''
        self.rating = 0
        self.length = 0
        self.pages = 0
        self.imgList = []
        self.originList = {}
        self.imgHashDic = {}

    def analysis_pages(self):
        """
        根据gallery路径分析页面内容，填充数据。

        :return: 读取的页面内容，可供进一步解析
        """
        log(0, '开始分析作品内容 ================================================================')
        req = request.Request(self.rootPath, headers=gen_headers(self.member_id, self.pass_hash))
        _content = request.urlopen(req, timeout=60).read().decode('utf-8')
        self.type = find_type(_content)
        self.posted = find_posted(_content)

        # 获取语言和名称，汉化组。中文由于需要寻找汉化组，所以处理方式不一样
        self.language = find_language(_content)
        if self.language == 'chinese':
            name1 = find_name_n(_content)
            name2 = find_name_j(_content)
            self.name_n = name1
            self.name_j = name2
            trans1 = find_translator(name1)
            trans2 = None
            if name2:
                trans2 = find_translator(name2)
                self.name = name2
            else:
                self.name = name1

            if trans2:
                self.translator = trans2
            elif trans1:
                self.translator = trans1
            else:
                self.translator = '未知汉化'

        else:
            # 解析名称，如果有日文名则设置为日文名，否则设置为英文名
            self.name_j = find_name_j(_content)
            self.name_n = find_name_n(_content)
            if self.name_j:
                self.name = self.name_j
            else:
                self.name = self.name_n
            self.translator = 'none'

        self.parody = find_parody(_content)
        self.group = find_group(_content)
        self.artist = find_artist(_content)
        self.male_tag = find_male_tag(_content)
        self.female_tag = find_female_tag(_content)
        self.is_anthology = find_anthology(_content)

        invalid_chars = '?*"<>/;:|'
        for char in invalid_chars:
            self.name = self.name.replace(char, ' ')
        log(0, '获取作品名称结束:', codecs.encode(self.name, 'gbk', 'ignore').decode('gbk'))

        # 解析评分
        self.rating = float(find_rating(_content)) / 10
        log(0, '获取作品评分结束:', self.rating)

        # 解析长度
        self.length = int(find_length(_content))
        log(0, '获取作品长度结束，共:', self.length, '页')

        # 获取所有图片========================================================================
        self.pages = find_pages(_content)
        log(0, '获取页面长度结束，共:', self.pages, '页')
        return _content

    def get_all_imgs(self, _content):
        """
        获取此gallery下的所有图片

        :param _content: 页面的解析结果
        """
        # 第一页单独获取，因为content已经拿到，同时不需要添加p=?的参数
        self.imgList = [ImageDownloadTask(self.rootPath, p) for p in find_pics(_content)]
        with open(r'd:\1.pkl', 'wb') as file:
            pickle.dump([l.downloadInfo for l in self.imgList], file)
        log(0, '从第1页获取图片列表结束, 当前的图片列表长度:', len(self.imgList))
        
        ref = self.rootPath
        for i in range(1, self.pages):
            now_page = self.rootPath + '?p=' + str(i)
            req = request.Request(now_page, headers=gen_headers(self.member_id, self.pass_hash, ref))
            _content = request.urlopen(req, timeout=60).read().decode('utf-8')
            self.imgList += [ImageDownloadTask(self.rootPath, p) for p in find_pics(_content)]
            self.imgList = list(set(self.imgList))
            log(0, '从第' + str(i + 1) + '页获取图片列表结束, 当前的图片列表长度:', len(self.imgList))
            ref = now_page

    def to_dict(self):
        """
        变形为一个dict以存储
        """
        dic = dict()
        dic['root_path'] = self.rootPath
        dic['attributeCode'] = self.attributeCode
        dic['attributeStr'] = self.attributeStr
        dic['type'] = self.type
        dic['posted'] = self.posted
        dic['name_j'] = self.name_j
        dic['name_n'] = self.name_n
        dic['name'] = self.name
        dic['language'] = self.language
        dic['parody'] = self.parody
        dic['group'] = self.group
        dic['artist'] = self.artist
        dic['male_tag'] = self.male_tag
        dic['female_tag'] = self.female_tag
        dic['is_anthology'] = self.is_anthology
        dic['translator'] = self.translator
        dic['rating'] = self.rating
        dic['length'] = self.length
        dic['pages'] = self.pages
        dic['img_list'] = [img_task.to_dict() for img_task in self.imgList]
        dic['originList'] = self.originList
        dic['imgHashDic'] = self.imgHashDic
        return dic


class ImageDownloadTask:
    """
    一个图片下载的任务，仅仅承载一张图片的下载。
    """

    def __init__(self, referer, download_info):
        """
        初始化函数，此类主要包括参数如下：

        - referer: 获取图片是的referer信息，使用获取图片页面的前一页的地址
        - downloadInfo: 具体的下载地址
        - tryTimes: 尝试次数
        - originalNotTried: 原图是否已尝试下载过

        :param referer: 用以设定referer
        :param download_info: 用以设定downloadInfo
        :return: 类型实例
        """
        self.referer = referer  # gallery某一页的地址，即跳转到具体的图片页面的那个页面的地址
        self.downloadInfo = download_info  # 具体的图片下载页面地址
        self.tryTimes = 0  # 重试次数，超过5的时候有可能图片本身已经挂了，则记录之，后续另行下载
        self.suffix = ''
        self.originalNotTried = True

    def try_times_add_once(self):
        """
        增加一次重试次数
        """
        self.tryTimes += 1

    def is_over_tried(self):
        """
        判断尝试次数是否超限

        :return: 超过5次则为尝试次数超限
        """
        return self.tryTimes > 3

    def to_dict(self):
        dic = dict()
        dic['referer'] = self.referer
        dic['downloadInfo'] = self.downloadInfo
        return dic


class ImageInfo:
    """
    图片信息类，用以检测下载的图片是否正确
    """

    def __init__(self, expected_width, expected_height, expected_size):
        """
        初始化函数。此类包含以下参数:

        - expectedWidth: 期望宽度，从页面获取
        - expectedHeight: 期望高度，从页面获取
        - expectedSize: 期望大小，从页面获取
        - path: 下载以后的地址
        - realWidth: 下载文件的实际宽度
        - realHeight: 下载文件的实际高度
        - realSize: 下载文件的实际大小

        :param expected_width: 期望宽度
        :param expected_height: 期望高度
        :param expected_size: 期望大小
        :return: 类型实例
        """
        self.expectedWidth = expected_width
        self.expectedHeight = expected_height
        self.expectedSize = expected_size
        self.path = ''
        self.realWidth = 0
        self.realHeight = 0
        self.realSize = 0

    def set_real_info(self, img_path):
        """
        根据图片地址获取图片的实际信息

        :param img_path: 下载的图片的地址
        :return: None
        """
        self.path = img_path
        _img = Image.open(self.path)
        self.realWidth, self.realHeight = _img.size
        self.realSize = os.path.getsize(self.path) / 1024  # 转化为kb

    def is_valid(self):
        """
        判断文件是否合法。需要在set_real_info()方法调用之后调用才能得到正确结果。

        :return: 图片是否合法
        """
        if self.realWidth != self.expectedWidth:
            return False
        if self.realHeight != self.expectedHeight:
            return False

        size_diff = self.realSize - self.expectedSize
        return (15 > size_diff) and (-15 < size_diff)

    def __str__(self):
        return "[ImageInfo : width: " + str(self.realWidth) + "/" + str(self.expectedWidth) + \
               ", height: " + str(self.realHeight) + "/" + str(self.expectedHeight) + ", size: " + str(self.realSize) +\
               "/" + str(self.expectedSize) + "]"


# 下载工作执行的类========================================================================================================

class Dispatcher(threading.Thread):
    """
    监视线程，也负责工作的维护
    """

    def __init__(self, gall, root_path, worker_number, member_id, pass_hash):
        threading.Thread.__init__(self)
        self.name = 'Dispatcher'
        self.queue = queue.Queue()
        self.gallery = gall
        for image in gall.imgList:
            self.queue.put(image)

        self.done = False
        self.workers = []
        self.unfinishList = []
        self.savePath = os.path.join(root_path, gall.name)
        if not os.path.exists(self.savePath):
            os.mkdir(self.savePath)
        for i in range(worker_number):
            self.workers.append(Worker('Worker' + str(i), self.savePath, self.queue, member_id, pass_hash,
                                       self.unfinishList, self.gallery.originList, self.gallery.imgHashDic))

    def run(self):

        for worker in self.workers:
            worker.start()

        while not self.done:

            awake = 0
            for worker in self.workers:
                # 查询线程工作状态
                if not worker.done:
                    awake += 1

            if awake < self.queue.qsize():
                # 当工作线程数少于任务队列中的任务数时，唤醒一个线程
                for worker in self.workers:
                    if worker.done:
                        worker.wake_up()
                        break

            elif self.queue.qsize() < 1 and awake == 0:
                # 当任务队列结束，并且所有线程都结束时，任务结束
                self.done = True
                for worker in self.workers:
                    worker.stop()
                if len(self.unfinishList) > 0:
                    with open(os.path.join(self.savePath, 'undone.pkl'), 'wb') as f:
                        pickle.dump(self.unfinishList, f)
                with open(os.path.join(self.savePath, 'gallery.dic'), 'wb') as f:
                    pickle.dump(self.gallery.to_dict(), f)
                log(0, 'Task Over')

            time.sleep(2)


class Worker(threading.Thread):
    """
    下载工作类，即一个线程
    """

    def __init__(self, name, save_path, que, member_id, pass_hash, unfinish_list, originList, imgHashDic):
        threading.Thread.__init__(self)
        self.name = name
        self.unfinishList = unfinish_list
        self.savePath = save_path  # 图片保存地址
        self.done = False  # 任务是否已完成
        self.queue = que  # 任务队列
        self.doing = ''
        self.originList = originList
        self.imgHashDic = imgHashDic
        self.has403 = False

        self.memberId = member_id
        self.passHash = pass_hash

    def wake_up(self):
        """
        唤醒此线程，重新开始进行下载任务
        """
        log(0, self.name + " is wake up")
        self.done = False
        self.start()

    def stop(self):
        """
        彻底终止此线程
        """
        self.done = True

    def run(self):
        """
        执行下载任务
        """
        while not self.done:
            try:
                task = self.queue.get(timeout=5)  # 阻塞模式，最多等待5秒
                file_name = 'not_exists'
                _content = None
                if task.is_over_tried():
                    log(0, 'task:', task.downloadInfo, 'is over tried, now list size:', len(self.unfinishList))
                    self.unfinishList.append(task.downloadInfo)
                    log(0, 'task:', task.downloadInfo, 'append task:', task.downloadInfo, 'now list size:', len(self.unfinishList))
                elif self.has403:
                    log(0, '403 happened, now list size:', len(self.unfinishList))
                    self.unfinishList.append(task.downloadInfo)
                    log(0, 'task:', task.downloadInfo, 'append task:', task.downloadInfo, 'now list size:', len(self.unfinishList))
                else:
                    log(0, self.name + " has taken work: " + task.downloadInfo + ", now queue size: "
                        + str(self.queue.qsize()))
                    # 先尝试下载原图
                    self.doing = task.downloadInfo + task.suffix
                    ori = None
                    req = request.Request(self.doing, headers=gen_headers(self.memberId, self.passHash, task.referer))
                    _content = request.urlopen(req, timeout=60).read().decode('utf-8')
                    ori_result = find_original_source(_content)
                    src = find_img(_content)
                    if task.originalNotTried and ori_result:
                        ori, file_info = ori_result
                        self.originList[task.downloadInfo] = ori
                        task.originalNotTried = False
                    else:
                        file_info = find_img_info(_content)

                    file_name = save_img(self.doing, src, self.savePath, ori)
                    file_info.set_real_info(file_name)
                    if not file_info.is_valid():  # 如果下载的图片不合法，则删除之，并且将任务重新插入队列
                        log(1, self.name + " download an invalid image:", file_info)
                        del_img(file_name)
                        self.put_back_task(task)
                    else:
                        self.imgHashDic[file_name.split('\\')[-1]] = count_img_hash(file_name)
            except queue.Empty:  # empty即取出任务失败，没有任务可用时
                log(0, self.name + " is done")
                self.stop()
            except urllib.error.URLError as e:
                # 网络问题，此时content可能还没有赋值
                log(2, self.name + " open url failed.", e)
                if _content:
                    if len(task.suffix) == 0:
                        task.suffix = '?nl=' + find_another_img(_content)
                    else:
                        task.suffix += '&nl=' + find_another_img(_content)
                self.put_back_task(task)
            except urllib.error.HTTPError as e:
                if str(e.code) == '403':
                    log(2, self.name + " has 403.", e)
                    self.has403 = True
                    self.put_back_task(task)
                else:
                    log(2, self.name + " open url failed.", e)
                    if len(task.suffix) == 0:
                        task.suffix = '?nl=' + find_another_img(_content)
                    else:
                        task.suffix += '&nl=' + find_another_img(_content)
                    self.put_back_task(task)
            except Exception as e:  # 连接超时等其他错误
                log(2, self.name + " open url failed.", e)
                if len(task.suffix) == 0:
                    task.suffix = '?nl=' + find_another_img(_content)
                else:
                    task.suffix += '&nl=' + find_another_img(_content)
                self.put_back_task(task)

    def put_back_task(self, task):
        """
        将下载失败的任务重新放回队列中，并将其tryTimes加1

        :param task: 失败的任务
        :return: None
        """
        log(2, self.name + " put back work: " + task.downloadInfo + task.suffix + ", tried : " + str(task.tryTimes))
        task.try_times_add_once()
        self.queue.put(task)


class Scavenger(threading.Thread):
    """
    执行补充工作的线程，即某些图片下载不下来时此线程会启动然后不断尝试下载
    """

    def __init__(self, root_path, member_id, pass_hash):
        threading.Thread.__init__(self)
        self.name = 'Scavenger'
        self.rootPath = root_path
        self.done = False
        self.memberId = member_id
        self.passHash = pass_hash
        self.workList = queue.Queue()
        self.unfinishWorks = {}

    def find_works(self):
        i = 0
        for parent, dicts, files in os.walk(self.rootPath):
            for pkl in files:
                if pkl == 'undone.pkl':
                    with open(os.path.join(parent, pkl), 'rb') as _file:
                        tmp_list = pickle.load(_file)
                    for uurl in tmp_list:
                        i += 1
                        self.workList.put([i, uurl, parent])
                    del_img(os.path.join(parent, pkl))

    def save_unfinish_work(self, _url, _parent):
        if '?' in _url:
            _url = _url.split('?')[0]
        if _parent not in self.unfinishWorks:
            self.unfinishWorks[_parent] = [_url]
        else:
            self.unfinishWorks[_parent].append(_url)

    def run(self):
        self.find_works()
        finish = 0
        log(0, '本次执行下载任务共', self.workList.qsize(), '个。')
        while not self.done:
            try:
                task = self.workList.get(timeout=5)
                i, _url, _parent = task
                req = request.Request(_url, headers=gen_headers(self.memberId, self.passHash))
                content = request.urlopen(req, timeout=60).read().decode('utf-8')
                ori = None
                ori_result = find_original_source(content)
                if ori_result:
                    ori, file_info = ori_result
                else:
                    file_info = find_img_info(content)

                src = find_img(content)
                file_name = 'not_exists'

                file_name = save_img(_url, src, _parent, ori)
                file_info.set_real_info(file_name)
                if not file_info.is_valid():  # 如果下载的图片不合法，则删除之，并且将任务重新插入队列
                    # del_img(file_name)
                    self.save_unfinish_work(_url, _parent)
                    log(2, '任务', i, '失败:', _url, 'reason:', file_info)
                else:
                    log(0, '任务', i, '成功:', _url)
                    finish += 1

            except queue.Empty:  # empty即取出任务失败，没有任务可用时
                self.done = True

            except Exception as e:
                log(2, '任务', i, '失败:', _url, 'reason:', e)
                if '?' not in _url:
                    _url = _url + '?nl=' + find_another_img(content)
                    print(file_name)
                    if file_name != 'not_exists' and os.path.exists(file_name):
                        os.remove(file_name)
                    log(0, '任务', i, '更换图源，准备重新下载')
                    self.workList.put([i, _url, _parent])
                else:
                    self.save_unfinish_work(_url, _parent)

        for _path in self.unfinishWorks:
            with open(os.path.join(_path, 'undone.pkl'), 'wb') as _file:
                pickle.dump(self.unfinishWorks[_path], _file)
        log(0, '本次执行下载任务共成功', finish, '个。')


def find_undone_imgs(root_path):
    for dir in os.listdir(root_path):
        dicName = os.path.join(root_path, dir, 'gallery.dic')
        if os.path.exists(dicName):
            pages = {}
            for f in os.listdir(os.path.join(root_path, dir)):
                p = f.split('.')[0].split('_')[0]
                if p != 'gallery' and p !='undone':
                    pages[int(p)] = f

            with open(dicName, 'rb') as file:
                imgs = pickle.load(file)['img_list']
            undones = []
            for img in imgs:
                p = int(img['downloadInfo'].split('-')[1])
                if p not in pages:
                    undones.append(img)
                else:
                    size = os.path.getsize(os.path.join(root_path, dir, pages[p]))
                    if size == 0 or size == 142:
                        undones.append(img)
            if len(undones) > 0:
                os.renames(os.path.join(root_path, dir), os.path.join(r'd:\undone', dir))


def find_authors(root_path, member_id, pass_hash):
    """
    对于没有作者信息的作品，重新定位其作者信息
    :param root_path: 需要搜索的文件夹
    :param member_id: 用户id
    :param pass_hash: 密码hash
    :return: None
    """
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('dic'):
                with open(os.path.join(root, file), 'rb') as f:
                    gallery_dic = pickle.load(f)
                try:
                    g = Gallery(gallery_dic['root_path'], member_id, pass_hash)
                    g.analysis_pages()
                    if g.artist or g.group:
                        log(0, root)
                        tmp = g.to_dict()
                        tmp['img_list'] = gallery_dic['img_list']
                        tmp['originList'] = gallery_dic['originList']
                        with open(os.path.join(root, file), 'wb') as f:
                            pickle.dump(tmp, f)
                except Exception as e:
                    log(2, '获取信息出现问题:', e)


if __name__ == '__main__':
    # memberId, passHash = connect_to_exhentai('mdlovewho', 'ma199141')
    memberId = '2631394'
    passHash = '77ded0c31e820ed60d11e6ca9b458c72'

    log(0, '连接e绅士成功!')
    clean_dir(r'd:\bbb')
    # find_undone_imgs(r'd:\bbb')
    # # # # # # # # # # #
    with open(r'd:\test.pkl', 'rb') as ff:
        fileList = pickle.load(ff)

    log(0, '本次下载共', len(fileList), '个任务')
    i = 0
    for line in fileList:
        line = line[0]
        log(0, "任务地址: ", line)
        i += 1
        gallery = Gallery(line, memberId, passHash)
        content = gallery.analysis_pages()
        gallery.get_all_imgs(content)
        log(0, '任务', i, '分析画集结束！')
        dispatcher = Dispatcher(gallery, r'd:\bbb', 5, memberId, passHash)
        dispatcher.start()

        while not dispatcher.done:
            time.sleep(10)
    # #
    # scavenger = Scavenger(r'D:\bbb', memberId, passHash)
    # scavenger.start()

    # find_authors(r'd:\bbb', memberId, passHash)

    # root_path = r'e:\eee'
    # errs = []
    # import zipfile
    # for root, dirs, files in os.walk(root_path):
    #     for file in files:
    #         if file.endswith('.zip'):
    #             try:
    #                 zfile = zipfile.ZipFile(os.path.join(root, file), 'r')
    #                 content = zfile.read(zfile.namelist()[-1])
    #                 dic = pickle.loads(content)
    #                 root_path = dic['root_path']
    #                 gallery = Gallery(root_path, memberId, passHash)
    #                 gallery.analysis_pages()
    #                 with open(os.path.join(root, file + '.dic'), 'wb') as f:
    #                     pickle.dump(gallery.to_dict(), f)
    #             except:
    #                 errs.append(os.path.join(root, file))
    # with open(r'd:\err', 'w', encoding='utf-8') as file:
    #     for err in errs:
    #         file.write(err + '\n')








