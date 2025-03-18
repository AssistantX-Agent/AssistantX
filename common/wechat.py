import socketio
import requests
from bs4 import BeautifulSoup
import cv2 as cv
import numpy as np
from pyzbar import pyzbar as pyzbar
import qrcode_terminal
import six
from pilk import *
import websockets
import asyncio
import json
import logging
import random
import threading
import time
import base64
import cv2
from common.andro_operation import juge_open_wechat

class WechatMessage(object):
    """微信message类"""

    def __init__(self,
                 FromUserName: str = None,
                 ToUserName: str = None,
                 MsgType: int = None,
                 Content: str = None,
                 ActionUserName: str = None,
                 PushContent: str = None,
                 ActionNickName: str = None):
        """微信message类

        :param:
        :param FromUserName: 消息来源
        :param ToUserName: 消息去处
        :param MsgType: 消息类型，1为文本消息
        :param Content: 消息内容
        :param ActionUserName: 群聊中会有，其他为空
        :param PushContent: 推送的消息(手机弹窗时的消息提示)
        :param ActionNickName: 备注名
        """
        self.FromUserName = FromUserName
        self.ToUserName = ToUserName
        self.Content = Content
        self.ActionUserName = ActionUserName
        self.MsgType = MsgType
        self.PushContent = PushContent
        self.ActionNickName = ActionNickName

    @classmethod
    def FromMessage(cls, message: json):
        wechatmessage = WechatMessage()
        for (key, value) in six.iteritems(message):
            wechatmessage.__dict__[key] = value
        return wechatmessage

class UserContext:
    """上下文context类"""
    def __init__(self,
                 user: str = None,
                 messages: str = None,
                 working=False):
        self.user = user
        self.user_messages = messages
        self.working = working
#
#     def display_info(self):
#         print("VX ID:", self.vx_id)
#         print("Working:", self.working)
#         for message in self.user_messages:
#             print("Role:", message["role"])
#             print("Content:", message["content"])
#
# # 使用示例
# if __name__ == "__main__":
#     # 创建一个微信上下文对象
#     user_messages = [
#         {"role": "user", "content": "aaa"},
#         {"role": "assistant", "content": "bbb"}
#     ]
#     user_context = UserContext(vx_id="789abc", user_messages=user_messages, working=True)
#
#     # 显示上下文信息
#     user_context.display_info()

