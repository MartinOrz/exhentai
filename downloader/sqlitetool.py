__author__ = 'mading01'

import os
import zipfile
import pickle

if __name__ == '__main__':
    # root_path = r'e:\comic'
    # namelist = {}
    # err = []
    # for root, dirs, files in os.walk(root_path):
    #     for file in files:
    #         if file.endswith('.zip'):
    #             zfile = zipfile.ZipFile(os.path.join(root, file), 'r')
    #             content = zfile.read(zfile.namelist()[-1])
    #             dic = pickle.loads(content)
    #             try:
    #                 for artist in dic['artist']:
    #                     if artist not in namelist:
    #                         namelist[artist] = 1
    #                     else:
    #                         namelist[artist] += 1
    #             except:
    #                 err.append(os.path.join(root, file))
    #
    # with open(r'd:\namelist', 'w', encoding='utf-8') as file:
    #     for name in namelist:
    #         file.write(name + '\t' + str(namelist[name]) + '\n')
    #
    # with open(r'd:\err', 'w', encoding='utf-8') as file:
    #     for e in err:
    #         file.write(e + '\n')

    root_path = r'e:\comic'
    find = 'kiai_neko'
    for root, dirs, files in os.walk(root_path):
        for file in files:
            if file.endswith('.zip'):
                zfile = zipfile.ZipFile(os.path.join(root, file), 'r')
                content = zfile.read(zfile.namelist()[-1])
                dic = pickle.loads(content)
                try:
                    if find in dic['artist']:
                        print(os.path.join(root, file).encode('gbk', 'ignore').decode('gbk'))
                except:
                    print('cao:' + os.path.join(root, file).encode('gbk', 'ignore').decode('gbk'))