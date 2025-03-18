#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2024/8/11 19:14
# @Author : Yongchang

# 指令计数
count = 0   # 0为初始指令
# 门锁信号
door_magnetic_value = 0
# 下发指令的人
initial_speaker = ''
initial_instruction = ''

# 门锁字段
locker_info = ''

locker_flag = False

# 微信id
chat_name = {
    '吴厉博闻': 'wxid_k1mju4pkr8jx12',
    '郑文': 'wxid_oajavhv6otdo22',
    'Wu': 'wxid_k1mju4pkr8jx12',
    'Zheng': 'wxid_oajavhv6otdo22',
    '实验区左墙角': 'wxid_oajavhv6otdo22',
    '实验区中间': 'wxid_oajavhv6otdo22',
    '实验区右墙角': 'wxid_oajavhv6otdo22'
}

room_name = {
    "Office Work": "48898365596@chatroom",
    "Study Group": "50562147484@chatroom"
}

# 指令下发后的历史群聊
group_history = {group_id: '' for group_id in room_name.keys()}
# 与用户的历史群聊信息
user_history = {user_id: '' for user_id in chat_name.keys()}
# print(user_history,type(user_history))

# print(user_history)
# list_of_manned_facilities = {'printer': ['李老师']}      # 有人值守的公共物品信息
# for facility, name in zip(list_of_manned_facilities.keys(), list_of_manned_facilities.values()):
#     print(facility, name)
