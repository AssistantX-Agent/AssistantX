import threading
import socket

# from scapy.all import *
import json
import urllib.parse
import qrcode
# from common import global_var
from datetime import datetime, timedelta
from PIL import ImageDraw, ImageFont, Image
import base64
import random
# door_magnetic_value = 0

# 服务器和机器人IP和端口
ROBOT_IP = '192.168.1.105'
ROBOT_PORT = 8888

# def send_locker():
#     # 创建客户端 socket
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
#         client_socket.connect((ROBOT_IP, ROBOT_PORT))
#         print("连接到机器人端")
#         message = "get_locker_process_packet"
#         try:
#             # 发送组合后的消息
#             client_socket.sendall(message.encode())
#             print(f"发送指令: {message}")
#             data = client_socket.recv(1024)
#             door_magnetic_value = int.from_bytes(data, byteorder='big')
#             print(f"接收到门锁状态: {door_magnetic_value}")
#             return door_magnetic_value
#         except Exception as e:
#             print(f"发送指令失败: {e}")

# # 回调函数
# def process_packet(packet):
#     """
#     sniff回调函数
#     :param packet: 捕获的包数据sniff
#     """
#     if packet.haslayer(Raw):
#         # 检查TCP包含HTTP
#         data = str(packet[Raw].load, "utf-8")
#         if "/iscs/QueryCmd" in data:
#             # 提取POST数据
#             headers, post_data = data.split("\r\n\r\n")
#             parameters = {}
#             for line in post_data.split("&"):
#                 key, value = line.split("=")
#                 parameters[key] = urllib.parse.unquote(value)  # 解码URL编码的值
#             # 转换为JSON字符串
#             json_string = json.dumps(parameters, indent=2)
#             # 去掉JSON字符串中的转义字符
#             json_data = json.loads(json_string)
#             # print("Captured JSON data:", json_data)
#             json_data = json.loads(json_data['paramaters'])
#             # 提取参数部分的JSON字符串
#             # print(json_data)
#             global_var.door_magnetic_value = int(json_data.get('DoorMagnetic', '0'))
#             # print(door_magnetic_value)

# 开始捕获数据包
# def ocSelect(person_name, item=''):
#     """
#     捕获文件取走信号
#     :return:
#     """
#     door_opened = False
#     start_time = time.time()
#     # print(global_var.locker_flag)
#     while global_var.locker_flag:
#         global_var.door_magnetic_value = send_locker()
#         #sniff(iface="enp89s0", filter="tcp and port 80 and src host 192.168.9.218", prn=process_packet, store=0, count=0, timeout=0.5)
#         if global_var.door_magnetic_value == 1 and not door_opened:
#             door_opened = True
#             # print("当前状态：门已打开")
#         if door_opened and global_var.door_magnetic_value == 0:
#             # print("当前状态：门已关闭")
#             door_opened = False
#             end_one_time = datetime.now()  # 获取等待的时间
#             time_end_str = end_one_time.strftime("%H:%M")
#             global_var.locker_info += str(f"At {time_end_str}, {person_name} have scanned the QR code and complete the operation of {item}; {person_name} has done what you asked {person_name} to do in {person_name}'s location.\n")
#             # print(global_var.locker_info)
#             global_var.locker_flag = False

# threading.Thread(target=ocSelect('lyc')).start()
# print('aaaaa')
# print(1111)
# locker = Loker('person_name')
# print(22222)
# global_var.locker_flag = True
# locker.start()
# print(3333)
# while True:
#     if global_var.locker_info != '':
#         print(global_var.locker_info)


#rc4编码
def rc4_crypt(key, data):
    """
    加密方法
    :param key: 密钥，
    :param data: 加密数据，
    :return:
    """
    S = list(range(256))
    j = 0
    out = []

    # KSA (Key Scheduling Algorithm)
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]

    # PRGA (Pseudo-Random Generation Algorithm)
    i = j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(chr(ord(char) ^ S[(S[i] + S[j]) % 256]))

    return ''.join(out).encode('latin-1').hex()

