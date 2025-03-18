import os
import time
import subprocess
from PIL import Image
import uiautomator2 as u2
import re

def get_size(adb_path):
    command = "adb shell wm size"
    result = subprocess.run(command, capture_output=True, text=True, shell=True)
    resolution_line = result.stdout.strip().split('\n')[-1]
    width, height = map(int, resolution_line.split(' ')[-1].split('x'))
    return width, height

def get_xml(adb_path):
    process = subprocess.Popen([adb_path, 'shell', 'uiautomator', 'dump'], stdout=subprocess.PIPE)
    process.communicate()
    subprocess.run([adb_path, 'pull', '/sdcard/window_dump.xml', './xml/window_dump.xml'])

def take_screenshots(adb_path, num_screenshots, output_folder, crop_y_start, crop_y_end, slide_y_start, slide_y_end):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for i in range(num_screenshots):
        command = f"adb shell rm /sdcard/screenshot{i}.png"
        subprocess.run(command, capture_output=True, text=True, shell=True)
        command = f"adb shell screencap -p /sdcard/screenshot{i}.png"
        subprocess.run(command, capture_output=True, text=True, shell=True)
        command = f"adb pull /sdcard/screenshot{i}.png {output_folder}"
        subprocess.run(command, capture_output=True, text=True, shell=True)
        image = Image.open(f"{output_folder}/screenshot{i}.png")
        cropped_image = image.crop((0, crop_y_start, image.width, crop_y_end))
        cropped_image.save(f"{output_folder}/screenshot{i}.png")
        subprocess.run([adb_path, 'shell', 'input', 'swipe', '500', str(slide_y_start), '500', str(slide_y_end)])

def get_screenshot(adb_path):
    command = "adb shell rm /sdcard/screenshot.png"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(0.5)
    command = "adb shell screencap -p /sdcard/screenshot.png"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(0.5)
    command = "adb pull /sdcard/screenshot.png ./screenshot"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    image_path = "./screenshot/screenshot.png"
    save_path = "./screenshot/screenshot.jpg"
    image = Image.open(image_path)
    image.convert("RGB").save(save_path, "JPEG")
    os.remove(image_path)


def get_keyboard(adb_path):
    command = "adb shell dumpsys input_method"
    process = subprocess.run(command, capture_output=True, text=True, shell=True, encoding='utf-8')
    output = process.stdout.strip()
    for line in output.split('\n'):
        if "mInputShown" in line:
            if "mInputShown=true" in line:
                
                for line in output.split('\n'):
                    if "hintText" in line:
                        hintText = line.split("hintText=")[-1].split(" label")[0]
                        break
                
                return True, hintText
            elif "mInputShown=false" in line:
                return False, None

def tap(adb_path, x, y):
    command = f"adb shell input tap {x} {y}"
    subprocess.run(command, capture_output=True, text=True, shell=True)

def type(adb_path, text):
    text = text.replace("\\n", "_").replace("\n", "_")
    for char in text:
        if char == ' ':
            command = f"adb shell input text %s"
            subprocess.run(command, capture_output=True, text=True, shell=True)
        elif char == '_':
            command = f"adb shell input keyevent 66"
            subprocess.run(command, capture_output=True, text=True, shell=True)
        elif 'a' <= char <= 'z' or 'A' <= char <= 'Z' or char.isdigit():
            command = f"adb shell input text {char}"
            subprocess.run(command, capture_output=True, text=True, shell=True)
        elif char in '-.,!?@\'°/:;()':
            command = f"adb shell input text \"{char}\""
            subprocess.run(command, capture_output=True, text=True, shell=True)
        else:
            command = f"adb shell am broadcast -a ADB_INPUT_TEXT --es msg \"{char}\""
            subprocess.run(command, capture_output=True, text=True, shell=True)

def slide(adb_path, x1, y1, x2, y2):
    command = f"adb shell input swipe {x1} {y1} {x2} {y2} 500"
    subprocess.run(command, capture_output=True, text=True, shell=True)

def tap_hold(adb_path, x1, y1, x2, y2):
    command = f"adb shell input swipe {x1} {y1} {x2} {y2} 1500"
    subprocess.run(command, capture_output=True, text=True, shell=True)

def back(adb_path):
    command = f"adb shell input keyevent 4"
    subprocess.run(command, capture_output=True, text=True, shell=True)

