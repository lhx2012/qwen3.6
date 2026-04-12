# Pro Soccer Online (PSO) 仿制项目 - 真实代码实现指南

**版本**: 1.0  
**引擎**: Unity 2022.3.48f1  
**服务器框架**: ET Framework (v8.1+)  
**网络同步**: 帧同步 (Lockstep)  
**目标**: 1:1 还原 PSO 操作手感与核心玩法，实现多人在线联机  

---

## 1. 项目目录结构规范

### 1.1 客户端目录结构 (Unity)
```text
Assets/
├── _Project/                  # 项目核心资源
│   ├── Scripts/               # C# 脚本
│   │   ├── Core/              # 核心架构 (单例、事件、对象池)
│   │   │   ├── GameApp.cs     # 游戏入口
│   │   │   ├── GameManager.cs # 全局管理器
│   │   │   ├── EventSystem.cs # 事件中心
│   │   │   └── ObjectPool.cs  # 对象池
│   │   ├── Network/           # 网络层 (对接 ET)
│   │   │   ├── ETClient.cs    # ET 客户端封装
│   │   │   ├── MessagePacker.cs
│   │   │   └── FrameSyncManager.cs # 帧同步核心
│   │   ├── Gameplay/          # 玩法逻辑
│   │   │   ├── Player/        
│   │   │   │   ├── PlayerController.cs  # 球员控制 (移动/转身)
│   │   │   │   ├── PlayerInput.cs       # 输入处理
│   │   │   │   ├── PlayerState.cs       # 状态机 (跑/停/滑铲)
│   │   │   │   └── PlayerStats.cs       # 属性 (速度/加速/平衡)
│   │   │   ├── Ball/          
│   │   │   │   ├── BallPhysics.cs       # 球物理模拟
│   │   │   │   └── BallTrajectory.cs    # 轨迹预测
│   │   │   ├── Match/         
│   │   │   │   ├── MatchManager.cs      # 比赛管理
│   │   │   │   ├── TeamManager.cs       # 队伍管理
│   │   │   │   └── ScoreBoard.cs        # 计分板
│   │   │   └── Mechanics/     
│   │   │       ├── PowerGauge.cs        # 力度条逻辑
│   │   │       ├── PassSystem.cs        # 传球计算
│   │   │       ├── ShotSystem.cs        # 射门计算
│   │   │       └── TackleSystem.cs      # 铲球判定
│   │   ├── Camera/            
│   │   │   └── MatchCamera.cs   # 比赛摄像机 (跟随/平滑)
│   │   ├── UI/                
│   │   │   ├── Lobby/         # 大厅界面
│   │   │   ├── Match/         # 比赛界面 (力度条/比分)
│   │   │   └── HUD/           # 血条/体力条
│   │   └── Utils/             # 工具类
│   ├── Prefabs/               # 预制体
│   │   ├── Players/           # 球员模型
│   │   ├── Ball/              # 足球
│   │   ├── Fields/            # 球场
│   │   └── UI/                # UI 预制体
│   ├── Animations/            # 动画控制器
│   ├── Art/                   # 美术资源
│   └── Configs/               # 配置表 (Excel/Lua)
├── Plugins/                   # 第三方插件 (ET.Runtime)
└── Scenes/                    # 场景
    ├── Login.unity
    ├── Lobby.unity
    └── Match.unity
```

### 1.2 服务器目录结构 (ET Framework)
```text
ETServer/
├── Proto/                     # 协议定义 (.proto)
│   ├── OuterMessage.proto     # 客户端直连消息
│   └── InnerMessage.proto     # 服务器内部消息
├── Model/                     # 数据模型
│   └── Module/
│       ├── Player/            # 玩家组件
│       └── Match/             # 比赛组件
├── Hotfix/                    # 热更逻辑 (核心玩法)
│   ├── Module/
│   │   ├── Login/             # 登录流程
│   │   ├── Match/             # 匹配逻辑
│   │   ├── FrameSync/         # 帧同步服务
│   │   └── GameLogic/         # 比赛逻辑 (服务端验证)
│   └── Init.cs                # 热更入口
├── HotfixView/                # 服务器端视图 (可选)
└── Tools/                     # 打包工具
```

---

## 2. 核心网络协议定义 (Protobuf)

必须严格定义 `.proto` 文件，这是前后端通信的基石。