class WechatServer:
    def __init__(self, wx_id: str, func_on_msgs, func_on_event, url: str = 'http://127.0.0.1:8898'  # 192.168.31.131:9502  81.70.197.166:8898 #82.156.146.74:8898
):
        """指定账号登陆
        :param:
        :param wx_id: 要登陆的微信号
        :param url: 服务器服务地址
        """
        self.url = url
        self.sio = socketio.Client(logger=False, engineio_logger=False)
        self.current_wx_id = wx_id
        requests.adapters.DEFAULT_RETRIES = 5
        self.s = requests.session()
        self.s.keep_alive = False
        self.func_on_msgs = func_on_msgs
        self.func_on_event = func_on_event
        self.wx_name = None
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger("WechatSever")
        self.logger.info('Everything Is OK!!')

        def OnWeChatMsgs(message):
            """
            接受到消息时触发

            :param message:
            :return:
            """

            if 'CurrentPacket' in message:
                if 'Data' in message['CurrentPacket']:
                    message = message['CurrentPacket']['Data']
            if message['ToUserName'] == self.current_wx_id:
                if 'MsgType' in message:
                    # 文本消息
                    if message['MsgType'] == 1 or message['MsgType'] == 34 or message['MsgType'] == 49:
                        # 消息来源他人
                        if message['FromUserName'] != self.current_wx_id:
                            # 来自群聊的消息
                            if message['FromUserName'][-9:] == '@chatroom':
                                if message['MsgType'] == 34:
                                    self.logger.info('message from chatroom:{},content:{}'.format(message['FromUserName'],
                                                                                              message['Content']))
                            # 来自个人的消息
                            else:
                                if message['MsgType'] == 34:
                                    self.logger.info('message from individual:{},content:{}'.format(message['FromUserName'],
                                                                                                message['Content']))
                            wechat_message = WechatMessage.FromMessage(message)
                            self.func_on_msgs(self, wechat_message)
                        # 消息来源自己
                        else:
                            if message['MsgType'] == 34:
                                print('send message to:{},content:{}'.format(message['ToUserName'], message['Content']))

        def OnWeChatEvents(message):
            """
            事件触发
            :param message:
            :return: None
            """
            print("*" * 30, "OnWeChatEvents", "*" * 30)
            print(message)

        async def Wsdemo():
            url = "127.0.0.1:8898"
            uri = "ws://{}/ws".format(url)
            while True:
                try:
                    async with websockets.connect(uri, ping_interval=None) as websocket:
                        while True:
                            greeting = await websocket.recv()
                            EventJson = json.loads(greeting)
                            EventName = EventJson["CurrentPacket"]["Data"]["EventName"]
                            # print(EventJson["CurrentPacket"]["Data"]["AddMsg"])
                            OnWeChatMsgs(EventJson["CurrentPacket"]["Data"]["AddMsg"])
                            # print(f"<{EventName} {greeting}")
                except Exception as e:
                    # 断线重连
                    t = random.randint(5, 7)
                    await asyncio.sleep(1)
                    await Wsdemo()


        def thread_job():
            asyncio.run(Wsdemo())

        add_thread = threading.Thread(target=thread_job)
        add_thread.start()

        try:
            if self.Is_Offline():
                self, logging.warning("检测到指定的微信账号未在给定的服务器中登陆，尝试历史登陆.....")
                if self.History_Login():
                    self.logger.warning("历史登陆失败，尝试扫码登陆....")
                    self.GetQRcode()
                else:
                    self.logger.info("已成功请求历史登陆，请在主设备上确认")
        except requests.exceptions.ConnectionError:
            self.logger.error("未检测到服务器端口的回复，请检测服务器上的服务是否部署,5秒中后尝试重新连接")
            time.sleep(5)

    def History_Login(self) -> str:
        """
        历史登陆该微信

        :return:None
        """
        url = self.url + '/v2/login/push'
        payload = {'wxid': self.current_wx_id}
        res = self.s.get(url, params=payload)
        print("测试" + res.text)
        # if res.json()['ErrMsg'] == 'err':
        #     return 'err'
        # else:
        #     return None

    def GetQRcode(self) -> None:
        """获取该微信号的登陆二维码

        :return: None
        """
        url = self.url + '/v2/login/getqrcode'
        payload = {
            'isIPad': 2,
            'wxid': self.current_wx_id
        }
        res = self.s.get(url, params=payload)
        base64qrcode = BeautifulSoup(res.text,"html.parser").img['src'].split(",")[1]
        print(base64qrcode)
        image = base64.b64decode(base64qrcode)
        image = np.frombuffer(image, np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        barcodes = pyzbar.decode(image)
        for barcode in barcodes:
            # 提取二维码的边界框的位置
            # 画出图像中条形码的边界框
            (x, y, w, h) = barcode.rect
            cv.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # 提取二维码数据为字节对象，所以如果我们想在输出图像上
            # 画出来，就需要先将它转换成字符串
            barcodeData = barcode.data.decode("UTF8")
            barcodeType = barcode.type

            # 绘出图像上条形码的数据和条形码类型
            text = "{} ({})".format(barcodeData, barcodeType)
            cv.putText(image, text, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, .5, (0, 0, 125), 2)
            # 向终端打印条形码数据和条形码类型
            print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
            print("请用微信扫描以下二维码，登陆微信")
            qrcode_terminal.draw(barcodeData)

    def Is_Offline(self) -> bool:
        """
        查看微信号是否在线，在线返回False，不在线返回True

        :return: bool
        """
        url = self.url + '/v2/wechatinfo'
        payload = None
        res = self.s.get(url, params=payload).text
        WechatUsers = json.loads(res)
        for WechatUser in WechatUsers['ResponseData']['WeChatUsers']:
            if self.current_wx_id[:-4] + '****' == WechatUser['Wxid']:
                self.wx_name = WechatUser['NickName']
                return False
        return True

    def Say(self, to_user_name: str, content: str, at_users: str = None) -> None:
        """发送文本消息

        :param to_user_name:要发送消息的联系人的wx_id
        :param content:要发送消息的文本内容
        :param at_users:需要@的用户，仅在群聊中有效，必须是默认用户名(message中的‘ActionNickName’)
        :return:None
        """
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        # url = "/v2/api?funcname=MagicCgi&timeout=10&wxid=" + self.current_wx_id
        url = self.url + '/v2/api?funcname=MagicCgi&timeout=10&wxid=' + self.current_wx_id
        if at_users is None:
            at_users = ""
        payload = json.dumps({
            "CgiCmd": 522,
            "CgiRequest": {
                "ToUserName": to_user_name,
                "Content": content,
                "MsgType": 1,
                "AtUsers": at_users
            }
        })
        res = requests.request('post', url, data=payload, headers=headers)
        self.logger.info("send message to {}:{}".format(to_user_name, content))

    def SayImage(self, to_user_name: str, base64_image: str) -> None:
        """
        发送图片
        :param to_user_name:
        :param base64_image:
        :return:
        """
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        url = self.url + '/v2/api?funcname=MagicCgi&timeout=10&wxid=' + self.current_wx_id
        payload = json.dumps({
                    "CgiCmd": 110,
                    "CgiRequest": {
                        "ToUserName": to_user_name,
                        "ImageBase64": base64_image
                    }
                })
        res = requests.request('post', url, data=payload, headers=headers)
        print(res.text)

    # 发送朋友圈
    def Sendsns(self, text):
        url = self.url + '/v2/api?funcname=MagicCgi&timeout=10&wxid=' + self.current_wx_id
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        payload = json.dumps({
            "CgiCmd": 209,
            "CgiRequest": {"XmlContent": "<TimelineObject><id><![CDATA[14368174633416724995]]></id><username><![CDATA[{}]]></username><createTime><![CDATA[1712819890]]></createTime><contentDescShowType>0</contentDescShowType><contentDescScene>0</contentDescScene><private><![CDATA[0]]></private><contentDesc><![CDATA[{}]]></contentDesc><contentattr><![CDATA[0]]></contentattr><sourceUserName></sourceUserName><sourceNickName></sourceNickName><statisticsData></statisticsData><weappInfo><appUserName></appUserName><pagePath></pagePath><version><![CDATA[0]]></version><isHidden>0</isHidden><debugMode><![CDATA[0]]></debugMode><shareActionId></shareActionId><isGame><![CDATA[0]]></isGame><messageExtraData></messageExtraData><subType><![CDATA[0]]></subType><preloadResources></preloadResources></weappInfo><canvasInfoXml></canvasInfoXml><ContentObject><contentStyle><![CDATA[2]]></contentStyle><contentSubStyle><![CDATA[0]]></contentSubStyle><title></title><description></description><contentUrl></contentUrl></ContentObject><actionInfo><appMsg><mediaTagName></mediaTagName><messageExt></messageExt><messageAction></messageAction></appMsg></actionInfo><appInfo><id></id></appInfo><location poiClassifyId=\"\" poiName=\"\" poiAddress=\"\" poiClassifyType=\"0\" city=\"\"></location><publicUserName></publicUserName><streamvideo><streamvideourl></streamvideourl><streamvideothumburl></streamvideothumburl><streamvideoweburl></streamvideoweburl></streamvideo></TimelineObject>".format(
                self.current_wx_id, text)
            }
        })
        res = requests.request('post', url, data=payload, headers=headers)
        print(res.text)


    #上传视频号
    def UpVideo(self, videoPath, imgPath):

        url = self.url + '/v2/cdnupload?wxid=' + self.current_wx_id
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        payload = json.dumps({
                    "CgiCmd": 0,
                    "CgiRequest": {
                        "FileType": 0,
                        "VideoPath": videoPath,
                        "ImagePath": imgPath
                    }
                })
        # print(payload)
        res = requests.request('post', url, data=payload, headers=headers)
        print(res.text)

    # 下载语音消息到工控机
    def DownVoice(self, xml, msgid):
        url = self.url + '/v2/cdndownload?funcname=MagicCgi&timeout=10&wxid=' + self.current_wx_id
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        # url = url = self.url + '/v2/api?funcname=DownloadVoice&timeout=10&wxid=' + self.current_wx_id
        payload = json.dumps({
            "CgiCmd": 0,
            "CgiRequest": {
                "VoiceXml": xml,
                "FileName": "/home/wx/RSTBot2/Voice/{}.silk".format(msgid),
                "FileType": 128,
                "MsgId": msgid
            }
        })

        res = requests.request('post', url, data=payload, headers=headers)
        print(res.text)

    # 语音下载到本地
    def upload_voice(self, msgid):
        url = 'http://127.0.0.1:4801/{}.silk'.format(msgid)  # Flask 服务器的地址
        destination = './voice/{}.silk'.format(msgid)  # 下载到的本地路径

        response = requests.get(url)
        if response.status_code == 200:
            with open(destination, 'wb') as f:
                f.write(response.content)
            print('文件下载成功！')
        else:
            print('文件下载失败:', response.status_code)

    # Voice to text:标贝智能语音
    def voice_to_text(self, msgid, client_secret="af099b38c15d421a9dd417d710ddaf49",
                      client_id="6f3aaa46970741c3b3c2e7f13f52883a", ):
        # 微信语音转wav
        silk_file = './voice/{}.silk'.format(msgid)
        wav_file = './voice/{}.wav'.format(msgid)
        silk_to_wav(silk_file, wav_file)

        # 读取音频文件
        with open(wav_file, 'rb') as f:
            file = f.read()

        # 获取鉴权信息
        grant_type = "client_credentials"
        url = "https://openapi.data-baker.com/oauth/2.0/token?grant_type={}&client_secret={}&client_id={}".format(
            grant_type, client_secret, client_id)

        try:
            response = requests.post(url)
            response.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            access_token = json.loads(response.text).get('access_token')

        # 填写Header信息
        audio_format = 'wav'
        sample_rate = '16000'
        add_pct = 'true'
        hotwordid = '5ad23faa08664ce1b853bff4aa4686c8'
        headers = {'access_token': access_token, 'audio_format': audio_format, 'sample_rate': sample_rate,
                   'add_pct': add_pct, 'hotwordid': hotwordid}
        # 模型封装
        url = "https://asr.data-baker.com/asr/api?"
        response = requests.post(url, data=file, headers=headers)
        code = json.loads(response.text).get("code")
        text = json.loads(response.text).get("text")
        if code != 20000:
            print(response.text)

        print("语音文本:" + str(text))
        # global_var.voice_message = text

    def sysn(self):
        url = self.url + '/v2/api?funcname=MagicCgi&timeout=10&wxid=' + self.current_wx_id
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        post_json = {"CgiCmd": 1000000005,
                      "CgiRequest":
                          {
                              "UseSync": True
                          }
                      }
        print(str(post_json))
        res = requests.request('post', url, json=post_json, headers=headers)
        print(res.text)

def onevent(wechatserver: WechatServer, event: json):
    pass
    # print('onevent')
# 微信消息处理
def onmessage(wechatserver: WechatServer, message: WechatMessage):
    task_value = {}
    # 来自群的消息
    if message.FromUserName[-9:] == '@chatroom':
        # 在群中被@的消息
        #  获取说话人名字
        # global_var.speaker == ''
        if '@' + wechatserver.wx_name in message.Content:
            if message.ActionNickName == '':
                speaker = message.PushContent[:-7]
            else:
                speaker = message.ActionNickName

            task_value['指令下发者'] = speaker
        else:
            pass
    # 来自个人的消息
    else:
        if message.ActionNickName == '':
            speaker = message.PushContent[:-7]
        else:
            speaker = message.ActionNickName
        task_value['指令下发者'] = speaker
        # @分离信息
        # content_after_bot = message.Content[len("@WechatBot1"):].strip()
        # 获取全部信息
        # user_received_message = speaker + ": " + str(message.Content)
        # juge_open_wechat(speaker)

from common.LockApi import img_encode

def main():
    print()
    # wxid_6upszurr9wlv12 dabai
    # wxid_517djxubg7rz22 履带车
    # wxid_lgqt76ellkpq12  car
    # dmf17801233376
    # wechatserver = WechatServer('wxid_lgqt76ellkpq12', onmessage, onevent)
    # time.sleep(2)
    # wechatserver.Say("wxid_5n9weu087l1222", "I have the takeaway of beef noodles.")
    # time.sleep(2)
    # wechatserver.SayImage("wxid_5n9weu087l1222", img_encode(itme_name="beef noodles"))

if __name__ == '__main__':
    main()
