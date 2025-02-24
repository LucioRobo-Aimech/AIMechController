# -*- coding: UTF-8 -*-
'''
@Project ：CoppeliaSim 
@File    ：ControllerTestIK.py
@Author  ：Lucio.YipengLi@outlook.com
@Date    ：2025/2/15 下午7:34 
'''
from exoskeleton_api import Exoskeleton
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import coppeliaSimType
import math

LeftJointName = ["/base_link1", "/link1_link2", "/link2_link3", "/link3_link4", "/link4_link5", "/link5_link6",
             "/link6_link7"]
RightJointName = ["/base_link8", "/link8_link9", "/link9_link10", "/link10_link11", "/link11_link12", "/link12_link13",
             "/link13_link14"]
LeftJoints = []
RightJoints = []

def rad_to_deg(radian):
    """
    将弧度转换为角度
    参数:
        radian (float): 弧度值
    返回:
        float: 角度值
    """
    return radian * 180 / math.pi


def deg_to_rad(degree):
    """
    将角度转换为弧度
    参数:
        degree (float): 角度值
    返回:
        float: 弧度值
    """
    return degree * math.pi / 180

def angle_mistake_fix(raw_list):
    raw_list[0][2] *= -1
    raw_list[0][5] *= -1
    raw_list[1][1] *= -1
    raw_list[1][2] *= -1
    raw_list[1][3] *= -1
    raw_list[1][5] *= -1
    return raw_list

def get_position_diff(init_position,new_position):
    c_list = [x - y for x, y in zip(init_position, new_position)]
    return c_list

def add_position_diff(init_position,add_position):
    c_list = [x + y for x, y in zip(init_position, add_position)]
    return c_list

client = RemoteAPIClient()
sim: coppeliaSimType.SimType = client.require('sim')
sim.setStepping(True)
sim.startSimulation()
obj = Exoskeleton(port="COM5")

try:
    init_num = 0
    for name in RightJointName:
        print(name)
        RightJoints.append(sim.getObject(name))
    for name in LeftJointName:
        print(name)
        LeftJoints.append(sim.getObject(name))
    MoveTest = sim.getObject("/MoveTest")
    left_hand_point = sim.getObject("/left_hand_point")
    MT_init_position = sim.getObjectPosition(MoveTest,sim.handle_world)

    #  让默认仿真模型先跑到现实转角
    while (t := sim.getSimulationTime()) < 3:
        ControllerData = obj.get_all_data()
        ControllerData = angle_mistake_fix(ControllerData)
        joint_num = 0
        for joint in LeftJoints:
            sim.setJointTargetPosition(joint, deg_to_rad(ControllerData[0][joint_num]))
            joint_num += 1
        joint_num = 0
        for joint in RightJoints:
            sim.setJointTargetPosition(joint, deg_to_rad(ControllerData[1][joint_num]))
            joint_num += 1
        sim.step()
    # 实际工作区间
    while (t := sim.getSimulationTime()) < 20:
        ControllerData = obj.get_all_data()
        ControllerData = angle_mistake_fix(ControllerData)
        joint_num = 0
        for joint in LeftJoints:
            sim.setJointTargetPosition(joint, deg_to_rad(ControllerData[0][joint_num]))
            joint_num += 1
        joint_num = 0
        for joint in RightJoints:
            sim.setJointTargetPosition(joint, deg_to_rad(ControllerData[1][joint_num]))
            joint_num += 1
        # print(sim.getSimulationTime())
        sim.step()
        if init_num == 0:
            point_init_position = sim.getObjectPosition(left_hand_point,sim.handle_world)
            init_num +=1
        else:
            new_position = sim.getObjectPosition(left_hand_point,sim.handle_world)
            diff_position = get_position_diff(point_init_position,new_position)
            print(diff_position)
            MT_new_position = get_position_diff(MT_init_position,diff_position)
            sim.setObjectPosition(MoveTest,MT_new_position,sim.handle_world)
finally:
    sim.stopSimulation()