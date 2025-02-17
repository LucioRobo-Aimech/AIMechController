<h1>AIMechController</h1>
<p>本项目是本人的毕业设计，基于外骨骼和仿真软件，设计一套遥操作外骨骼系统，主要功能是机器学习数据采集、遥操作控制、机器仿真控制</p>
<p>Author： Lucio.YipengLi@Outlook.com</p>
<p>Date:  2025/01 - 2025/05 </p>

<h2>文件结构</h2>

```markdown
AIMechController/
│
├── PythonScript/
│   └── OnlyController.py
│
├── ReadmeSource/
│   └── Images
│       ├── ControllerWithCuboid.gif
│       └── OnlyController.gif
│
└── Scene/
    └── OnlyController.ttt
```

<h2> 项目组成 </h2>
<h3> 1.OnlyController</h3>
<p>本项目是在CoppeliaSim中测试大象myController所用，将现实外骨骼的关节角度设定在仿真环境中的外骨骼。</p>
<p align="center">
  <img src="ReadmeSource/Images/OnlyController.gif" alt="OnlyController" width = "640" height = "360"/>
</p>
<br>
<h3> 2.ControllerWithCuboid</h3>
<p>本项目是在CoppeliaSim中测试大象myController所用，将仿真外骨骼的手柄位置实时控制到仿真方块上，实现手柄位置对仿真方块位置的控制。</p>
<p align="center">
  <img src="ReadmeSource/Images/ControllerWithCuboid.gif" alt="ControllerWithCuboid" width = "640" height = "360"/>
</p>


