# -*- coding: utf-8 -*-
import os
import uuid
import json
import pickle
import hashlib
from flask import request, jsonify, send_from_directory, abort, Flask


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# 服务器ip和端口
server_ip = '127.0.0.1'
server_port = 1213

allfile = []
md5_list = []
updateList = {}
directory = os.getcwd()


# 向服务器定时请求，获取更新地址和版本号
def get_version():  # TODO
    pass

# 下载文件服务
@app.route("/<path:filename>", methods=['GET'])
def download(filename):
    if request.method == "GET":
        if os.path.isfile(os.path.join('updateFiles', filename)):
            return send_from_directory(directory + '/updateFiles/', filename, mimetype='application/octet-stream',
                                       as_attachment=False)
        abort(404)


# 获取本地mac地址
def get_mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    mac_addr = ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
    return mac_addr


# 计算文件MD5
def get_file_md5(filename):
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


# 计算生成新的清单文件
@app.route("/generateNewConfig", methods=['GET'])
def generate():
    findFile(directory + '/updateFiles/')
    file_md5_list = json.dumps(updateList)
    print(file_md5_list)
    with open('./updateFiles/.listFile', 'wb') as f:
        pickle.dump(updateList, f)
    return_data = {
        'Statu': 'success',
    }
    updateList.clear()
    return jsonify(return_data)
    # file_md5_list=json.load(updateList)


# 找到更新文件目录里面的文件以及文件夹、递归寻找
def findFile(path):
    fsinfo = os.listdir(path)
    for fn in fsinfo:
        temp_path = os.path.join(path, fn)
        # 如果该路径不是目录（即文件），则加入updateList
        if not os.path.isdir(temp_path):
            print('文件路径: {}'.format(temp_path))
            # 获取文件的md5
            fm = get_file_md5(temp_path)
            print(fn)
            # 获取文件的文件名
            fn = temp_path.replace(directory + "/updateFiles/", '')
            updateList[fn] = fm
        # 如果该路径是目录，则递归寻找
        else:
            findFile(temp_path)


# 检查更新版本，该部分尚未够，完善。可以考虑为管理员远程上传文件的时候
# 将更新说明以json格式一同上传到服务器中，更新时直接读取即可
@app.route("/checkUpdate", methods=['GET'])
def check():
    if request.method == "GET":
        return_data = {
            'Version': '0.0.1',
            'Msg': '更新文件，修复初始化卡顿bug，增加文件预下载功能',
        }
        return jsonify(return_data)


# 首页Hello
@app.route("/", methods=['GET'])
def hello():
    if request.method == "GET":
        return "Hello I'm Client"


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1314, debug=True)  # 运行，指定监听地址为 127.0.0.1:1314
