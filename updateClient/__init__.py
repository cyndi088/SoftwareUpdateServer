# -*- coding: utf-8 -*-
import hashlib
import sys
import pickle
from PyQt5 import QtWidgets
from urllib3 import request
from urllib import request
import os
import shutil

from updateClient.sample import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.showUpdate)
        self.pushButton_2.clicked.connect(self.updateNow)
        self.updateList = []
        self.updateServer = UpdateFiles()

    def showUpdate(self):
        self.textBrowser.clear()
        self.updateList = self.updateServer.check_update()
        for j in self.updateList:
            self.textBrowser.append(j)

    def updateNow(self):
        all_file_number = 0
        for j in self.updateList:
            self.updateServer.downloadFiles(j)
            all_file_number += 1
            vau = int((all_file_number * 100) / len(self.updateList))
            self.progressBar.setValue(vau)
            self.repaint()


class UpdateFiles(object):
    def __init__(self):
        self.server = '127.0.0.1'
        self.port = '1213'
        self.directory = os.getcwd()
        self.client = '/updateFiles/'

    def downloadFiles(self, key):
        checkurl = 'http://' + self.server + ':' + self.port
        file_dir = self.directory + self.client + key
        if os.path.exists(file_dir):
            os.remove(file_dir)
            request.urlretrieve(checkurl + '/' + key, file_dir)
        else:

            newpath = '/'.join(file_dir.split('/')[:-1:])
            print('+++++++++++++++++++++++++')
            print(file_dir)
            print(newpath)
            print('+++++++++++++++++++++++++')

            try:
                if not os.path.isdir(newpath):
                    os.makedirs(newpath)
                request.urlretrieve(checkurl + '/' + key, file_dir)
            except Exception as e:
                print('eeeeeeeeeeeeeeeeeeeee')
                print(e)
                print('eeeeeeeeeeeeeeeeeeeee')
                request.urlretrieve(checkurl + '/' + key, file_dir)

    def get_file_md5(self, filename):
        if not os.path.isfile(filename):
            return
        myHash = hashlib.md5()
        f = open(filename, 'rb')
        while True:
            b = f.read(8096)
            if not b:
                break
            myHash.update(b)
        f.close()
        return myHash.hexdigest()

    def clear_up(self):
        delDir = self.directory + self.client
        if not os.path.exists(delDir):
            return
        delList = os.listdir(delDir)
        for f in delList:
            filePath = os.path.join(delDir, f)
            if os.path.isfile(filePath):
                os.remove(filePath)
            elif os.path.isdir(filePath):
                shutil.rmtree(filePath, True)

    def check_update(self):
        self.clear_up()
        updateList = []
        checkurl = 'http://' + self.server + ':' + self.port
        request.urlretrieve(checkurl + '/.listFile', ".listFile")

        with open(".listFile", "rb") as f:
            data = pickle.load(f)
        num = 1
        for key in data:
            # 服务端文件的md5
            print('*' * num)
            print(key)
            server_md5 = data[key]
            client_file_dir = self.directory + self.client + key
            # 如果文件存在于客户端
            if os.path.exists(client_file_dir):
                # 客户端文件的md5
                client_md5 = self.get_file_md5(client_file_dir)
                # 判断客户端与服务器是否一致
                if client_md5 != server_md5:
                    print(server_md5, ".listFile不一致，需要准备下载")
                    # 若不一致则加入updateList
                    updateList.append(key)
            else:
                # 如果文件不存在于客户端
                updateList.append(key)
                print('准备下载', client_file_dir)
            print('*' * num)
            num += 1
        return updateList


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
