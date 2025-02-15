# -*- coding: UTF-8 -*-
'''
@Project ：AIMechController 
@File    ：OnlyController.py
@Author  ：Lucio.YipengLi@outlook.com
@Date    ：2025/2/15 下午5:05 
'''
from exoskeleton_api import Exoskeleton
from coppeliasim_zmqremoteapi_client import RemoteAPIClient
import coppeliaSimType
import math


# 场景左右臂关节名
LeftJointName = ["/base_link1", "/link1_link2", "/link2_link3", "/link3_link4", "/link4_link5", "/link5_link6",
                 "/link6_link7"]
RightJointName = ["/base_link8", "/link8_link9", "/link9_link10", "/link10_link11", "/link11_link12", "/link12_link13",
                  "/link13_link14"]
# 左右臂关节对象
LeftJoints = []
RightJoints = []

def rad_to_deg(radian):
    # 弧度转角度
    return radian * 180 / math.pi


def deg_to_rad(degree):
    # 角度转弧度
    return degree * math.pi / 180


def angle_mistake_fix(raw_list):
    # 由于实物和仿真模型的有些关节角度关系呈现反数关系，需要手动给关节值打个补丁
    # PS： 改模型也行，但太麻烦了，不如直接乘数
    raw_list[0][2] *= -1
    raw_list[0][5] *= -1
    raw_list[1][1] *= -1
    raw_list[1][2] *= -1
    raw_list[1][3] *= -1
    raw_list[1][5] *= -1
    return raw_list

#  获取远程遥控接口，设置参数
client = RemoteAPIClient()
sim: coppeliaSimType.SimType = client.require('sim')
sim.setStepping(True)
sim.startSimulation()
obj = Exoskeleton(port="COM5")
# 防止代码的bug导致远程接口提前下线而仿真软件继续仿真
# 在进行仿真时必须慎重启动！因为远程脚本的提前下线而没有结束仿真会导致意想不到的结果！
try:
    # 获取全部两臂对象
    for name in RightJointName:
        print(name)
        RightJoints.append(sim.getObject(name))
    for name in LeftJointName:
        print(name)
        LeftJoints.append(sim.getObject(name))
    # 设置仿真时间为60s，到时间自动退出仿真
    while (t := sim.getSimulationTime()) < 60:
        # 得到所有现实外骨骼关节数据，并根据规则修补
        ControllerData = obj.get_all_data()
        ControllerData = angle_mistake_fix(ControllerData)
        # 分别设置到仿真模型各个关节的目标位置
        joint_num = 0
        for joint in LeftJoints:
            sim.setJointTargetPosition(joint, deg_to_rad(ControllerData[0][joint_num]))
            joint_num += 1
        joint_num = 0
        for joint in RightJoints:
            sim.setJointTargetPosition(joint, deg_to_rad(ControllerData[1][joint_num]))
            joint_num += 1
        # 注意时间
        print(sim.getSimulationTime())
        sim.step()
finally:
    # 结束退出仿真
    sim.stopSimulation()


