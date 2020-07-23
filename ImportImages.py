import os
from pathlib import Path
import datetime
import shutil
import json
import re

base_path = ''
movePath = 'Assets.xcassets/'
nowtime = ''
newFilePath = ''

 
def timestamp2datetime(timestamp, convert_to_local=True, utc=8, is_remove_ms=True):
    if is_remove_ms:
        timestamp = int(timestamp)
    dt = datetime.datetime.utcfromtimestamp(timestamp)
    if convert_to_local:
        dt = dt + datetime.timedelta(hours=utc)
    return dt


def convert_date(timestamp, format='%Y-%m-%d'):
    dt = timestamp2datetime(timestamp)
    return dt.strftime(format)


def compare_time(startTime, endTime):
    date1 = datetime.datetime.strptime(startTime, '%Y-%m-%d').date()
    date2 = datetime.datetime.strptime(endTime, '%Y-%m-%d').date()

    return date1 > date2


if __name__ == "__main__":

    while len(base_path) <= 0:
        base_path = input("输入你资源路径:")
        # 判断路径是否存在
        if not os.path.exists(base_path):
            print('资源路径不存在 请重新输入！')
            base_path = ''
    while len(nowtime) <= 0:
        nowtime = input("输入要更新的时间 2020-0X-XX格式:")
    while len(newFilePath) <= 0:
        newFilePath = input("输入文件夹名称:")

    # 判断目标目录是否存在一样目录
    isCover = ''
    if os.path.exists(movePath + newFilePath):
        isCover = input("已存在相同文件夹名称是否覆盖(y/n/z(追加)):")
        if isCover == 'y':
            shutil.rmtree(movePath + newFilePath)

        elif isCover == 'n':
            newFilePath = newFilePath + '-1'

    pathAry = Path(base_path)

    # 创建一个新文件夹 来保存这些新增的图片
    newFilePath1 = './' + newFilePath
    p = Path(newFilePath1)
    p.mkdir(exist_ok=True)

    for entry in pathAry.iterdir():
        if entry.is_file():
            info = entry.stat()
            # 判断资源是否是图片类型不是图片类型丢弃
            pattern = re.compile(r"(.jpg|.png|.jpeg)$", re.I)
            m = pattern.match(entry.suffix)
            if not m:
                continue
            fileTime = convert_date(info.st_mtime)
            isBig = compare_time(nowtime, fileTime)
            if not isBig:
                print(nowtime + ' 之后新加的图片 ' + entry.name)

                shutil.copy2(base_path + '/' + entry.name, newFilePath)

    # 1.图片遍历相同文件 合成一个文件夹 .imageset 并生成 Contents.json 文件
    newPathAry = Path(newFilePath)

    for entry in newPathAry.iterdir():
        if entry.is_file():
            strAry = entry.name.split('@')
            nameStr = strAry[0]

            for entry2 in newPathAry.iterdir():
                if nameStr in entry2.name:
                    p = Path(newFilePath + '/' + nameStr + '.imageset')
                    p2 = Path(newFilePath + '/' + nameStr + '.imageset/' + 'Contents.json')
                    p.mkdir(exist_ok=True)
                    shutil.move(newFilePath + '/' + entry.name, p)
                    with open(p2, 'w') as f:
                        data = {
                            "images": [
                                {
                                    "idiom": "universal",
                                    "scale": "1x"
                                },
                                {
                                    "idiom": "universal",
                                    "filename": nameStr + "@2x.png",
                                    "scale": "2x"
                                },
                                {
                                    "idiom": "universal",
                                    "filename": nameStr + "@3x.png",
                                    "scale": "3x"
                                }
                            ],
                            "info": {
                                "version": 1,
                                "author": "xcode"
                            }
                        }
                        jsObj = json.dumps(data)
                        f.write(jsObj)
                        f.close()

                    break

    if isCover == 'z':
        for entry in newPathAry.iterdir():

            if not os.path.exists(movePath + newFilePath + '/' + entry.name):
                shutil.move(newFilePath + '/' + entry.name, movePath + newFilePath)

        shutil.rmtree(newFilePath1)
    else:
        # 移动文件图片到xcode项目里（移动到Assets）
        shutil.move(newFilePath, movePath)
