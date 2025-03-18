import json
import socket
import time
import math
import cv2
import numpy as np

class WaterApi:
    def __init__(self, host: str, port: int) -> None:
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.connect((host, port))
        self.origin_x, self.origin_y, self.height, self.width, self.resolution = self.get_map_info()

    def robot_status(self) -> dict:
        """
        获取机器人的状态信息
        {"results":
            {
            "move_target": "target_name", // 移动指令指定的目标点位名称
            "move_status": "running", // 移动指令的执行状态。详细解释见后边
            "running_status": "running", // v0.7.12新增，移动任务的具体状态， 详细见后面解释
            "move_retry_times": 3, //此次数每增加1，表示机器人进行了新一轮的路径重试；路径规划一次性成功此值默认为0

            "charge_state": bool, //true->充电中状态。false->未充电状态。
            "soft_estop_state": bool, // 通过API接口设置的软急停状态, true->急停中，false->非急停中
            "hard_estop_state": bool, // 通过硬件急停按钮设置的硬急停状态, true->急停中，false->非急停中
            "estop_state": bool,  // hard_estop_state || sofpt_estop_state, true->急停中，false->非急停中
            "power_percent": 100, //电量百分比，单位：%
            "current_pose": {
                "x": 11.0,     // 单位：m
                "y": 11.0,	   // 单位：m
                "theta": 0.5, //单位：rad
            }
        "current_floor": 16,
        "chargepile_id": "1234", // v0.9.6新增。充电状态下表示当前正在充电的充电桩ID，非充电状态下返回“0”。注：此字段仅在部分产品中有效，其余返回“0”。
        "error_code": "00000000"   // v0.7.7新增，16进制错误码，总共8个字节表示，非0表示机器人异常
        }

        """
        receive = {}
        try:
            send_data = "/api/robot_status"
            self.tcp_socket.send(send_data.encode("utf-8"))
            rrr = self.tcp_socket.recv(2048)
            rrr = rrr.split()
        # receive = json.loads(rrr[0])
            try:
                receive = json.loads(rrr[0])
            except json.decoder.JSONDecodeError as e:
                error = str(e).split(':', 1)
                line = error[1].split()[1]  # 行
                column = error[1].split()[3]  # 列
                char = error[1].split()[5].split(')')[0]  # 字节序数
                if error[0] == "Expecting value":  # 开头数据有问题
                    print('error: ', error[0], line, column, char)
                if error[0] == "Extra data":  # 结尾数据有问题
                    print('error: ', error[0], line, column, char)
                if error[0] == "Unterminated string starting at":
                    receive = json.loads(rrr[1])
                print(error)
        except Exception as e:
            receive = self.robot_status()
        if 'results' not in receive:
            receive = self.robot_status()
        return receive

    def get_map_info(self):
        """
        得到地图的相关信息
        :return: [地图左下角世界坐标x, 地图左下角世界坐标y, 像素地图高度, 像素地图宽度, 分辨率]
        """
        send_data = "/api/map/get_current_map"
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        receive = json.loads(receive)
        receive = receive['results']['info']
        return [receive['origin_x'], receive['origin_y'], receive['height'], receive['width'], receive['resolution']]

    def get_marker_list(self):
        send_data = "/api/markers/query_list"
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(51200)
        receive = json.loads(receive)
        if receive['status'] == 'OK':
            return receive['results']
        else:
            print("获取当前地图具体信息失败，错误信息：{}".format(receive['error_message']))
            return receive['status'], receive['error_message']

    def get_current_pose(self):
        """
        返回当前世界坐标

        :return: [世界坐标x, 世界坐标y, 角度theta]
        """
        send_data = "/api/robot_status"
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        receive = json.loads(receive)
        receive = receive['results']['current_pose']
        return [receive['x'], receive['y'], receive['theta']]

    def get_pose_pix(self):
        """
        返回像素坐标

        :return: [像素坐标x, 像素坐标y, 角度theta]
        """
        loc_x, loc_y, theta = self.get_current_pose()
        loc_x_pix = int((loc_x - self.origin_x) / self.resolution)
        loc_y_pix = int(self.height - (loc_y - self.origin_y) / self.resolution)
        return loc_x_pix, loc_y_pix, theta

    def get_path(self):
        """
        返回当前路径

        :return:
        """
        send_data = "/api/get_planned_path"
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(51200)
        receive = json.loads(receive)
        print(receive)
        path = receive['results']['path']
        return path

    def make_plan(self, start, goal, start_floor=5, goal_floor=5):
        """
        规划两点之间的路径，返回距离
        @param start:开始点(x,y)
        @param goal:目标点(x,y)
        @return:距离
        """
        send_data = "/api/make_plan?start_x={}&start_y={}&start_floor={}&goal_x={}&goal_y={}&goal_floor={}".format(
            start[0], start[1], start_floor, goal[0], goal[1], goal_floor)
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        receive = json.loads(receive)
        return receive

    def get_pose_real_and_pix_and_isRunning(self):
        """
        返回世界坐标和像素坐标以及isRunning的状态

        :return: ([世界坐标x, 世界坐标y, 当前角度theta], [像素坐标x, 像素坐标y, 当前角度theta], isRunning)
        """
        receive = self.robot_status()
        current_pose = receive['results']['current_pose']
        loc_x_pix, loc_y_pix = self.real_to_pix(current_pose['x'], current_pose['y'])
        isRunning = receive['results']['move_status'] == 'running'
        return [current_pose['x'], current_pose['y'], current_pose['theta']], \
               [loc_x_pix, loc_y_pix, current_pose['theta']], isRunning

    def real_to_pix(self, real_x, real_y):
        """
        世界坐标转换成像素坐标

        :param real_x: 世界坐标x
        :param real_y: 世界坐标y
        :return: (像素坐标x, 像素坐标y)
        """
        return int((real_x - self.origin_x) / self.resolution), \
               int(self.height - (real_y - self.origin_y) / self.resolution)

    def pix_to_real(self, pix_x, pix_y):
        """
        像素坐标转换成世界坐标

        :param pix_x: 像素坐标x
        :param pix_y: 像素坐标y
        :return: (世界坐标x, 世界坐标y)
        """
        return self.resolution * pix_x + self.origin_x, self.origin_y - (pix_y - self.height) * self.resolution

    def move_marker(self, marker_name):
        """
        移动任务设置
        :param marker_name: 机器人的marker名字
        :return:
        """
        send_data = "/api/move?marker=" + marker_name
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        # receive = receive.decode("utf-8")
        # if len(receive):
        #     receive = json.loads(receive)
        #     if receive['status'] == 'OK':
        #         print("目标" + marker_name + "设置成功")
        #         self.clear()
        #         return True
        #     elif receive['error_message'] != '':
        #         print("目标" + marker_name + "设置失败")
        #         self.clear()
        #         return False

    def move_location(self, x, y, theta):
        """
        移动到指定位置
        :param x: 目标位置x坐标
        :param y: 目标位置y坐标
        :param theta: 目标位置theta角度
        :return:
        """
        send_data = "/api/move?location={},{},{}".format(x, y, theta)
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        # receive = receive.decode("utf-8")
        if len(receive):
            receive = json.loads(receive)
            if receive['status'] == 'OK':
                print("移动坐标(" + x + "," + y + ")设置成功")
                return True
            elif receive['error_message'] != '':
                print("移动坐标(" + x + "," + y + ")设置失败")
                return False

    def move_cancel(self):
        send_data = "/api/move/cancel"
        self.tcp_socket.send(send_data.encode("utf-8"))
        # receive = self.tcp_socket.recv(1024)
        # receive = receive.decode("utf-8")
        # if len(receive):
        #     receive = json.loads(receive)
        #     if receive['status'] == 'OK':
        #         print("移动任务取消成功")
        #         return True
        #     elif receive['error_message'] != '':
        #         print("移动任务取消失败")
        #         return False

    def delete_marker(self, marker_name):
        send_data = "/api/markers/delete?name={}".format(marker_name)
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        # receive = receive.decode("utf-8")
        if len(receive):
            receive = json.loads(receive)
            if receive['status'] == 'OK':
                print("目标" + marker_name + "删除成功")
                return True
            elif receive['error_message'] != '':
                print("目标" + marker_name + "删除失败")
                return False

    def adjust(self, marker_name):
        send_data = "/api/position_adjust?marker={}".format(marker_name)
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        # receive = receive.decode("utf-8")
        if len(receive):
            receive = json.loads(receive)
            if receive['status'] == 'OK':
                print("校正成功")
                return True
            elif receive['error_message'] != '':
                print("校正失败")
                return False

    def set_current_marker(self, marker_name):
        """
        当前位置设置marker
        @param location:location['name'], location['x'], location['y'], location['theta']
        @return:
        """
        send_data = "/api/markers/insert?name={}".format(marker_name)
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        # receive = receive.decode("utf-8")
        if len(receive):
            receive = json.loads(receive)
            if receive['status'] == 'OK':
                print("当前点位设置成功")
                return True
            elif receive['error_message'] != '':
                print("当前点位设置失败")
                return False

    def set_location_marker(self, location, floor = 5):
        """
        坐标设置设置地图上的标记点
        @param location:location['name'], location['x'], location['y'], location['theta']
        @return:
        """
        send_data = "/api/markers/insert_by_pose?name={}&x={}&y={}&theta={}&floor={}}&type=0".format(
            location['name'], location['x'], location['y'], location['theta'], floor)
        self.tcp_socket.send(send_data.encode("utf-8"))
        receive = self.tcp_socket.recv(1024)
        # receive = receive.decode("utf-8")
        if len(receive):
            receive = json.loads(receive)
            if receive['status'] == 'OK':
                print("坐标点位设置成功")
                return True
            elif receive['error_message'] != '':
                print("坐标点位设置失败")
                return False

    def forward(self, length: int) -> None:
        for _ in range(length):
            send_data = "/api/joy_control?angular_velocity={}&linear_velocity={}".format(0.0, 0.2)
            self.tcp_socket.send(send_data.encode("utf-8"))
            receive = self.tcp_socket.recv(1024)
            if len(receive): print(str(receive, encoding='utf-8'))
            time.sleep(0.2)

    def backward(self, length: int) -> None:
        for _ in range(length):
            send_data = "/api/joy_control?angular_velocity={}&linear_velocity={}".format(0.0, -0.2)
            self.tcp_socket.send(send_data.encode("utf-8"))
            receive = self.tcp_socket.recv(1024)
            if len(receive): print(str(receive, encoding='utf-8'))
            time.sleep(0.2)

    def rotate_right(self, angle: int) -> None:  # 30
        for _ in range(angle):
            send_data = "/api/joy_control?angular_velocity={}&linear_velocity={}".format(0.19, 0)
            self.tcp_socket.send(send_data.encode("utf-8"))
            receive = self.tcp_socket.recv(1024)
            if len(receive): print(str(receive, encoding='utf-8'))
            time.sleep(0.4)

    def rotate_left(self, angle: int) -> None:  # 30
        for _ in range(angle):
            send_data = "/api/joy_control?angular_velocity={}&linear_velocity={}".format(-0.4, 0)
            self.tcp_socket.send(send_data.encode("utf-8"))
            receive = self.tcp_socket.recv(1024)
            if len(receive): print(str(receive, encoding='utf-8'))

    def clear(self):
        receive = self.tcp_socket.recv(1024)

    def move_stop_or(self, flag=True):
        """进入或退出急停模式，默认进入
                 参数：
                     flag：true/false,进入或退出急停模式
                 返回值：状态或错误信息
        """
        if flag:
            send_data = "/api/estop?flag=" + "true"
            self.tcp_socket.send(send_data.encode("utf-8"))
            receive = self.tcp_socket.recv(1024)
        else:
            send_data = "/api/estop?flag=" + "true"
            self.tcp_socket.send(send_data.encode("utf-8"))
            receive = self.tcp_socket.recv(1024)
