# -*- coding: utf-8 -*-
__author__ = 'v_mading'

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
import os
import sys
import zipfile


class ExHentaiMain(QtWidgets.QMainWindow):

    def __init__(self):
        super(ExHentaiMain, self).__init__()
        self.nowFile = None
        self.nowFileName = ''
        self.nowIdx = 0

        self.setWindowTitle('Exhentai')
        self.openAction = QtWidgets.QAction('打开目录', self)
        self.openAction.triggered.connect(self.set_rootpath)

        self.menuBar = self.menuBar()
        self.mainMenu = self.menuBar.addMenu('文件')
        self.mainMenu.addAction(self.openAction)

        main_ground = QtWidgets.QWidget()
        grid = QtWidgets.QGridLayout()
        main_ground.setLayout(grid)
        self.setCentralWidget(main_ground)

        self.filesTree = QtWidgets.QTreeView()
        self.filesTree.clicked.connect(self.file_selected)
        grid.addWidget(self.filesTree, 1, 1)

        self.image = QtWidgets.QLabel('test')
        self.image.setFixedWidth(500)
        self.image.setFixedHeight(500)
        grid.addWidget(self.image, 1, 2, 1, 4)

        self.pre = QtWidgets.QPushButton('<')
        self.pre.clicked.connect(self.pre_page)
        grid.addWidget(self.pre, 2, 2)

        self.next = QtWidgets.QPushButton('>')
        self.next.clicked.connect(self.next_page)
        grid.addWidget(self.next, 2, 3)

        self.delete = QtWidgets.QPushButton('delete')
        self.delete.clicked.connect(self.delete_file)
        grid.addWidget(self.delete, 2, 4)

        self.save = QtWidgets.QPushButton('save')
        self.save.clicked.connect(self.re_save)
        grid.addWidget(self.save, 2, 5)

    def set_rootpath(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(self, "选取文件夹", "E:/comic")
        model = QtWidgets.QFileSystemModel()
        model.setRootPath(dir)
        self.filesTree.setModel(model)

        index = model.index(QtCore.QDir.cleanPath(dir))
        if index.isValid():
            self.filesTree.setRootIndex(index)

    def file_selected(self, index):
        self.nowFileName = self.filesTree.model().filePath(index)
        if not self.nowFileName.endswith('zip'):
            return
        self.nowFile = zipfile.ZipFile(self.nowFileName, 'r')
        self.nowIdx = 0
        content = self.nowFile.read(self.nowFile.namelist()[self.nowIdx])
        image = QtGui.QPixmap()

        form = self.nowFile.namelist()[self.nowIdx].split(r".")[1]
        image.loadFromData(content, form)
        image = image.scaled(self.image.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.image.setPixmap(image)

    def next_page(self):
        if len(self.nowFile.namelist()) == self.nowIdx + 1:
            return
        self.nowIdx += 1
        form = self.nowFile.namelist()[self.nowIdx].split(r".")[1]
        if form == 'dic':
            return
        content = self.nowFile.read(self.nowFile.namelist()[self.nowIdx])
        image = QtGui.QPixmap()

        image.loadFromData(content, form)
        image = image.scaled(self.image.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.image.setPixmap(image)

    def pre_page(self):
        if self.nowIdx == 0:
            return
        self.nowIdx -= 1
        form = self.nowFile.namelist()[self.nowIdx].split(r".")[1]
        if form == 'dic':
            return
        content = self.nowFile.read(self.nowFile.namelist()[self.nowIdx])
        image = QtGui.QPixmap()

        image.loadFromData(content, form)
        image = image.scaled(self.image.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.image.setPixmap(image)

    def delete_file(self):
        try:
            self.image.setText('none')
            self.filesTree.clearFocus()
            self.nowFile.close()
            os.remove(self.nowFileName)
        except Exception as e:
            print(e)

    def re_save(self):
        try:
            self.image.setText('none')
            self.filesTree.clearFocus()
            self.nowFile.close()
            os.renames(self.nowFileName, os.path.join(r'e:\done', self.nowFileName.split('/')[-1]))
        except Exception as e:
            print(e)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main_window = ExHentaiMain()
    main_window.show()
    sys.exit(app.exec_())