# 生成锁二维码
def generate_encrypted_qrcode(itme_name):
    """
    生成二维码图片
    图片名称：encrypted_qrcode.png
    return:图片名
    """
    # 获取当前时间和2分钟后的时间
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    # print(current_time)
    future_time = (datetime.now() + timedelta(minutes=3600)).strftime("%Y%m%d%H%M%S")
    # print(future_time)

    # 用户提供的数据




    data = ["17860390991", "V123", current_time, future_time, random.randint(100000, 999999), 1, ""]


    data_str = '[' + ','.join(map(str, data)) + ']'  # 加上方括号
    # print(data_str)
    encryption_key = b"CB1712345678"  # 注意这里是字节串
    # RC4加密
    encrypted_data = rc4_crypt(encryption_key, data_str)
    # 在加密字符串前面增加CB01
    total_encrypted_string = "CB01" + encrypted_data
    # print(total_encrypted_string)
    # 生成二维码
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=15,
    )
    qr.add_data(total_encrypted_string)
    qr.make(fit=True)
    # 创建Image对象
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.convert('RGBA')
    # 在图片上添加说明文字

    # 计算文本宽度和高度
    # text = f"{str(itme_name)}"  # 注意这里变量名应该是item_name而不是itme_name


    draw = ImageDraw.Draw(img)

    # font = ImageFont.truetype("NotoSansCJK-Regular.ttc", 16)
    # bbox = draw.textbbox((0, 0),itme_name, font=font)
    # width = bbox[2] - bbox[0]
    # height = bbox[3] - bbox[1]
    # print(bbox)
    # img_width, img_height = img.size
    # x = (img_width - width) / 2
    # y = (img_height - height) / 10
    # draw.text((x, y), f"{str(itme_name)}", fill='red', font=font,align='center')
    # # draw.text((0,40),"如无反应，请调整间距和位置多尝试几次", fill='red', font=font,align='left')

    # 生成文件名
    filename = "encrypted_qrcode1.png"
    # 保存二维码图片
    img.save(filename)
    return filename
generate_encrypted_qrcode("erwei")
# generate_encrypted_qrcode("Pleas.")
# generate_encrypted_qrcode("douctime")
# if __name__ == '__main__':
#     # generate_encrypted_qrcode()
#     a = ocSelect()
#     print(a)
# print(a)
# sniff(filter="tcp and port 80 and host 183.173.71.4", prn=process_packet)
# def img_encode(path = 'encrypted_qrcode.png', itme_name=''):
#     generate_encrypted_qrcode(itme_name)
#     image = open(path, 'rb')
#     base64_image = base64.b64encode(image.read()).decode()
#     image.close()
#     return base64_image
#
# img_encode()

# Given encrypted data and RC4 encryption key, let's decrypt the data using the provided RC4crypt function.
# First, we need to remove the "CB01" prefix from the encrypted data.

# encrypted_data_hex = "CB015a3bf022ab2458905d48e67ff74dede572cb6c7031ce33a5a4e94ef0f8d22501f3a1937d862a4040cceb83be3b3b"
# # encrypted_data_hex = "CB0105f442bb7734a14db7ec24859b6582a62722e1843a3e329f90caef0abb5522cf0aba338a02c3f78bb48f0c7b1016bc0e"
# encrypted_data_hex = "CB0105f442bb7734a14db7ec24859b6582a62722e1843a3e339491c7ec0dba5124c00aba328105c2fc89b18f0f7f1210b37feb62c3d8bdb96cf70b77b2"
# encryption_key = b"CB1712345678"
# encryption_key = b"CB1712345678"
#
# # Remove the "CB01" prefix
# encrypted_data_hex = encrypted_data_hex[4:]
#
# # Convert hex string to bytes
# encrypted_data = bytes.fromhex(encrypted_data_hex)
#
# # RC4 decryption function (which is the same as encryption function)
# def rc4crypt(key, data):
#     S = list(range(256))
#     j = 0
#     out = []
#
#     # KSA (Key Scheduling Algorithm)
#     for i in range(256):
#         j = (j + S[i] + key[i % len(key)]) % 256
#         S[i], S[j] = S[j], S[i]
#
#     # PRGA (Pseudo-Random Generation Algorithm)
#     i = j = 0
#     for char in data:
#         i = (i + 1) % 256
#         j = (j + S[i]) % 256
#         S[i], S[j] = S[j], S[i]
#         out.append(chr(char ^ S[(S[i] + S[j]) % 256]))
#
#     return ''.join(out)
#
# # Decrypt the data
# decrypted_data = rc4crypt(encryption_key, encrypted_data)
# print(decrypted_data)