### 2.1 登录与大厅协议 (`OuterMessage.proto`)
```protobuf
syntax = "proto3";
package ET;

// 请求登录
message C2G_LoginGate {
    int64 AccountId = 1;
    string Token = 2;
}

// 登录响应
message G2C_LoginGate {
    int32 ErrorCode = 1;
    int64 PlayerId = 2;
}

// 请求创建房间
message C2M_CreateMatch {
    int32 Mode = 1; // 1:快速, 2:排位
}

// 匹配成功通知
message M2C_MatchSuccess {
    int64 MatchId = 1;
    repeated PlayerInfo Players = 2;
}

message PlayerInfo {
    int64 PlayerId = 1;
    string Name = 2;
    int32 TeamId = 3; // 1:蓝队, 2:红队
}
```

### 2.2 帧同步协议 (`FrameSync.proto`)
**关键**: 所有操作必须转换为 `InputCommand` 发送到服务器，服务器广播 `FrameData`。

```protobuf
// 客户端上报操作
message C2G_FrameInput {
    int64 PlayerId = 1;
    int32 FrameIndex = 2;      // 当前帧号
    InputCommand Command = 3;
}

message InputCommand {
    float MoveX = 1;           // -1 ~ 1
    float MoveY = 2;           // -1 ~ 1
    bool BtnPass = 3;          // J 键
    bool BtnShot = 4;          // K 键
    bool BtnTackle = 5;        // L 键
    bool BtnSprint = 6;        // Shift
    int32 PowerGaugeStage = 7; // 力度条阶段 (0-3)
}

// 服务器广播帧数据
message G2C_FrameData {
    int32 FrameIndex = 1;
    repeated FramePlayerData Players = 2;
    FrameBallData Ball = 3;
}

message FramePlayerData {
    int64 PlayerId = 1;
    float PosX = 2;
    float PosY = 3;
    float Rot = 4;
    int32 AnimState = 5;
}

message FrameBallData {
    float PosX = 1;
    float PosY = 2;
    float VelX = 3;
    float VelY = 4;
}
```

---

## 3. 客户端核心代码实现逻辑

### 3.1 帧同步管理器 (`FrameSyncManager.cs`)
**职责**: 缓存输入，发送输入，接收服务器帧，回放帧。

```csharp
using System.Collections.Generic;
using UnityEngine;

public class FrameSyncManager : MonoBehaviour
{
    public static FrameSyncManager Instance;
    
    // 配置
    public int TickRate = 60; // 60 FPS 逻辑帧
    public int MaxBufferFrames = 5; // 最大缓冲帧数
    
    // 状态
    private int _currentFrameIndex = 0;
    private int _serverConfirmedFrame = 0;
    private Queue<InputCommand> _inputQueue = new Queue<InputCommand>();
    private Dictionary<int, FrameData> _frameBuffer = new Dictionary<int, FrameData>();
    
    void Awake() { Instance = this; }
    
    void Update()
    {
        // 1. 采集本地输入 (每帧)
        if (Time.frameCount % (60 / TickRate) == 0)
        {
            CaptureInput();
        }
        
        // 2. 发送输入到服务器
        SendInputToServer();
        
        // 3. 执行逻辑帧 (如果缓冲区有数据)
        if (_frameBuffer.ContainsKey(_currentFrameIndex))
        {
            ReplayFrame(_frameBuffer[_currentFrameIndex]);
            _currentFrameIndex++;
        }
        else
        {
            // 预测逻辑 (可选): 如果没收到服务器帧，先按本地输入跑
            // 等服务器帧到了再修正 (橡皮筋效果)
        }
    }
    
    void CaptureInput()
    {
        var cmd = new InputCommand
        {
            MoveX = Input.GetAxis("Horizontal"),
            MoveY = Input.GetAxis("Vertical"),
            BtnPass = Input.GetKeyDown(KeyCode.J),
            BtnShot = Input.GetKeyDown(KeyCode.K),
            BtnTackle = Input.GetKeyDown(KeyCode.L),
            BtnSprint = Input.GetKey(KeyCode.LeftShift)
        };
        _inputQueue.Enqueue(cmd);
    }
    
    void SendInputToServer()
    {
        // 实际项目中调用 ET.Network.Send
        // Network.Send(new C2G_FrameInput { FrameIndex = _currentFrameIndex, Command = cmd });
    }
    
    public void OnReceiveFrameData(FrameData data)
    {
        if (_frameBuffer.ContainsKey(data.FrameIndex)) return;
        _frameBuffer[data.FrameIndex] = data;
        
        // 清理旧帧
        if (_frameBuffer.Count > MaxBufferFrames)
        {
            int minKey = int.MaxValue;
            foreach(var k in _frameBuffer.Keys) if(k < minKey) minKey = k;
            _frameBuffer.Remove(minKey);
        }
    }
    
    void ReplayFrame(FrameData data)
    {
        // 遍历所有玩家，强制设置位置
        foreach(var p in data.Players)
        {
            var player = PlayerManager.Get(p.PlayerId);
            if(player != null)
            {
                player.transform.position = new Vector3(p.PosX, 0, p.PosY);
                player.transform.rotation = Quaternion.Euler(0, p.Rot, 0);
                player.SetAnimState(p.AnimState);
            }
        }
        
        // 更新球
        Ball.Instance.SetState(data.Ball.PosX, data.Ball.PosY, data.Ball.VelX, data.Ball.VelY);
    }
}
```

