#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2024/8/9 10:35
# @Author : Yongchang
import uiautomator2 as u2
import subprocess
import time

def open_wechat(adb_path):
    command = f"adb shell am start -n com.tencent.mm/.ui.LauncherUI"
    subprocess.run(command, capture_output=True, text=True, shell=True)

def open_meituan(adb_path):
    d = u2.connect()
    d.app_start("com.sankuai.meituan")

def open_xiecheng(text):
    print(text)
    d = u2.connect()
    d.app_stop("ctrip.android.view")
    d.app_start("ctrip.android.view")
    d.xpath("//*[@content-desc='搜索']").click()
    # time.sleep(1)
    d.send_keys(str(text))
    time.sleep(1)
    d.xpath("//*[@text='搜索']").click()

def open_didi(source_location, target_location):
    # print(text)
    d = u2.connect()
    d.app_stop("com.sdu.didi.psnger")
    d.app_start("com.sdu.didi.psnger")
    d(resourceId="com.sdu.didi.psnger:id/tv_text").click()
    d.send_keys(source_location)
    time.sleep(1)
    d.xpath("//*[@text='附近']").click()
    d(resourceId="com.sdu.didi.psnger:id/to_poi_text_view").click()
    time.sleep(1)
    d.send_keys(target_location)
    time.sleep(1)
    d.xpath("//*[@resource-id='com.sdu.didi.psnger:id/sweep_view']").click()

# def Forward_file_on_Wechat(source_contact, target_contact):
#     # source_contact  源目标
#     # target_contact  转发目标
#     it = 0
#     while it <= 2:
#         try:
#             d = u2.connect()
#             juge_open_wechat(source_contact)
#             # 等待微信启动
#             # d.app_stop('com.tencent.mm')
#             # d.app_start('com.tencent.mm')
#             # 打开源微信账号的聊天界面
#             # d(text=source_contact).click()
#
#             # 假设文件消息有一个特定的resource-id，这里用"com.tencent.mm:id/bju"代替
#             # 选择最新的文件消息，这里我们尝试选择最后一个出现的
#             # 注意：这需要根据你的实际界面布局来调整
#             file_messages = d(resourceId="com.tencent.mm:id/bju")
#             if file_messages.count > 0:
#                 # 选择最后一个文件消息
#                 latest_file_message = file_messages[-1]
#
#                 # 长按文件进行转发
#                 latest_file_message.long_click()
#
#                 # 选择转发
#                 d.xpath("//*[@text='Forward']").click()
#
#                 # 选择通过微信转发
#                 d.xpath("//*[@text='Search']").click()
#                 time.sleep(1)
#                 d.send_keys(target_contact)
#                 # 选择目标微信账号
#                 d(text=target_contact).click()
#                 # 确认转发
#                 d.xpath("//*[@text='Send']").click()
#             else:
#                 # 选择最后一个文件消息
#                 # latest_file_message = file_messages
#
#                 # 长按文件进行转发
#                 d(resourceId="com.tencent.mm:id/bju").long_click()
#
#                 # 选择转发
#                 d.xpath("//*[@text='Forward']").click()
#
#                 # 选择通过微信转发
#                 d.xpath("//*[@text='Search']").click()
#                 time.sleep(1)
#                 d.send_keys(target_contact)
#                 # 选择目标微信账号
#                 d(text=target_contact).click()
#                 # 确认转发
#                 d.xpath("//*[@text='Send']").click()
#                 # print("未找到文件类型的消息")
#             time.sleep(4)
#             juge_open_wechat(target_contact)
#             return f"Successful forwarding of electronic files from {source_contact} to {target_contact}"
#         except Exception as e:
#             it += 1
#     return f"Failure to forward electronic files from {source_contact} to {target_contact}"

def Forward_file_on_Wechat(source_contact, target_contact):
    # source_contact  源目标
    # target_contact  转发目标
    it = 0
    return f"Successful forwarding of electronic files from {source_contact} to {target_contact}"



def skipp_wechat_interface(contact):
    d = u2.connect()
    d.app_stop('com.tencent.mm')
    d.app_start('com.tencent.mm')
    d(text=contact).click()

def talk_to_someone(contact, text):

    d = u2.connect()
    d.app_stop('com.tencent.mm')
    d.app_start('com.tencent.mm')
    d(text=contact).click()
    d(resourceId="com.tencent.mm:id/o4q").click()
    time.sleep(2)
    d.send_keys(text)
    d(resourceId="com.tencent.mm:id/bql").click()

def send_message(text):

    d = u2.connect()
    d(resourceId="com.tencent.mm:id/o4q").click()
    d.send_keys(text)
    d(resourceId="com.tencent.mm:id/bql").click()

def search_food(text):
    d = u2.connect()
    d.app_start("com.sankuai.meituan")
    d(description="外卖").click()
    d.xpath('//*[@resource-id="com.sankuai.meituan:id/txt_search_normal"]/android.widget.LinearLayout[1]').click()
    d.send_keys(text)
    d(resourceId="com.sankuai.meituan:id/search_tv").click()

def find_specific_food(text):
    d = u2.connect()
    d.xpath('//*[@content-desc="搜索"]/android.widget.ImageView[1]').click()
    d.xpath(
        '//*[@resource-id="com.sankuai.meituan:id/fl_mrn_container"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[1]/android.view.ViewGroup[2]').click()
    d.send_keys(text)

def juge_open_wechat(contact):
    count = 0
    while count < 3:
        try:
            d = u2.connect()
            open_flag = d(packageName="com.tencent.mm").exists
            user_chat_flag = d(resourceId="com.tencent.mm:id/obn").exists
            if open_flag and user_chat_flag:
                if d(text=contact).exists:
                    pass
                else:
                    d.press("back")
                    d(text=contact).click()
                if d(text="Study Group(7)").exists and d(text="Zhao").exists:
                    d.press("back")
                if d(text="Office Work(8)").exists and d(text="Zhao").exists:
                    d.press("back")
            elif open_flag and user_chat_flag == False:
                d(text=contact).click()
            else:
                # d.press("home")
                # d.app_stop('com.tencent.mm')
                # d.app_start('com.tencent.mm')
                d(text=contact).click()
            return None
        except Exception as e:
            count += 1
    print("打开微信失败（仅演示）")

# juge_open_wechat()
# Forward_file_on_Wechat("Lee","Zhao")
#
# device = u2.connect()  # 你也可以使用USB连接，不过需要先通过adb连接到设备
# user_chat_flag = device(resourceId="com.tencent.mm:id/obn").exists
# print(user_chat_flag)
# elements = device.dump_hierarchy()
# with open('user_wechat.xml', 'w', encoding='utf-8') as file:
#     file.write(elements)