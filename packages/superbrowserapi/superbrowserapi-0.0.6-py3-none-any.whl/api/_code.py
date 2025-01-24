import time
import os
import random
import uuid
import json
import requests
import subprocess
import platform
import psutil
import xml.etree.ElementTree as ET
import shutil
from time import sleep
import re


def is_windows():
    return platform.system() == 'Windows'


def is_mac():
    return platform.system() == 'Darwin'


def kill_all_by_names(process_names):
    processes = psutil.process_iter(['pid', 'name'])
    for process_name in process_names:
        for process in processes:
            try:
                if process_name in process.info['name'] and process.is_running():
                    process.terminate()
                    process.wait(timeout=3)
            except Exception as ex:
                print(ex)


class SuperBrowserAPI:

    def __init__(self, company, username, password):
        self.exe_path = self.get_super_browser_exe_path()
        assert company and username and password, "登录信息都是必选,请检查"
        self.user_info = {"company": company, "username": username, "password": password}
        self.socket_port=None
        # 初始化一个端口
        self.socket_port = self.get_port()

    @staticmethod
    def get_super_browser_exe_path():
        """获取紫鸟浏览器启动文件路径"""

        config_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'ShadowBot', 'ChromiumBrowser.config')

        if not os.path.exists(config_path):
            raise Exception("未安装紫鸟浏览器插件，请在影刀中安装插件")

        # 解析XML文件
        tree = ET.parse(config_path)
        root = tree.getroot()

        # 查找匹配的产品名称
        matching_nodes = root.findall(".//ChromiumBrowserInfo[ProductName='{}']".format("superbrowser"))
        if len(matching_nodes) == 0:
            raise Exception("未安装紫鸟浏览器插件，请在影刀中安装插件")
        # 提取ProcessName和ExePath
        node = matching_nodes[0]
        ProcessName, ExePath = node.find('ProcessName').text, node.find('ExePath').text
        assert ProcessName == "superbrowser", "紫鸟浏览器插件未正确安装，请检查"
        assert os.path.basename(ExePath) != "superbrowser.exe", "紫鸟浏览器插件未正确安装，请检查"
        return ExePath

    def get_port(self):
        procarr = []
        for conn in psutil.net_connections():
            if conn.raddr and conn.status == 'LISTEN':
                procarr.append(conn.laddr.port)
        # 判断当前端口是否占用,如果占用刷新端口
        if not self.socket_port or self.socket_port in procarr:
            tt = random.randint(15000, 20000)
            if tt not in procarr:
                return tt
            else:
                return self.get_port()
        else:
            return self.socket_port

    def start_exe_browser(self):
        """
        启动紫鸟客户端
        :return:
        """
        self.kill_all_super_browser()
        self.kill_all_store_process()
        cmd_text = None
        try:
            self.socket_port = self.get_port()
            cmd_text = [self.exe_path, '--run_type=web_driver', '--ipc_type=http', '--port=' + str(self.socket_port)]
            print(" ".join(cmd_text))
            subprocess.Popen(cmd_text)
            print("start ..")
            time.sleep(3)
        except Exception as e:
            print("start_ExeBrowser err...", e)
            try:
                self.socket_port = self.get_port()
                subprocess.Popen(cmd_text)
                time.sleep(3)
            except Exception as e:
                print('start browser process failed', e)
                raise Exception(f'start browser process failed {e}')

    def send_http(self, data):
        """
        通讯方式
        :param data:
        :return:
        """
        try:
            sleep(1)
            url = 'http://127.0.0.1:{}'.format(self.socket_port)
            # response = requests.post(url, json.dumps(data).encode('utf-8'), timeout=120)
            response = requests.post(url, json=data, timeout=120)
            r = json.loads(response.text)
            status_code = str(r.get("statusCode"))
            if status_code == "0":
                return r
            elif status_code == "-10003":
                raise Exception(json.dumps(r))
            else:
                raise Exception(json.dumps(r))
        except Exception as err:
            raise

    def open_store(self, store_info,
                   close_other_store=True,
                   isWebDriverReadOnlyMode=0,
                   isprivacy=0,
                   cookieTypeLoad=0,
                   cookieTypeSave=0,
                   isHeadless=False,
                   jsInfo=""):
        # 关闭其他店铺
        if close_other_store:
            self.kill_all_store_process()
        """
        打开店铺
        """
        requestId = str(uuid.uuid4())
        data = {
            "action": "startBrowser",
            "internalPluginList": "SBShopReport.zip,SBRPAEditor.zip,SBMessage.zip,SBCRM.zip,SBEcology.zip,SBHelp.zip,SBPassword.zip,SBRPA.zip,SBSems.zip,SBSetting.zip,SBShop.zip",
            "isWaitPluginUpdate": True,
            "isHeadless": isHeadless,
            "requestId": requestId,
            "isWebDriverReadOnlyMode": isWebDriverReadOnlyMode,
            "cookieTypeLoad": cookieTypeLoad,
            "cookieTypeSave": cookieTypeSave,
            "runMode": "3",
            "isLoadUserPlugin": True,
            "pluginIdType": 1,
            "privacyMode": isprivacy
        }
        data.update(self.user_info)

        data["browserId"] = store_info

        if len(str(jsInfo)) > 2:
            data["injectJsInfo"] = json.dumps(jsInfo)

        return self.send_http(data)

    def close_store(self, ziniao_shop_id):
        request_id = str(uuid.uuid4())
        data = {
            "action": "stopBrowser"
            , "requestId": request_id
            , "duplicate": 0
            , "browserOauth": ziniao_shop_id
        }
        data.update(self.user_info)

        r = self.send_http(data)
        if str(r.get("statusCode")) == "0":
            return r
        elif str(r.get("statusCode")) == "-10003":
            print(f"login Err {json.dumps(r, ensure_ascii=False)}")
        else:
            print(f"Fail {json.dumps(r, ensure_ascii=False)} ")

    def get_browser_list(self):
        requestId = str(uuid.uuid4())
        data = {
            "action": "getBrowserList",
            "requestId": requestId
        }
        data.update(self.user_info)

        r = self.send_http(data)
        return r.get("browserList")

    def get_store_name_list(self):
        browser_list = self.get_browser_list()
        store_name_list = []
        for item in browser_list:
            store_name_list.append(item.get("browserName"))
        return store_name_list

    @staticmethod
    def delete_all_cache():
        """
        删除所有店铺缓存
        非必要的，如果店铺特别多、硬盘空间不够了才要删除
        """
        if not is_windows:
            return
        local_appdata = os.getenv('LOCALAPPDATA')
        cache_path = os.path.join(local_appdata, 'SuperBrowser')
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)

    @staticmethod
    def kill_all_store_process():
        kill_all_by_names(["superbrowser"])

    @staticmethod
    def kill_all_super_browser():
        kill_all_by_names(["SuperBrowser","ziniao"])

    def get_exit(self):
        """
        关闭客户端
        :return:
        """
        data = {"action": "exit", "requestId": str(uuid.uuid4())}
        # data.update(self.user_info)
        print('@@ get_exit...' + json.dumps(data))
        self.kill_all_store_process()
        self.kill_all_super_browser()


def go_home(url, timeout=20):
    pass


def main(args):
    pass