### 3.2 球员控制器 (`PlayerController.cs`)
**职责**: 解析输入，应用物理，播放动画。**注意：在帧同步模式下，位置由 FrameSyncManager 驱动，但本地预览需要预测。**

```csharp
using UnityEngine;

[RequireComponent(typeof(CharacterController))]
public class PlayerController : MonoBehaviour
{
    [Header("Stats")]
    public float MaxSpeed = 7.0f;
    public float Acceleration = 20.0f;
    public float TurnSpeed = 10.0f;
    
    private CharacterController _cc;
    private Vector3 _velocity;
    private Animator _animator;
    
    // 状态
    private bool _isGrounded;
    private int _animStateHash_Run = Animator.StringToHash("Run");
    
    void Awake()
    {
        _cc = GetComponent<CharacterController>();
        _animator = GetComponent<Animator>();
    }
    
    // 此方法由 FrameSyncManager 调用，用于强制同步
    public void ForceSync(Vector3 pos, float rot, int animState)
    {
        transform.position = pos;
        transform.rotation = Quaternion.Euler(0, rot, 0);
        _animator.SetInteger("State", animState);
    }
    
    // 本地预测用 (仅在未收到服务器帧时运行)
    public void LocalMove(Vector2 input, bool sprint)
    {
        float targetSpeed = MaxSpeed * (sprint ? 1.5f : 1.0f);
        
        // 移动方向
        if (input.magnitude > 0.1f)
        {
            Vector3 targetDir = new Vector3(input.x, 0, input.y).normalized;
            float targetRot = Mathf.Atan2(targetDir.x, targetDir.z) * Mathf.Rad2Deg;
            
            // 平滑旋转
            float currentRot = transform.eulerAngles.y;
            float delta = Mathf.DeltaAngle(currentRot, targetRot);
            transform.Rotate(0, delta * TurnSpeed * Time.deltaTime, 0);
            
            // 加速
            _velocity = Vector3.MoveTowards(_velocity, targetDir * targetSpeed, Acceleration * Time.deltaTime);
        }
        else
        {
            // 减速
            _velocity = Vector3.MoveTowards(_velocity, Vector3.zero, Acceleration * 2 * Time.deltaTime);
        }
        
        _cc.Move(_velocity * Time.deltaTime);
        
        // 动画
        _animator.SetFloat("Speed", _velocity.magnitude);
    }
}
```

### 3.3 力度条系统 (`PowerGauge.cs`)
**核心机制**: 按住按键 -> 力度条增长 -> 松开按键 -> 确定力度。