def home(adb_path):
    command = f"adb shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
    subprocess.run(command, capture_output=True, text=True, shell=True)

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
    # d(resourceId='com.sdu.didi.psnger:id/sweep_view').click()


    # d.xpath("//*[@content-desc='搜索']").click()
    # # time.sleep(1)
    # d.send_keys(str(text))
    # time.sleep(1)
    # d.xpath("//*[@text='搜索']").click()
# open_xiecheng([1111])
# open_didi("清华大学FIT楼", "汇智大厦")

def Forward_file_on_Wechat(source_contact, target_contact):
    # source_contact  源目标
    # target_contact  转发目标
    d = u2.connect()

    # 等待微信启动
    d.app_stop('com.tencent.mm')
    d.app_start('com.tencent.mm')
    # 打开源微信账号的聊天界面
    d(text=source_contact).click()

    # 假设文件消息有一个特定的resource-id，这里用"com.tencent.mm:id/bju"代替
    # 选择最新的文件消息，这里我们尝试选择最后一个出现的
    # 注意：这需要根据你的实际界面布局来调整
    file_messages = d(resourceId="com.tencent.mm:id/bju")
    if file_messages.count > 0:
        # 选择最后一个文件消息
        latest_file_message = file_messages[-1]

        # 长按文件进行转发
        latest_file_message.long_click()

        # 选择转发
        d.xpath("//*[@text='转发']").click()

        # 选择通过微信转发
        d.xpath("//*[@text='搜索']").click()
        time.sleep(1)
        d.send_keys(target_contact)
        # 选择目标微信账号
        d(text=target_contact).click()
        # 确认转发
        d.xpath("//*[@text='发送']").click()
    else:
        # 选择最后一个文件消息
        # latest_file_message = file_messages

        # 长按文件进行转发
        d(resourceId="com.tencent.mm:id/bju").long_click()

        # 选择转发
        d.xpath("//*[@text='转发']").click()

        # 选择通过微信转发
        d.xpath("//*[@text='搜索']").click()
        time.sleep(1)
        d.send_keys(target_contact)
        # 选择目标微信账号
        d(text=target_contact).click()
        # 确认转发
        d.xpath("//*[@text='发送']").click()
        # print("未找到文件类型的消息")

def skipp_wechat_interface(contact):
    d = u2.connect()
    d.app_stop('com.tencent.mm')
    d.app_start('com.tencent.mm')
    d(text=contact).click()

# Forward_file_on_Wechat("孙楠", "毛博")
def talk_to_fitbot1(adb_path, text):

    d = u2.connect()
    d.app_stop('com.tencent.mm')
    d.app_start('com.tencent.mm')
    d(text='FitBot1').click()
    d(resourceId="com.tencent.mm:id/o4q").click()
    d.send_keys(text)
    time.sleep(1)
    d(resourceId="com.tencent.mm:id/bql").click()

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
    d = u2.connect()
    open_flag = d(packageName="com.tencent.mm").exists
    user_chat_flag = d(resourceId="com.tencent.mm:id/obn").exists
    if open_flag and user_chat_flag:
        if d(text=contact).exists:
            pass
        else:
            d.press("back")
            d(text=contact).click()
    elif open_flag and user_chat_flag==False:
        d(text=contact).click()
    else:
        d.press("home")
        d.app_stop('com.tencent.mm')
        d.app_start('com.tencent.mm')
        d(text=contact).click()


# device = u2.connect()  # 你也可以使用USB连接，不过需要先通过adb连接到设备
# elements = device.dump_hierarchy()
# with open('user_wechat.xml', 'w', encoding='utf-8') as file:
#     file.write(elements)

# input_str = "Forward file on WeChat(孙 楠, 毛 博)"
# # 使用正则表达式去除空格
# cleaned_str = re.sub(r'\s', '', input_str)
#
# # 提取名字
# names = re.findall(r'(\w+)', cleaned_str)
#
# # 打印结果
# print(names[1])
# action = "Open ticket booking app(北京到西安 7点)"
#
# cleaned_str = re.sub(r'\s', '', action)
# match = re.search(r'(\([^)]+\))', cleaned_str)
# # print(match[0])
# brackets_content = match.group(1)
#
# # 移除括号
# cleaned_content = re.sub(r'\(', '', brackets_content)
# cleaned_content = re.sub(r'\)', '', cleaned_content)
# type(cleaned_content)