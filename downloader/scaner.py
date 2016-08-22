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
        return os.path.join(dst, 'cos', dic['name'])
    if dic['is_anthology']:
        return os.path.join(dst, 'anthology', dic['name'])
    if dic['type'] == 'artistcg' or dic['type'] == 'gamecg':
        if dic['group'] != 'none':
            author = dic['group']
        elif dic['artist']:
            author = dic['artist'][0]
        else:
            print(dic['name'])
            return None
        return os.path.join(dst, 'cg', author, dic['name'])
    if dic['type'] == 'western':
        if not dic['artist']:
            return None
        return os.path.join(dst, 'western', dic['artist'][0], dic['name'])
    if dic['type'] == 'misc':
        return os.path.join(dst, 'misc', dic['name'])
    if dic['group'] and dic['group'] != 'none':
        return os.path.join(dst, 'groups', dic['group'], dic['name'])
    if not dic['artist']:
        return None
    return os.path.join(dst, 'artists', dic['artist'][0], dic['name'])


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


def renames(root, dst):
    for root, dirs, files in os.walk(root):
        for file in files:
            if not os.path.exists(os.path.join(dst, file)):
                os.renames(os.path.join(root, file), os.path.join(dst, file))




if __name__ == '__main__':
    # renames(r'e:\comic', r'e:\new')
    clear_gif(r'd:\bbb')
    # scan(r'd:\bbb', r'd:\kkk')
    zipAll(r'd:\bbb')
    # path = r'E:\comic'
    # save_authors(path)