```csharp
using UnityEngine;
using UnityEngine.UI;

public class PowerGauge : MonoBehaviour
{
    public static PowerGauge Instance;
    
    [Header("UI")]
    public Slider powerSlider;
    public GameObject gaugePanel;
    
    [Header("Config")]
    public float FillSpeed = 2.0f; // 充满所需秒数
    public float OscillateSpeed = 3.0f; // 摆动速度
    
    private enum GaugeState { Hidden, Filling, Oscillating, Locked }
    private GaugeState _state = GaugeState.Hidden;
    private float _currentValue = 0f; // 0~1
    private float _direction = 1f; // 1:增，-1:减
    
    void Awake() { Instance = this; gaugePanel.SetActive(false); }
    
    public void StartCharge()
    {
        if (_state == GaugeState.Hidden)
        {
            _state = GaugeState.Filling;
            _currentValue = 0f;
            gaugePanel.SetActive(true);
        }
    }
    
    public void ReleaseCharge(out float power)
    {
        if (_state == GaugeState.Filling)
        {
            _state = GaugeState.Oscillating;
            // 记录当前值作为初始摆动点 (简化版直接锁定，完整版会摆动)
            // PSO 机制：第一次点击开始，第二次点击停止在某个值，第三次点击确认方向/精度
            // 这里简化为：按住蓄力，松开即释放 (适合初版)
            power = _currentValue;
            _state = GaugeState.Hidden;
            gaugePanel.SetActive(false);
            return;
        }
        power = 0f;
    }
    
    void Update()
    {
        if (_state == GaugeState.Filling)
        {
            _currentValue += Time.deltaTime / FillSpeed;
            if (_currentValue >= 1f)
            {
                _currentValue = 1f;
                _state = GaugeState.Oscillating; // 满了之后开始摆动
            }
        }
        else if (_state == GaugeState.Oscillating)
        {
            // 模拟指针来回摆动
            _currentValue += _direction * Time.deltaTime * OscillateSpeed;
            if (_currentValue >= 1f || _currentValue <= 0f)
            {
                _direction *= -1f;
                _currentValue = Mathf.Clamp(_currentValue, 0, 1);
            }
        }
        
        powerSlider.value = _currentValue;
    }
    
    // 供外部调用获取最终力度
    public float GetCurrentPower() => _currentValue;
}
```

### 3.4 球的物理模拟 (`BallPhysics.cs`)
**注意**: 为了帧同步，球物理必须使用**确定性物理**或完全由服务器计算。这里使用简化的运动学公式。

```csharp
using UnityEngine;

public class BallPhysics : MonoBehaviour
{
    public static BallPhysics Instance;
    
    [Header("Physics")]
    public float Friction = 0.98f; // 地面摩擦
    public float AirResistance = 0.99f;
    public float MaxSpeed = 30f;
    
    private Vector3 _position;
    private Vector3 _velocity;
    private float _height; // Z 轴高度 (2.5D)
    
    void Awake() { Instance = this; }
    
    // 由服务器帧数据驱动
    public void SetState(float x, float y, float vx, float vy)
    {
        _position = new Vector3(x, 0, y);
        _velocity = new Vector3(vx, 0, vy);
        transform.position = _position;
    }
    
    // 本地预测更新 (如果没有收到服务器帧)
    public void LocalUpdate()
    {
        _position += _velocity * Time.fixedDeltaTime;
        _velocity *= Friction;
        
        // 速度阈值停止
        if (_velocity.magnitude < 0.1f) _velocity = Vector3.zero;
        
        transform.position = _position;
    }
    
    // 被踢
    public void Kick(Vector3 direction, float force)
    {
        _velocity = direction.normalized * Mathf.Min(force, MaxSpeed);
        // 添加一点随机旋转模拟真实感 (需确保随机种子同步)
    }
}
```

---

## 4. 服务器端核心逻辑 (ET Framework)

### 4.1 帧同步服务 (`FrameSyncComponent.cs`)
**位置**: `Model/Module/FrameSync` 或 `Hotfix/Module/FrameSync`

```csharp
using ET;
using System.Collections.Generic;

namespace ET
{
    [ObjectSystem]
    public class FrameSyncComponentSystem : ObjectSystem<FrameSyncComponent>
    {
        public override void Update(FrameSyncComponent self)
        {
            // 1. 收集本帧所有玩家的输入
            // 2. 检查是否所有玩家都提交了输入 (或超时)
            // 3. 计算下一帧状态 (跑服逻辑)
            // 4. 广播 FrameData 给所有客户端
            
            // 伪代码:
            // if (self.IsReadyForNextFrame())
            // {
            //     self.CalculateNextFrame();
            //     self.BroadcastFrame();
            //     self.CurrentFrameIndex++;
            // }
        }
    }
    
    public class FrameSyncComponent : Entity, IAwake, IDestroy
    {
        public int CurrentFrameIndex { get; set; }
        public Dictionary<long, InputCommand> FrameInputs { get; set; } = new();
        
        public void AddInput(long playerId, InputCommand cmd)
        {
            FrameInputs[playerId] = cmd;
        }
        
        // 核心：服务端计算逻辑 (防作弊)
        public void CalculateNextFrame()
        {
            // 遍历所有玩家，根据输入计算新位置
            // 遍历球，根据碰撞计算新位置
            // 将结果存入 FrameData
        }
    }
}
```

