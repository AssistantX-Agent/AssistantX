#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2024/8/8 13:54
# @Author : Yongchang
import threading

from common.wechat import *
from common.andro_operation import Forward_file_on_Wechat, juge_open_wechat
from common.robot_api import *
from common.LockApi import *
from common.global_var import count, initial_speaker, initial_instruction, group_history, user_history, chat_name, room_name, door_magnetic_value
from handing import *
import os
import time
from datetime import datetime
import copy

from OfficeAssistant.api import inference_chat

from OfficeAssistant.controller import get_screenshot, tap, slide, type, back, home, tap_hold, talk_to_fitbot1, talk_to_someone, search_food, open_meituan, find_specific_food, open_xiecheng, open_didi, skipp_wechat_interface
from OfficeAssistant.prompt_test import get_action_prompt, get_reflect_prompt, get_memory_prompt, get_process_prompt, read_prior_knowledge,get_perception_prompt,get_planning_prompt
from OfficeAssistant.chat import init_action_chat, init_reflect_chat, init_memory_chat, init_reflect_to_human_chat, add_response,init_perception_chat, add_response_two_image,init_planning_chat
from OfficeAssistant.prompt_assx import to_witch_robot

import re

import socket_server_dabai
import socket_server_armcar
import handle_dabai
import handle_armcar

result = ''
execute = False
robot = ''


def onmessage(wechatserver: WechatServer, message: WechatMessage):
    global execute, robot
    global count, group_history, user_history, initial_instruction
    order = ''
    now_time = datetime.now()
    time_str = str(now_time.strftime("%H:%M")) + ', '
    print(str(message.Content))
    output = to_witch_robot(str(message.Content))
    print(output)
    # 检查是否存在空格
    if ' ' not in output:
        wechatserver.Say(message.FromUserName, output)
    else:
        # 以第一个空格为间隔分割字符串
        robot, order = output.split(' ', 1)
        execute = True
        wechatserver.Say(message.FromUserName, '机器人' + robot + '为您服务~')
    if count == 0:
        # 来自群的消息
        if message.FromUserName[-9:] == '@chatroom':
            if message.ActionNickName == '':
                speaker = message.PushContent[:-7]
            else:
                speaker = message.ActionNickName
            if '@' + wechatserver.wx_name in message.Content:
                initial_instruction = speaker + " says: " + str(message.Content) + "\n"
                if message.FromUserName[-20:] == '48898365596@chatroom':
                    group_history['Office Work'] += initial_instruction
                    count += 1
                elif message.FromUserName[-20:] == '50562147484@chatroom':
                    group_history['Study Group'] += initial_instruction
                    count += 1

            else:
                group_chat = time_str + speaker + " says: " + str(message.Content) + "\n"
                if message.FromUserName[-20:] == '48898365596@chatroom':
                    group_history['Office Work'] += group_chat
                elif message.FromUserName[-20:] == '50562147484@chatroom':
                    group_history['Study Group'] += group_chat
        # 来自个人的消息
        else:
            if message.ActionNickName == '':
                speaker = message.PushContent[:-7]
            else:
                speaker = message.ActionNickName
            # @分离信息
            # content_after_bot = message.Content[len("@WechatBot1"):].strip()
            # 获取初始指令信息
            count += 1
            initial_instruction = speaker + " says: " + order + "\n"
            user_history[speaker] += initial_instruction
            # juge_open_wechat(speaker)
            # run(initial_instruction)
    elif count >= 1:
        # 来自群的消息
        if message.FromUserName[-9:] == '@chatroom':
            # 在群中被@的消息
            #  获取说话人名字
            # global_var.speaker == ''
            if message.ActionNickName == '':
                speaker = message.PushContent[:-7]
            else:
                speaker = message.ActionNickName
            group_chat = time_str + speaker + " says: " + str(message.Content) + "\n"
            if message.FromUserName[-20:] == '48898365596@chatroom':
                group_history['Office Work'] += group_chat
            elif message.FromUserName[-20:] == '50562147484@chatroom':
                group_history['Study Group'] += group_chat

            # print(group_history)
        # 来自个人的消息
        else:
            if message.ActionNickName == '':
                speaker = message.PushContent[:-7]
            else:
                speaker = message.ActionNickName
            if message.PushContent[-4:] == '[文件]':
                # @分离信息
                # content_after_bot = message.Content[len("@WechatBot1"):].strip()
                user_history[speaker] += time_str + speaker + " send an electronic file to you." + "\n"
            else:
                chat = time_str + speaker + " says: " + order + "\n"
                user_history[speaker] += chat
                # juge_open_wechat(speaker)
    print(robot)


