# -*- coding: UTF-8 -*-
'''
@Project ：CoppeliaSim 
@File    ：ControllerWithArm.py
@Author  ：Lucio.YipengLi@outlook.com
@Date    ：2025/2/25 下午3:20 
'''
from exoskeleton_api import Exoskeleton
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import coppeliaSimType
import math
import threading

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


def get_position_diff(init_position, new_position):
    c_list = [x - y for x, y in zip(init_position, new_position)]
    return c_list


def add_position_diff(init_position, add_position):
    c_list = [x + y for x, y in zip(init_position, add_position)]
    return c_list


class TaskControllerRead2Sim(threading.Thread):
    #  现实控制器仿真到仿真控制器，并改变target1的位置
    def __init__(self):
        super().__init__()

    def run(self):
        client = RemoteAPIClient()
        sim: coppeliaSimType.SimType = client.require('sim')
        sim.setStepping(True)
        sim.startSimulation()
        obj = Exoskeleton(port="COM5")
        obj.set_color(1, 0, 0, 255)
        try:
            init_num = 0
            for name in RightJointName:
                print(name)
                RightJoints.append(sim.getObject(name))
            for name in LeftJointName:
                print(name)
                LeftJoints.append(sim.getObject(name))
            MoveTest = sim.getObject("/MoveTest")
            MoveTest = sim.getObject("/Sphere")
            left_hand_point = sim.getObject("/left_hand_point")
            MT_init_position = sim.getObjectPosition(MoveTest, sim.handle_world)

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
            obj.set_color(1, 0, 255, 0)
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
                    point_init_position = sim.getObjectPosition(left_hand_point, sim.handle_world)
                    init_num += 1
                else:
                    new_position = sim.getObjectPosition(left_hand_point, sim.handle_world)
                    diff_position = get_position_diff(point_init_position, new_position)
                    MT_new_position = get_position_diff(MT_init_position, diff_position)
                    sim.setObjectPosition(MoveTest, MT_new_position, sim.handle_world)
        finally:
            sim.stopSimulation()


class TaskArmIK(threading.Thread):
    #  机械臂专门进行IK逆解的线程，跟随物体target1  #
    def __init__(self):
        super().__init__()

    def run(self):
        client = RemoteAPIClient()
        sim: coppeliaSimType.SimType = client.require('sim')
        simIK: coppeliaSimType.SimIKType = client.require('simIK')
        sim.setStepping(True)
        sim.startSimulation()
        try:
            simBase = sim.getObject("/NiryoOne")
            simTip = sim.getObject("/tip1")
            simTarget = sim.getObject("/target1")
            ikEnv = simIK.createEnvironment()
            ikGroup_ud = simIK.createGroup(ikEnv)
            simIK.setGroupCalculation(ikEnv, ikGroup_ud, simIK.method_pseudo_inverse, 0, 20)
            simIK.addElementFromScene(ikEnv, ikGroup_ud, simBase, simTip, simTarget, simIK.constraint_pose)

            ikGroup_d = simIK.createGroup(ikEnv)
            simIK.setGroupCalculation(ikEnv, ikGroup_d, simIK.method_damped_least_squares, 1, 99)
            simIK.addElementFromScene(ikEnv, ikGroup_d, simBase, simTip, simTarget, simIK.constraint_pose)

            while (t := sim.getSimulationTime()) < 20:
                # 简单方法
                res, *_ = simIK.handleGroup(ikEnv, ikGroup_ud, {'syncWorlds': True})
                if res != simIK.result_success:
                    simIK.handleGroup(ikEnv, ikGroup_d, {'syncWorlds': True})
                    sim.addLog(sim.verbosity_scriptwarnings, "IK solver failed.")
                sim.step()
        finally:
            sim.stopSimulation()


# Create Thread #
thread1 = TaskControllerRead2Sim()
thread2 = TaskArmIK()

# Start Thread and Join #
thread1.start()
thread2.start()

thread1.join()
thread2.join()

print("Over")