### 4.2 匹配逻辑 (`MatchHandler.cs`)
```csharp
using ET;
using System;

namespace ET
{
    [MessageHandler(SceneType.Match)]
    public class C2M_CreateMatchHandler : AMRpcHandler<C2M_CreateMatch, M2C_CreateMatch>
    {
        protected override async STask Run(Unit unit, C2M_CreateMatch message, Action<M2C_CreateMatch> reply)
        {
            var response = new M2C_CreateMatch();
            
            // 1. 将玩家加入匹配队列
            // 2. 匹配策略：寻找分数相近的玩家 (4v4)
            // 3. 凑齐 8 人后，创建 MatchScene
            // 4. 通知所有玩家进入场景
            
            // 示例:
            // var matchScene = await Game.Scene.GetComponent<MatchQueueComponent>().CreateMatch(message.Mode);
            // response.MatchId = matchScene.Id;
            
            reply(response);
        }
    }
}
```

---

## 5. 详细开发步骤 (Step-by-Step)

### 第一阶段：基础设施搭建 (第 1-2 周)

#### Day 1-3: 环境配置
1.  **安装 Unity 2022.3.48**: 确保安装 Android/iOS Build Support。
2.  **拉取 ET 框架**: 
    ```bash
    git clone https://github.com/egametang/ET.git
    git checkout v8.1 # 或最新稳定版
    ```
3.  **配置 VS/Rider**: 导入 `ET.sln`，确保编译通过。
4.  **创建 Unity 项目**: 在 `ET/Unity/Assets` 下建立 `_Project` 目录结构。

#### Day 4-7: 网络连通性
1.  **定义 Proto**: 编写 `Login.proto` 和 `FrameSync.proto`。
2.  **生成代码**: 运行 ET 的 `Proto2CS` 工具生成 C# 代码。
3.  **实现登录**:
    - 客户端：写死账号密码，连接 GateServer。
    - 服务端：处理 `C2G_LoginGate`，返回 `PlayerId`。
4.  **测试**: 运行 `Start.bat`，客户端连接，Console 输出 "Login Success"。

#### Day 8-14: 帧同步骨架
1.  **服务端时钟**: 实现 `FrameSyncComponent` 的定时器，每秒固定触发 60 次 `Update`。
2.  **输入回显**: 客户端发送 `C2G_FrameInput` -> 服务端存入缓冲 -> 服务端广播 `G2C_FrameData` (原样返回输入)。
3.  **客户端回放**: 接收 `G2C_FrameData`，打印日志，确认延迟在 50ms 以内。

### 第二阶段：核心玩法实现 (第 3-6 周)

#### Day 15-21: 球员移动
1.  **角色建模**: 导入低模球员，设置 Animator (Idle, Run, Turn)。
2.  **物理控制**: 实现 `PlayerController`，使用 `CharacterController`。
3.  **同步验证**: 
    - 客户端按下 W，发送输入。
    - 服务端计算新坐标 `(x + speed*dt, z)`。
    - 广播坐标，客户端插值移动。
    - **关键点**: 解决 "瞬移" 问题，客户端使用线性插值 (Lerp) 平滑过渡。

#### Day 22-28: 球与交互
1.  **球体物理**: 实现 `BallPhysics`，模拟滚动摩擦。
2.  **碰撞检测**: 
    - 简单的圆形碰撞检测 (距离 < 半径和)。
    - 当球员触碰球时，将球速度设为球员速度 + 额外推力。
3.  **力度条**: 实现 `PowerGauge` UI，绑定到传球/射门逻辑。

#### Day 29-35: 传球与射门
1.  **传球逻辑**: 
    - 计算最近队友方向。
    - 根据力度条决定球速。
    - 服务端验证：是否在射程内，是否有遮挡。
2.  **射门逻辑**: 
    - 检测球门区域。
    - 判定进球：球完全越过门线且无防守队员触碰。
    - 更新比分，重置球位置。

#### Day 36-42: 游戏流程
1.  **状态机**: 实现比赛状态 (准备中 -> 进行中 -> 进球回放 -> 结束)。
2.  **倒计时**: 服务端同步比赛时间。
3.  **胜负判定**: 时间到或分数达标，结算比赛。

### 第三阶段：完善与优化 (第 7-9 周)

