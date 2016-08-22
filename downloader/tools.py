# coding=utf-8
__author__ = 'v_mading'

import math
import pickle

def getInput():
    result = []
    inn = ''
    while inn != 'end':
        inn = input()
        result.append(inn)
    result = result[:-1]
    _dic = {}
    for res in result:
        tmp = res.split(' ')
        url = tmp[0]
        length = int(tmp[1])
        pri = int(tmp[2]) if len(tmp) == 3 else 50
        prif = pri / math.log(length)
        if prif not in _dic:
            _dic[prif] = [(url, length, pri)]
        else:
            _dic[prif].append((url, length, pri))
    result = []
    urls = {}
    for k in sorted(_dic.keys(), reverse=True):
        for u in _dic[k]:
            if u[0] not in urls:
                result.append((u[0], u[1], u[2], k))
                urls[u[0]] = 1
    return result


def resort(result):
    _dic = {}
    for k in result:
        if k[3] not in _dic:
            _dic[k[3]] = [k]
        else:
            _dic[k[3]].append(k)
        result = []
    urls = {}
    for k in sorted(_dic.keys(), reverse=True):
        for u in _dic[k]:
            if u[0] not in urls:
                result.append((u[0], u[1], u[2], k))
                urls[u[0]] = 1
    return result


def read():
    with open(r'd:\test.pkl', 'rb') as file:
        return pickle.load(file)


def save(result):
    with open(r'd:\test.pkl', 'wb') as file:
        pickle.dump(result, file)

# def reverse(line):
#     tmp = line.split('\t')
#     if tmp[-1] == 'NULL':
#         return None
#     result = tmp[0] + '\t'
#     result += tmp[14] + '\t'
#     result += tmp[12] + '\t'
#     result += '01:低俗标签:' + tmp[16].split('(')[1].split(')')[0] + '\t' # 低俗
#     result += '02:信息虚假:' + tmp[18].split('(')[1].split(')')[0] + '\t' # 信息虚假
#     result += '03:效果虚假:' + tmp[19].split('(')[1].split(')')[0] + '\t' # 效果虚假
#     result += '04:治愈率和:' + tmp[20].split('(')[1].split(')')[0] + '\t' # 治愈率
#     result += '05:服务承诺:' + tmp[21].split('(')[1].split(')')[0] + '\t' # 服务承诺虚假
#     result += '06:恶性竞争:' + tmp[26].split('(')[1].split(')')[0] + '\t' # 恶性竞争
#     result += '07:禁用描述:' + tmp[24].split('(')[1].split(')')[0] + '\t' # 禁用描述
#     result += '08:专利许可:' + tmp[27].split('(')[1].split(')')[0] + '\t' # 专利许可
#     result += '09:人物肖像:' + tmp[25].split('(')[1].split(')')[0] + '\t' # 人物肖像
#     result += '10:推荐机构:' + tmp[28].split('(')[1].split(')')[0] + '\t' # 推荐机构
#     result += '11:禁止宣传:' + tmp[22].split('(')[1].split(')')[0] + '\t' # 禁止宣传
#     result += '12:排版布局:' + tmp[31].split('(')[1].split(')')[0] + '\t' # 排版布局
#     result += '13:颜色使用:' + tmp[32].split('(')[1].split(')')[0] + '\t' # 颜色使用
#     result += '14:图片使用:' + tmp[33].split('(')[1].split(')')[0] + '\t' # 图片使用
#     result += '15:文字使用:' + tmp[34].split('(')[1].split(')')[0] + '\t' # 文字使用
#     result += '16:动画效果:' + tmp[30].split('(')[1].split(')')[0] + '\t' # 动画效果
#     result += '17:有效吸引:' + tmp[35].split('(')[1].split(')')[0] + '\t' # 有效吸引
#     result += '18:表达清晰:' + tmp[36].split('(')[1].split(')')[0] + '\t' # 表达清晰
#     result += '19:厌恶标签:' + tmp[37].split('(')[1].split(')')[0] + '\t' # 厌恶
#     result += '20:你的信任:' + '0' + '\t' # lp信任
#     result += '21:你相关性:' + '0' + '\t' # lp相关性
#     result += '22:个人隐私:' + tmp[29].split('(')[1].split(')')[0] + '\t' # 个人隐私
#     result += '23:处理状态:' + '0' + '\t' # 处理状态
#     result += '24:形式美观:' + tmp[38].split('(')[1].split(')')[0] + '\t' # 形式美观
#     result += '25:警告明示:' + tmp[23].split('(')[1].split(')')[0] + '\t' # 警告明示
#     result += '26:新高危度:' + tmp[17].split('(')[1].split(')')[0] + '\t' # 高危度
#     result += tmp[-4] + '\t'
#     result += tmp[-3] + '\n'
#     return result
#
# if __name__ == '__main__':
#     with open(r'd:\baidudsp\baidudsp', encoding='utf-8') as file:
#         lines = file.readlines()
#     with open(r'd:\baidudsp\baidudsp2', 'w', encoding='utf-8') as file:
#         for line in lines:
#             line = reverse(line[:-1])
#             if line:
#                 file.write(line)

