# coding=utf-8
__author__ = 'mading01'

import os
import pickle
import zipfile
import shutil


def scan(src, dst):
    dst_dirs = []
    for root, dirs, files in os.walk(src):
        for file in files:
            if file.endswith('zip'):
                with open(os.path.join(root, file), 'rb') as file:
                    dic = pickle.load(file)
                d = get_path(dst, dic)
                if d:
                    dst_dirs.append((root, d))

    for root, save_dst in dst_dirs:
        os.renames(root, save_dst)


def get_path(dst, dic):
    if dic['type'] == 'cosplay':
        return os.path.join(dst, 'cos', dic['name'] + '.zip')
    if dic['is_anthology']:
        return os.path.join(dst, 'anthology', dic['name'])
    if dic['type'] == 'artistcg' or dic['type'] == 'gamecg':
        if dic['group'] != 'none':
            return os.path.join(dst, 'cg', 'groups', dic['group'], dic['name'] + '.zip')
        elif dic['artist']:
            return os.path.join(dst, 'cg', 'artists', dic['artist'][0], dic['name'] + '.zip')
        else:
            return None
    if dic['type'] == 'western':
        if not dic['artist']:
            return None
        return os.path.join(dst, 'western', 'artists', dic['artist'][0], dic['name'] + '.zip')
    if dic['type'] == 'misc':
        return os.path.join(dst, 'misc', dic['name'] + '.zip')
    if dic['group'] and dic['group'] != 'none':
        return os.path.join(dst, 'manga', 'groups', dic['group'], dic['name'] + '.zip')
    if not dic['artist']:
        return None
    return os.path.join(dst, 'manga', 'artists', dic['artist'][0], dic['name'] + '.zip')


def zip(path):
    file_name = path + '.zip'
    try:
        print('Start zip: ' + file_name)
    except:
        print('Print Name error.')
    zip_file = zipfile.ZipFile(file_name, mode='w', compression=zipfile.ZIP_STORED)
    for root, dirs, files in os.walk(path):
        for f in files:
            zip_file.write(os.path.join(root, f), os.path.join(root, f).replace(path + os.sep, ''))
    zip_file.close()
    shutil.rmtree(path)


def zipAll(path):
    if not os.path.isdir(path):
        return
    dic_path = os.path.join(path, 'gallery.dic')
    if os.path.exists(dic_path):
        zip(path)
    else:
        for d in os.listdir(path):
            zipAll(os.path.join(path, d))


def get_zip_gallery(zpath):
    zip_file = zipfile.ZipFile(zpath, "r")
    gallery_name = zip_file.namelist()[-1]
    gallery = pickle.loads(zip_file.read(gallery_name), encoding='utf-8')
    return gallery


def clear_gif(root_path):
    for root, dirs, files in os.walk(root_path):
        for file in files:
            fileName = os.path.join(root, file)
            if file.endswith('gif'):
                os.remove(fileName)
            elif os.path.getsize(fileName) < 1:
                os.remove(fileName)


def save_authors(root_path):
    artists = set([])
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.zip'):
                gallery = get_zip_gallery(os.path.join(root, file))
                artist = gallery['artist']
                artists.update(artist)
    with open(r'd:\artists', 'w', encoding='utf-8') as file:
        for art in artists:
            file.write(art + "\t\n")


def renames(root_dir, dst):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('zip'):
                zip_file = zipfile.ZipFile(os.path.join(root, file), "r")
                gall = None
                for name in zip_file.namelist():
                    if name == 'gallery.dic':
                        gall = pickle.loads(zip_file.read(name), encoding='utf-8')
                zip_file.close()
                if gall:
                    path = get_path(dst, gall)
                    if path:
                        try:
                            os.renames(os.path.join(root, file), path)
                        except:
                            print('fail!')



def findInvalidZips(root_dir, dst):
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('zip'):
                zip_file = zipfile.ZipFile(os.path.join(root, file), "r")
                for name in zip_file.namelist():
                    length = len(zip_file.read(name))
                    if name.endswith('gif') or length < 10 or length in [142, 143] or name == 'undone.pkl':
                        zip_file.close()
                        os.renames(os.path.join(root, file), os.path.join(dst, file))
                        break


def getGroupsAndAuthors(root_path):
    artists = {}
    groups = {}

    al = []
    gl = []

    done = 0
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('zip'):
                zip_file = zipfile.ZipFile(os.path.join(root, file), "r")
                for name in zip_file.namelist():
                    if name == 'gallery.dic':
                        gall = pickle.loads(zip_file.read(name), encoding='utf-8')
                        zip_file.close()
                        if gall['group'] not in groups:
                            gl.append(gall['group'])
                            groups[gall['group']] = gall['root_path']
                        for a in gall['artist']:
                            if a not in artists:
                                al.append(a)
                                artists[a] = gall['root_path']
            done += 1
            print('Get author info done: ', done)
    with open(r'd:\group', 'w', encoding='utf-8') as file:
        for g in gl:
            file.write(g + " " + groups[g] + "\n")
    with open(r'd:\artist', 'w', encoding='utf-8') as file:
        for a in al:
            file.write(a + " " + artists[a] + "\n")


if __name__ == '__main__':
    # # renames(r'e:\comic', r'e:\new')
    # clear_gif(r'd:\bbb')
    # # scan(r'd:\bbb', r'd:\kkk')
    zipAll(r'd:\bbb')
    # # path = r'E:\comic'
    # # save_authors(path)

    # getGroupsAndAuthors(r'E:\comic\western')

    # renames(r'e:\new', r'e:\comic')
    # for root, dirs, files in os.walk(r'E:\comic\anthology'):
    #     for file in files:
    #         if not file.endswith('zip'):
    #             os.renames(os.path.join(root, file), os.path.join(root, file + '.zip'))