1.  **摄像机**: 实现 `MatchCamera`，平滑跟随球的位置，限制在球场边界内。
2.  **动画融合**: 使用 BlendTree 实现 8 方向跑步动画平滑切换。
3.  **断线重连**: 
    - 客户端断开后重新连接。
    - 服务端缓存最近 300 帧 `FrameData`。
    - 重连时一次性发送历史帧，客户端快速回放追上进度。
4.  **性能优化**: 
    - 对象池管理球员和球。
    - GC 优化 (避免 Update 中 new 对象)。

### 第四阶段：测试与部署 (第 10-11 周)

1.  **多端测试**: Windows 编辑器开 8 个窗口互测。
2.  **压力测试**: 模拟高延迟 (使用 Clumsy 工具)，调整插值算法。
3.  **服务器部署**: 
    - 购买阿里云/腾讯云 (Ubuntu 20.04)。
    - 安装 Docker, MongoDB。
    - 部署 ET Server (Dotnet 6.0)。
4.  **打包发布**: 构建 Windows .exe 和 Android .apk。

---

## 6. 关键技术难点与解决方案

### 6.1 操作手感一致性 (最重要)
*   **问题**: 帧同步下，不同帧率的设备会导致移动距离不同。
*   **解决**: 
    1.  逻辑帧率固定 60Hz (`FixedUpdate`)。
    2.  移动公式使用 `Distance = Speed * (1/60)` 而不是 `Time.deltaTime`。
    3.  渲染帧与逻辑帧分离，渲染只做插值。

### 6.2 橡皮筋效应 (Rubber-banding)
*   **问题**: 本地预测跑远了，服务器帧回来强制拉回，导致人物瞬移。
*   **解决**: 
    1.  **延迟输入**: 客户端故意延迟 3 帧执行本地输入，等待服务器确认。
    2.  **平滑修正**: 如果偏差 < 0.5 米，下一帧缓慢修正；如果 > 0.5 米，立即瞬移。

### 6.3 球的确定性物理
*   **问题**: Unity 自带 PhysX 不是确定性的，不同设备球轨迹不同。
*   **解决**: 
    1.  **方案 A (推荐)**: 放弃物理引擎，手写运动学公式 (`Pos += Vel * dt`, `Vel *= Friction`)。
    2.  **方案 B**: 仅服务器计算球物理，客户端纯表现。

---

## 7. 资源配置清单

| 资源类型 | 规格要求 | 数量 | 备注 |
| :--- | :--- | :--- | :--- |
| **球员模型** | 低模 (<5000 面), 骨骼绑定 | 10 | 不同发型/肤色区分 |
| **球场** | 2048x2048 贴图 | 2 | 草地/室内地板 |
| **动画** | Mixamo 或手K | 20+ | 跑、停、转、传、射、铲、庆祝 |
| **UI 图片** | PNG, 9 宫格 | 50+ | 按钮、力度条、图标 |
| **音效** | MP3/WAV | 30+ | 踢球声、哨声、观众欢呼 |

---

## 8. 验收标准

1.  **功能验收**:
    - [ ] 8 人能同时进入房间。
    - [ ] WASD 移动无延迟感，转向平滑。
    - [ ] 力度条操作精准，传球/射门力度符合预期。
    - [ ] 进球判定准确，比分实时同步。
    - [ ] 断线重连后能继续比赛。
2.  **性能验收**:
    - [ ] 客户端帧率稳定 60FPS (PC)。
    - [ ] 服务器支持至少 10 个房间并发。
    - [ ] 网络延迟 < 100ms 时无明显瞬移。

---

## 附录：常用命令

**启动服务器 (本地):**
```bash
cd ET/Tools/Bin
dotnet ET.Server.dll --Process=1 --Config=Dev
```

**生成 Proto 代码:**
```bash
cd ET/Tools
dotnet build
dotnet ET.Tools.dll --Proto2CS
```

**Unity 打包命令行:**
```bash
"C:\Program Files\Unity\Hub\Editor\2022.3.48f1\Editor\Unity.exe" -batchmode -quit -projectPath "D:/ET/Unity" -executeMethod BuildScript.BuildWindows
```

---

**开发者提示**: 
本项目核心在于**帧同步的稳定性**。前期不要追求画面华丽，先保证 8 个方块人在服务器上跑动位置一致。一旦网络同步底层稳固，后续替换美术资源即可快速完成产品。