if __name__ == '__main__':
    wechatserver = WechatServer('wxid_lq6wcq7qnjbp29', onmessage, onevent)  # 微信端口
    # while not robot:  # 如果 robot 为空字符串，就继续等待
    #     time.sleep(1)  # 每隔 0.1 秒检查一次
    ###water_api = WaterApi("192.168.10.10", 31001)  # 机器人连接端口
    # Your GPT-4o API URL
    API_url = "https://api.openai-hk.com/v1/chat/completions"
    # Your GPT-4o API Token
    token = "hk-x7r3vc100003489791121e73861680c3d17f2a2e074c5ae5"
    # token = "hk-9wv3wc10000348971afbdd5fea12c9e752219233bf35e73c"
    # list_of_unmanned_facilities = "water dispenser 1, water dispenser 2"  # 无人值守的公共物品信息
    # list_of_manned_facilities = "'毛博' '孙楠' is next to the printer"  # 有人值守的公共物品信息
    #priori_knowledge = read_prior_knowledge()  # 先验知识
    # print(priori_knowledge)
    thought_history = []  # 思考历史
    summary_history = []  # 总结历史
    action_history = []  # 行动历史
    reflect_history_count = []
    reflect_history = ''
    robot_status = ''  # 机器人状态感知  正在移动到l、空闲、移动到l成功
    thought = ''
    summary = ""  # 最后一次的总结
    action = ""  # 执行的行动
    description = ''
    # 上一次的记录
    last_thought_history = []  # 思考历史

    last_robot_status = ''  # 机器人状态感知  正在移动到l、空闲、移动到l成功
    last_summary = ""  # 最后一次的总结
    last_action = ""  # 执行的行动
    last_description = ""
    # 反射和记忆
    reflection_switch = True
    error_flag = False  # 动作执行错误标志？
    flag_count = 0
    flag = False
    refined_instruction = ''
    completed_content = ''
    while True:
        if robot == '大白1号' or robot == '大白2号':
            from OfficeAssistant.prompt_test import get_action_prompt, get_reflect_prompt, get_memory_prompt, get_process_prompt, read_prior_knowledge, get_perception_prompt, get_planning_prompt
            priori_knowledge = read_prior_knowledge()
            # initial_instruction = input("问题：")
            # count += 1
            # reflect test
            last_thought_history = thought_history  # 思考历史
            last_robot_status = robot_status  # 机器人状态感知  正在移动到l、空闲、移动到l成功
            last_summary = summary  # 最后一次的总结
            last_action = action  # 执行的行动
            last_description = description
            # reflect test
            robot_status = socket_server_dabai.send_dabai_command(
                'monitor_move_status')  # robot_status = monitor_move_status(water_api)
            now_time = datetime.now()
            time_str = "The current time is" + str(now_time.strftime("%H:%M"))
            time_str_chat = str(now_time.strftime("%H:%M")) + ', '
            reflect_flag = False
            if count >= 1:
                flag_count += 1
                if flag_count == 1:
                    flag = True
                else:
                    flag = False
                # start
                # ACTION
                chat_perception = init_perception_chat()
                prompt_perception = get_perception_prompt(initial_instruction, flag, robot_status, time_str,
                                                          global_var.locker_info, user_history, group_history,
                                                          priori_knowledge)
                perception_action = add_response("user", prompt_perception, chat_perception)
                output_perception = inference_chat(perception_action, 'gpt-4o', API_url, token)
                print('#' * 20, 'Perception', '#' * 20 + "\n")
                print(output_perception)
                if flag == False:
                    description = \
                    output_perception.split("### Description ###")[-1].split("### Active chat group and person ###")[
                        0].replace("\n", " ").replace(
                        "  ", " ").strip()
                    active = output_perception.split("### Active chat group and person ###")[-1].replace("\n",
                                                                                                         " ").replace(
                        "  ", " ").strip()
                if flag:
                    refined_instruction = output_perception.split("### Refined instruction ###")[-1].replace("\n",
                                                                                                             " ").replace(
                        "  ", " ").strip()
                    description = \
                    output_perception.split("### Description ###")[-1].split("### Active chat group and person ###")[
                        0].replace("\n", " ").replace(
                        "  ", " ").strip()
                    active = output_perception.split("### Active chat group and person ###")[-1].split(
                        "### Refined instruction ###")[0].replace("\n", " ").replace(
                        "  ", " ").strip()
                    # print(initial_instruction)

                # print('#' * 20, 'Description', '#' * 20 + "\n")
                # print(description)
                # print(initial_instruction)
                chat_planning = init_planning_chat()
                prompt_planning = get_planning_prompt(initial_instruction, summary_history,
                                                  action_history, summary, action, error_flag,
                                                  priori_knowledge, user_history
                                                  , time_str, group_history, reflect_history,description)
                chat_planning = add_response("user", prompt_planning, chat_planning)
                output_planning = inference_chat(chat_planning, 'gpt-4o', API_url, token)
                print('#' * 20, 'Output_Planning', '#' * 20 + "\n")
                print(output_planning)

                prompt_action = get_action_prompt(initial_instruction, summary_history,
                                                  action_history, summary, action, error_flag,
                                                  priori_knowledge, user_history
                                                  , time_str, group_history, reflect_history, description,
                                                  refined_instruction, active, global_var.locker_info, robot_status, output_planning)

                chat_action = init_action_chat()
                chat_action = add_response("user", prompt_action, chat_action)
                output_action = inference_chat(chat_action, 'gpt-4o', API_url, token)
                print('#' * 20, 'Output_Action', '#' * 20 + "\n")
                print(output_action)
                thought = output_action.split("### Thought ###")[-1].split("### Action ###")[0].replace("\n",
                                                                                                        " ").replace(
                    ":", "").replace("  ", " ").strip()
                summary = output_action.split("### Operation ###")[-1].replace("\n", " ").replace("  ", " ").strip()
                action = output_action.split("### Action ###")[-1].split("### Operation ###")[0].replace("\n",
                                                                                                         " ").replace(
                    "  ", " ").strip()
                if "Forward electronic file" in action:
                    # print( '#' * 50, action, '#' * 50)
                    send_message_pattern = r"Forward electronic file\s*\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)"
                    send_message_match = re.search(send_message_pattern, action)
                    if send_message_match:
                        name_one = send_message_match.group(1).strip()
                        name_two = send_message_match.group(2).strip()
                        flag_forward = Forward_file_on_Wechat(str(name_one), str(name_two))
                        action += flag_forward
                if "Move" in action:
                    move_and_wait_pattern = r"Move\s*\(\s*([^)]+?)\s*\)"
                    move_and_wait_match = re.search(move_and_wait_pattern, action)
                    if move_and_wait_match:
                        mover = move_and_wait_match.group(1)
                        socket_server_dabai.send_dabai_command('move_cancel')  # water_api.move_cancel()
                        socket_server_dabai.send_dabai_command('move_marker',
                                                               str(mover))  # water_api.move_marker(str(mover))
                if "Inform" in action:
                    # 使用正则表达式抽取 Send message 的参数
                    send_message_pattern = r"Inform\s*\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)"
                    send_message_match = re.search(send_message_pattern, action)
                    if send_message_match:
                        person_name = send_message_match.group(1).strip()
                        message = send_message_match.group(2).strip(' "\'')
                        time.sleep(1)
                        if "Office Work" in action:
                            # juge_open_wechat("Office Work")
                            wechatserver.Say(room_name[person_name], str(message))
                            group_history[person_name] += time_str_chat + "Assitant(yourself): " + str(message) + "\n"
                        elif "Study Group" in action:
                            # juge_open_wechat("Study Group")
                            wechatserver.Say(room_name[person_name], str(message))
                            group_history[person_name] += time_str_chat + "Assitant(yourself): " + str(message) + "\n"
                        else:
                            # juge_open_wechat(person_name)
                            wechatserver.Say(chat_name[person_name], str(message))
                            user_history[person_name] += time_str_chat + "Assitant(yourself): " + str(
                                person_name) + ', ' + str(message) + "\n"
                if "Ask" in action:
                    send_message_pattern = r"Ask\s*\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)"
                    send_message_match = re.search(send_message_pattern, action)
                    if send_message_match:
                        person_name = send_message_match.group(1).strip(' "\'')
                        message = send_message_match.group(2).strip(' "\'')  # 移除消息字符串两边的引号\
                        time.sleep(1)
                        if "Office Work" in action:
                            # juge_open_wechat("Office Work")
                            wechatserver.Say(room_name[person_name], str(message))
                            group_history[person_name] += time_str_chat + "Assitant(yourself): " + str(message) + "\n"
                        elif "Study Group" in action:
                            # juge_open_wechat("Study Group")
                            wechatserver.Say(room_name[person_name], str(message))
                            group_history[person_name] += time_str_chat + "Assitant(yourself): " + str(message) + "\n"
                        else:
                            # juge_open_wechat(person_name)
                            wechatserver.Say(chat_name[person_name], str(message))
                            user_history[person_name] += time_str_chat + "Assitant(yourself): " + str(
                                person_name) + ', ' + str(message) + "\n"

                        # action_history.append(f"I have asked {person_name}: {str(message)}")
                        # action_history.append(f"Ask someone({str(person_name)}, {str(message)})")

                if "Send QR code" in action:
                    # print( '#' * 50, action, '#' * 50)
                    send_message_pattern = r"Send QR code\s*\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)"
                    send_message_match = re.search(send_message_pattern, action)
                    if send_message_match:
                        person_name = send_message_match.group(1).strip()
                        itme_name = send_message_match.group(2).strip()
                        global_var.locker_flag = False
                        time.sleep(2)
                        global_var.locker_flag = True
                        thread = threading.Thread(target=ocSelect, args=(str(person_name), str(itme_name),))
                        thread.start()
                        # juge_open_wechat(person_name)
                        time.sleep(1)
                        wechatserver.SayImage(chat_name[person_name], img_encode(itme_name=itme_name))
                # if "Send QR code" in action:
                #     send_message_pattern = r"Send QR code\s*\(\s*([^,]+?)\s*\)"
                #     send_message_match = re.search(send_message_pattern, action)
                #     if send_message_match:
                #         person_name = send_message_match.group(1).strip()
                #         global_var.locker_flag = False
                #         time.sleep(2)
                #         global_var.locker_flag = True
                #         thread = threading.Thread(target=ocSelect, args=(str(person_name),))
                #         thread.start()
                #         time.sleep(1)
                #         wechatserver.SayImage(chat_name[person_name], img_encode())

                if "Wait in place" in action:
                    wait_pattern = r"Wait in place\s*\(\s*([^)]+?)\s*\)"
                    wait_match = re.search(wait_pattern, action)
                    if wait_match:
                        person_name = wait_match.group(1)
                if "Wait" in action:
                    send_message_pattern = r"Wait\s*\(\s*([^)]+?)\s*\)"
                    send_message_match = re.search(send_message_pattern, action)
                    word_to_count = "Wait"
                    pattern = r'\b' + re.escape(word_to_count) + r'\b'
                    count = len(re.findall(pattern, action, re.IGNORECASE))
                    time_int = 5 * int(count)
                    if send_message_match:
                        person_name = send_message_match.group(1)
                    time.sleep(time_int)
                if "Stop" in action:
                    socket_server_dabai.send_dabai_command('move_cancel')  # water_api.move_cancel()
                    socket_server_dabai.send_dabai_command('move_marker', '充电桩')  # water_api.move_marker('充电桩')
                    chat_planning = init_planning_chat()

                    prompt_planning = get_planning_prompt(initial_instruction, thought_history,
                                                          action_history, thought, action, error_flag,
                                                          priori_knowledge, user_history
                                                          , time_str, group_history, reflect_history, description)
                    chat_planning = add_response("user", prompt_planning, chat_planning)
                    output_planning = inference_chat(chat_planning, 'gpt-4o', API_url, token)
                    print('#' * 20, 'Planing', '#' * 20 + "\n")
                    print(output_planning)
                    item_pos = time_str_chat + output_planning.split("### Items location ###")[-1].replace("\n",
                                                                                                           " ").replace(
                        "  ", " ").strip()
                    priori_knowledge += '\n' + item_pos
                    print(priori_knowledge)
                    with open(f"Result/gpt4o/{initial_instruction}.txt", "w+") as f:
                        f.write(result)
                        f.close()
                    count = 0
                    flag_count = 0
                    thought_history = []  # 思考历史
                    summary_history = []  # 总结历史
                    action_history = []  # 行动历史
                    reflect_history_count = []
                    robot_status = ''  # 机器人状态感知  正在移动到l、空闲、移动到l成功
                    summary = ""  # 最后一次的总结
                    action = ""  # 执行的行动
                    thought = ""
                    last_thought_history = thought_history  # 思考历史
                    last_summary = summary  # 最后一次的总结
                    last_action = action  # 执行的行动
                    description = ''
                    last_description = description
                    # 反射和记忆
                    reflection_switch = True
                    error_flag = False  # 动作执行错误标志？

                    global_var.locker_info = ''
                    reflect_flag = False
                    user_history = {user_id: '' for user_id in chat_name.keys()}
                    group_history = {group_id: '' for group_id in room_name.keys()}

                    # break

                time.sleep(2)
                robot_status = socket_server_dabai.send_dabai_command(
                    'monitor_move_status')  # robot_status = monitor_move_status(water_api)
                print(robot_status)
                prompt_reflect = get_reflect_prompt(initial_instruction, thought_history,
                                                    action_history, last_description, thought, action, description,
                                                    priori_knowledge, user_history, group_history, completed_content)
                chat_reflect = init_reflect_chat()
                chat_reflect = add_response_two_image("user", prompt_reflect, chat_reflect)

                output_reflect = inference_chat(chat_reflect, 'gpt-4o', API_url, token)
                status = "#" * 50 + " Reflcetion " + "#" * 50
                print(status)
                print(output_reflect)
                print('#' * len(status))

                if reflect_flag == True:
                    reflect_history = ''
                    robot_status = socket_server_dabai.send_dabai_command(
                        'monitor_move_status')  # robot_status = monitor_move_status(water_api)
                    print(robot_status)
                    prompt_reflect = get_reflect_prompt(initial_instruction, thought_history,
                                                        action_history, last_description, thought, action, description,
                                                        priori_knowledge, user_history, group_history,
                                                        completed_content)
                    chat_reflect = init_reflect_chat()
                    chat_reflect = add_response_two_image("user", prompt_reflect, chat_reflect)

                    output_reflect = inference_chat(chat_reflect, 'gpt-4o', API_url, token)
                    answer = output_reflect.split("### Answer ###")[-1].replace("\n", " ").strip()
                    chat_reflect = add_response("assistant", output_reflect, chat_reflect)
                    completed_content = output_action.split("### Completed contents ###")[-1].split("### Thought ###")[
                        0].replace("\n", " ").replace(":", "").replace("  ", " ").strip()

                    status = "#" * 50 + " Reflcetion " + "#" * 50
                    reply_marker = "### Reflect ###"
                    answer_marker = "### Answer ###"

                    start_pos = output_reflect.find(reply_marker) + len(reply_marker) + 1
                    end_pos = output_reflect.find(answer_marker) - 1
                    extracted_text = output_reflect[start_pos:end_pos]
                    reflect = extracted_text.strip()

                    print(status)
                    print(output_reflect)
                    print('#' * len(status))
                    if 'Y' in answer:
                        # thought_history.append(thought)
                        # summary_history.append(summary)
                        # action_history.append(action)

                        error_flag = False
                    elif 'N' in answer:
                        error_flag = True
                        reflect_history = reflect
                        # action_history.append(action)

                thought_history.append(thought)
                summary_history.append(summary)
                action_history.append(action)
                # reflect_history_count.append(output_reflect + "\n")
                # result = '\n thought_history：\n' + str(thought_history) + '\n action_history：\n' + str(action_history) + '\n action_history：\n' + str(action_history) + '\n reflect_history：\n' + str(reflect_history_count)

            print("###################################")
            time.sleep(4)
        elif robot == '移动机械臂':
            from OfficeAssistant.prompt_test import get_action_prompt, get_reflect_prompt, get_memory_prompt, get_process_prompt, read_prior_knowledge, get_perception_prompt, get_planning_prompt
            priori_knowledge = read_prior_knowledge()
            # initial_instruction = input("问题：")
            # count += 1
            # reflect test
            last_thought_history = thought_history  # 思考历史
            last_robot_status = robot_status  # 机器人状态感知  正在移动到l、空闲、移动到l成功
            last_summary = summary  # 最后一次的总结
            last_action = action  # 执行的行动
            last_description = description
            # reflect test
            # robot_status = socket_server_dabai.send_robot_command(
            #     'monitor_move_status')  # robot_status = monitor_move_status(water_api)
            now_time = datetime.now()
            time_str = "The current time is" + str(now_time.strftime("%H:%M"))
            time_str_chat = str(now_time.strftime("%H:%M")) + ', '
            reflect_flag = False
            if count >= 1:
                flag_count += 1
                if flag_count == 1:
                    flag = True
                else:
                    flag = False
                # start
                # ACTION
                chat_perception = init_perception_chat()
                prompt_perception = get_perception_prompt(initial_instruction, flag, robot_status, time_str,
                                                          global_var.locker_info, user_history, group_history,
                                                          priori_knowledge)
                perception_action = add_response("user", prompt_perception, chat_perception)
                output_perception = inference_chat(perception_action, 'gpt-4o', API_url, token)
                print('#' * 20, 'Perception', '#' * 20 + "\n")
                print(output_perception)
                if flag == False:
                    description = \
                    output_perception.split("### Description ###")[-1].split("### Active chat group and person ###")[
                        0].replace("\n", " ").replace(
                        "  ", " ").strip()
                    active = output_perception.split("### Active chat group and person ###")[-1].replace("\n",
                                                                                                         " ").replace(
                        "  ", " ").strip()
                if flag:
                    refined_instruction = output_perception.split("### Refined instruction ###")[-1].replace("\n",
                                                                                                             " ").replace(
                        "  ", " ").strip()
                    description = \
                    output_perception.split("### Description ###")[-1].split("### Active chat group and person ###")[
                        0].replace("\n", " ").replace(
                        "  ", " ").strip()
                    active = output_perception.split("### Active chat group and person ###")[-1].split(
                        "### Refined instruction ###")[0].replace("\n", " ").replace(
                        "  ", " ").strip()
                    # print(initial_instruction)

                # print('#' * 20, 'Description', '#' * 20 + "\n")
                # print(description)
                # print(initial_instruction)
                # chat_planning = init_planning_chat()
                # prompt_planning = get_planning_prompt(initial_instruction, summary_history,
                #                                   action_history, summary, action, error_flag,
                #                                   priori_knowledge, user_history
                #                                   , time_str, group_history, reflect_history,description)
                # chat_planning = add_response("user", prompt_planning, chat_planning)
                # output_planning = inference_chat(chat_planning, 'gpt-4o', API_url, token)
                # print('#' * 20, 'Output_Planning', '#' * 20 + "\n")
                # print(output_planning)

                prompt_action = get_action_prompt(initial_instruction, summary_history,
                                                  action_history, summary, action, error_flag,
                                                  priori_knowledge, user_history
                                                  , time_str, group_history, reflect_history, description,
                                                  refined_instruction, active, global_var.locker_info, robot_status)

                chat_action = init_action_chat()
                chat_action = add_response("user", prompt_action, chat_action)
                output_action = inference_chat(chat_action, 'gpt-4o', API_url, token)
                print('#' * 20, 'Output_Action', '#' * 20 + "\n")
                print(output_action)
                thought = output_action.split("### Thought ###")[-1].split("### Action ###")[0].replace("\n",
                                                                                                        " ").replace(
                    ":", "").replace("  ", " ").strip()
                summary = output_action.split("### Operation ###")[-1].replace("\n", " ").replace("  ", " ").strip()
                action = output_action.split("### Action ###")[-1].split("### Operation ###")[0].replace("\n",
                                                                                                         " ").replace(
                    "  ", " ").strip()
                if "Forward electronic file" in action:
                    # print( '#' * 50, action, '#' * 50)
                    send_message_pattern = r"Forward electronic file\s*\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)"
                    send_message_match = re.search(send_message_pattern, action)
                    if send_message_match:
                        name_one = send_message_match.group(1).strip()
                        name_two = send_message_match.group(2).strip()
                        flag_forward = Forward_file_on_Wechat(str(name_one), str(name_two))
                        action += flag_forward
                if "Move" in action:
                    move_and_wait_pattern = r"Move\s*\(\s*([^)]+?)\s*\)"
                    move_and_wait_match = re.search(move_and_wait_pattern, action)
                    if move_and_wait_match:
                        mover = move_and_wait_match.group(1)
                        socket_server_armcar.send_armcar_command('move_marker', str(mover))
                        # socket_server_dabai.send_robot_command('move_cancel')  # water_api.move_cancel()
                        # socket_server_dabai.send_robot_command('move_marker',
                        #                                        str(mover))  # water_api.move_marker(str(mover))
                if "Inform" in action:
                    # 使用正则表达式抽取 Send message 的参数
                    send_message_pattern = r"Inform\s*\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)"
                    send_message_match = re.search(send_message_pattern, action)
                    if send_message_match:
                        person_name = send_message_match.group(1).strip()
                        message = send_message_match.group(2).strip(' "\'')
                        time.sleep(1)
                        if "Office Work" in action:
                            # juge_open_wechat("Office Work")
                            wechatserver.Say(room_name[person_name], str(message))
                            group_history[person_name] += time_str_chat + "Assitant(yourself): " + str(message) + "\n"
                        elif "Study Group" in action:
                            # juge_open_wechat("Study Group")
                            wechatserver.Say(room_name[person_name], str(message))
                            group_history[person_name] += time_str_chat + "Assitant(yourself): " + str(message) + "\n"
                        else:
                            # juge_open_wechat(person_name)
                            wechatserver.Say(chat_name[person_name], str(message))
                            user_history[person_name] += time_str_chat + "Assitant(yourself): " + str(
                                person_name) + ', ' + str(message) + "\n"
                if "Ask" in action:
                    send_message_pattern = r"Ask\s*\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)"
                    send_message_match = re.search(send_message_pattern, action)
                    if send_message_match:
                        person_name = send_message_match.group(1).strip(' "\'')
                        message = send_message_match.group(2).strip(' "\'')  # 移除消息字符串两边的引号\
                        time.sleep(1)
                        if "Office Work" in action:
                            # juge_open_wechat("Office Work")
                            wechatserver.Say(room_name[person_name], str(message))
                            group_history[person_name] += time_str_chat + "Assitant(yourself): " + str(message) + "\n"
                        elif "Study Group" in action:
                            # juge_open_wechat("Study Group")
                            wechatserver.Say(room_name[person_name], str(message))
                            group_history[person_name] += time_str_chat + "Assitant(yourself): " + str(message) + "\n"
                        else:
                            # juge_open_wechat(person_name)
                            wechatserver.Say(chat_name[person_name], str(message))
                            user_history[person_name] += time_str_chat + "Assitant(yourself): " + str(
                                person_name) + ', ' + str(message) + "\n"

                        # action_history.append(f"I have asked {person_name}: {str(message)}")
                        # action_history.append(f"Ask someone({str(person_name)}, {str(message)})")

                if "Wait in place" in action:
                    wait_pattern = r"Wait in place\s*\(\s*([^)]+?)\s*\)"
                    wait_match = re.search(wait_pattern, action)
                    if wait_match:
                        person_name = wait_match.group(1)
                if "Wait" in action:
                    send_message_pattern = r"Wait\s*\(\s*([^)]+?)\s*\)"
                    send_message_match = re.search(send_message_pattern, action)
                    word_to_count = "Wait"
                    pattern = r'\b' + re.escape(word_to_count) + r'\b'
                    count = len(re.findall(pattern, action, re.IGNORECASE))
                    time_int = 5 * int(count)
                    if send_message_match:
                        person_name = send_message_match.group(1)
                    time.sleep(time_int)
                if "Stop" in action:
                    socket_server_armcar.send_armcar_command('move_marker', 'place1')
                    # socket_server_dabai.send_robot_command('move_cancel')  # water_api.move_cancel()
                    # socket_server_dabai.send_robot_command('move_marker', '充电桩')  # water_api.move_marker('充电桩')
                    chat_planning = init_planning_chat()

                    prompt_planning = get_planning_prompt(initial_instruction, thought_history,
                                                          action_history, thought, action, error_flag,
                                                          priori_knowledge, user_history
                                                          , time_str, group_history, reflect_history, description)
                    chat_planning = add_response("user", prompt_planning, chat_planning)
                    output_planning = inference_chat(chat_planning, 'gpt-4o', API_url, token)
                    print('#' * 20, 'Planing', '#' * 20 + "\n")
                    print(output_planning)
                    item_pos = time_str_chat + output_planning.split("### Items location ###")[-1].replace("\n",
                                                                                                           " ").replace(
                        "  ", " ").strip()
                    priori_knowledge += '\n' + item_pos
                    print(priori_knowledge)
                    with open(f"Result/gpt4o/{initial_instruction}.txt", "w+") as f:
                        f.write(result)
                        f.close()
                    count = 0
                    flag_count = 0
                    thought_history = []  # 思考历史
                    summary_history = []  # 总结历史
                    action_history = []  # 行动历史
                    reflect_history_count = []
                    robot_status = ''  # 机器人状态感知  正在移动到l、空闲、移动到l成功
                    summary = ""  # 最后一次的总结
                    action = ""  # 执行的行动
                    thought = ""
                    last_thought_history = thought_history  # 思考历史
                    last_summary = summary  # 最后一次的总结
                    last_action = action  # 执行的行动
                    description = ''
                    last_description = description
                    # 反射和记忆
                    reflection_switch = True
                    error_flag = False  # 动作执行错误标志？

                    global_var.locker_info = ''
                    reflect_flag = False
                    user_history = {user_id: '' for user_id in chat_name.keys()}
                    group_history = {group_id: '' for group_id in room_name.keys()}

                    # break

                time.sleep(2)
                # robot_status = socket_server_dabai.send_robot_command(
                #     'monitor_move_status')  # robot_status = monitor_move_status(water_api)
                print(robot_status)
                prompt_reflect = get_reflect_prompt(initial_instruction, thought_history,
                                                    action_history, last_description, thought, action, description,
                                                    priori_knowledge, user_history, group_history, completed_content)
                chat_reflect = init_reflect_chat()
                chat_reflect = add_response_two_image("user", prompt_reflect, chat_reflect)

                output_reflect = inference_chat(chat_reflect, 'gpt-4o', API_url, token)
                status = "#" * 50 + " Reflcetion " + "#" * 50
                print(status)
                print(output_reflect)
                print('#' * len(status))

                if reflect_flag == True:
                    reflect_history = ''
                    # robot_status = socket_server_dabai.send_robot_command(
                    #     'monitor_move_status')  # robot_status = monitor_move_status(water_api)
                    print(robot_status)
                    prompt_reflect = get_reflect_prompt(initial_instruction, thought_history,
                                                        action_history, last_description, thought, action, description,
                                                        priori_knowledge, user_history, group_history,
                                                        completed_content)
                    chat_reflect = init_reflect_chat()
                    chat_reflect = add_response_two_image("user", prompt_reflect, chat_reflect)

                    output_reflect = inference_chat(chat_reflect, 'gpt-4o', API_url, token)
                    answer = output_reflect.split("### Answer ###")[-1].replace("\n", " ").strip()
                    chat_reflect = add_response("assistant", output_reflect, chat_reflect)
                    completed_content = output_action.split("### Completed contents ###")[-1].split("### Thought ###")[
                        0].replace("\n", " ").replace(":", "").replace("  ", " ").strip()

                    status = "#" * 50 + " Reflcetion " + "#" * 50
                    reply_marker = "### Reflect ###"
                    answer_marker = "### Answer ###"

                    start_pos = output_reflect.find(reply_marker) + len(reply_marker) + 1
                    end_pos = output_reflect.find(answer_marker) - 1
                    extracted_text = output_reflect[start_pos:end_pos]
                    reflect = extracted_text.strip()

                    print(status)
                    print(output_reflect)
                    print('#' * len(status))
                    if 'Y' in answer:
                        # thought_history.append(thought)
                        # summary_history.append(summary)
                        # action_history.append(action)

                        error_flag = False
                    elif 'N' in answer:
                        error_flag = True
                        reflect_history = reflect
                        # action_history.append(action)

                thought_history.append(thought)
                summary_history.append(summary)
                action_history.append(action)
                # reflect_history_count.append(output_reflect + "\n")
                # result = '\n thought_history：\n' + str(thought_history) + '\n action_history：\n' + str(action_history) + '\n action_history：\n' + str(action_history) + '\n reflect_history：\n' + str(reflect_history_count)

            print("###################################")
            time.sleep(4)