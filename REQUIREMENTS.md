# Pro Soccer Online 仿制项目需求文档

## 1. 项目概述

### 1.1 项目名称
**Open Soccer Online** - 基于 ET 框架的在线足球游戏

### 1.2 项目目标
- 完全复刻《Pro Soccer Online》的核心玩法和操作体验
- 使用 GitHub 上的 ET 框架作为服务器后端
- 实现完整的多人在线足球对战功能
- 支持实时联网对战

### 1.3 技术栈
- **客户端**: Unity 2022.3.48 LTS
- **服务器**: ET 框架 (https://github.com/egametang/ET)
- **网络协议**: protobuf + TCP/WebSocket
- **数据库**: MongoDB (可选，用于数据存储)
- **版本控制**: Git

---

## 2. 游戏核心功能需求

### 2.1 游戏模式

#### 2.1.1 主要模式

1. **快速匹配 (Quick Match)**
   - 5v5 标准比赛
   - 自动匹配系统
   - 随机球队选择

2. **好友对战 (Friend Match)**
   - 创建房间
   - 邀请好友
   - 自定义球队和规则

3. **排位赛 (Ranked Match)**
   - ELO 积分系统
   - 段位排名
   - 赛季奖励

4. **训练模式 (Training Mode)**
   - 单人练习
   - 技能训练
   - 射门练习

#### 2.1.2 比赛规则
- 比赛时长：5 分钟/半场 (可配置)
- 球员数量：5v5 (包括守门员)
- 越位规则：启用/禁用 (可配置)
- 犯规系统：黄牌/红牌
- 加时赛和点球大战

### 2.2 操作控制系统 (1:1 复刻 Pro Soccer Online)

#### 2.2.1 基础移动操作

| 操作 | 输入方式 | 说明 |
|------|----------|------|
| 移动球员 | WASD / 方向键 | 8 方向移动 |
| 冲刺 | Shift + 移动 | 加速跑动，消耗体力 |
| 切换球员 | Q / E | 切换控制的球员 |
| 手动切换 | 右摇杆 / 鼠标 | 精确选择目标球员 |

#### 2.2.2 进攻操作

| 操作 | 输入方式 | 说明 |
|------|----------|------|
| 短传 | J / X | 短距离传球，力度可控 |
| 长传 | K / A | 长距离传球，抛物线轨迹 |
| 射门 | L / B | 射门，力度和方向可控 |
| 大力射门 | Shift + 射门 | 强力射门，精度降低 |
| 挑射 | 上 + 射门 | 高弧线射门 |
| 低射 | 下 + 射门 | 贴地射门 |
| 盘带 | 移动 + 空格 | 近距离控球 |
| 技能动作 | U / Y | 花式动作 (马赛回旋等) |
| 直塞球 | I / △ | 穿透性传球 |

#### 2.2.3 防守操作

| 操作 | 输入方式 | 说明 |
|------|----------|------|
| 抢断 | J / X | 尝试断球 |
| 铲球 | K / A | 滑铲断球 (有犯规风险) |
| 施压 | L / B | 紧逼持球球员 |
| 门将出击 | Shift + 门将切换 | 守门员出击 |
| 造越位 | 战术按钮 | 防线前移制造越位 |

#### 2.2.4 特殊操作

| 操作 | 输入方式 | 说明 |
|------|----------|------|
| 战术切换 | 方向键 + 功能键 | 改变球队战术 |
| 换人 | Pause + 选择 | 请求换人 |
| 暂停 | Esc / Start | 暂停比赛 |
| 视角切换 | V / R3 | 切换摄像机角度 |
| 语音聊天 | T | 队伍语音 |

#### 2.2.5 操作力度系统
- **力度条机制**: 按住按键时间决定力度
- **方向控制**: 左摇杆/方向键控制传球/射门方向
- **组合键**: 多个按键组合触发特殊动作

### 2.3 球员系统

#### 2.3.1 球员属性
```
- 速度 (Speed): 移动速度
- 加速度 (Acceleration): 加速能力
- 射门 (Shooting): 射门精度和力量
- 传球 (Passing): 传球精度
- 盘带 (Dribbling): 控球能力
- 防守 (Defending): 抢断和拦截
- 头球 (Heading): 争顶能力
- 体力 (Stamina): 影响冲刺和持续表现
- 守门 (Goalkeeping): 守门员专用属性
```

#### 2.3.2 球员状态
- 体力值动态变化
- 士气系统
- 受伤系统
- 红黄牌累积

#### 2.3.3 球员成长
- 经验值系统
- 等级提升
- 属性点分配
- 技能解锁

### 2.4 球队管理系统

#### 2.4.1 球队创建
- 自定义队名、队徽、球衣
- 主场球场选择
- 球队配色方案

#### 2.4.2 阵容管理
- 阵型选择 (4-3-3, 4-4-2, 3-5-2 等)
- 球员位置安排
- 替补席管理
- 队长任命

#### 2.4.3 战术设置
- 进攻风格 (控球/反击/边路)
- 防守策略 (压迫/收缩/造越位)
- 定位球战术
- 换人策略

### 2.5 比赛系统

#### 2.5.1 物理引擎
- 球的物理模拟 (重力、摩擦力、弹性)
- 碰撞检测 (球员 - 球、球员 - 球员、球 - 门柱)
- 轨迹预测
- 天气影响 (雨天球速快，雪天球速慢)

#### 2.5.2 AI 系统
- 队友 AI 行为树
- 对手 AI 难度等级
- 守门员 AI
- 定位球 AI 跑位

#### 2.5.3 裁判系统
- 犯规判定
- 越位判定
- 判罚执行 (任意球、点球、角球)
- VAR 回放 (可选)

#### 2.5.4 比赛事件
- 进球动画和庆祝
- 扑救特写
- 犯规回放
- 精彩瞬间捕捉

### 2.6 用户界面

#### 2.6.1 主菜单
- 开始游戏
- 在线匹配
- 好友列表
- 球队管理
- 商店
- 设置
- 退出

#### 2.6.2 比赛界面
- 比分显示
- 比赛时间
- 球员体力条
- 小地图
- 操作提示
- 聊天窗口
- 战术板

#### 2.6.3 结算界面
- 比赛数据统计
- 球员评分
- 经验值和奖励
- 录像回放选项

---

## 3. 服务器架构设计 (基于 ET 框架)

### 3.1 ET 框架集成

#### 3.1.1 ET 框架获取与配置
```bash
# 克隆 ET 框架
git clone https://github.com/egametang/ET.git

# 切换到稳定版本
cd ET
git checkout v8.0  # 或最新稳定版本

# 初始化子模块
git submodule update --init --recursive
```

#### 3.1.2 项目结构
```
OpenSoccerOnline/
├── Client/                    # Unity 客户端
│   ├── Assets/
│   │   ├── Scripts/
│   │   │   ├── ET/           # ET 客户端代码
│   │   │   ├── Game/         # 游戏逻辑
│   │   │   │   ├── Module/
│   │   │   │   │   ├── Player/
│   │   │   │   │   ├── Match/
│   │   │   │   │   ├── Ball/
│   │   │   │   │   └── UI/
│   │   │   │   └── ...
│   │   │   └── ...
│   │   ├── Resources/
│   │   ├── Scenes/
│   │   └── ...
│   └── ...
├── Server/                    # ET 服务器
│   ├── Modules/
│   │   ├── Gate/            # 网关服务器
│   │   ├── Login/           # 登录服务器
│   │   ├── Match/           # 匹配服务器
│   │   ├── Game/            # 游戏逻辑服务器
│   │   ├── DB/              # 数据库服务器
│   │   └── Manager/         # 管理服务器
│   └── ...
├── Proto/                     # Protobuf 协议定义
│   └── soccer.proto
├── Tools/                     # 开发工具
└── README.md
```

### 3.2 服务器模块设计

#### 3.2.1 Gate 服务器 (网关)
**功能**:
- 客户端连接入口
- 消息转发
- 会话管理
- 负载均衡

**配置**:
```json
{
  "gate": {
    "listenPort": 10001,
    "outerIP": "0.0.0.0",
    "outerPort": 10001,
    "maxConnection": 10000
  }
}
```

#### 3.2.2 Login 服务器 (登录)
**功能**:
- 用户认证
- 账号注册
- Token 生成
- 玩家数据加载

**协议消息**:
```protobuf
// 登录请求
message C2G_LoginRequest {
  string account = 1;
  string password = 2;
}

// 登录响应
message G2C_LoginResponse {
  int32 errorCode = 1;
  string token = 2;
  int64 playerId = 3;
}
```

#### 3.2.3 Match 服务器 (匹配)
**功能**:
- 匹配队列管理
- ELO 算法实现
- 房间创建
- 匹配结果通知

**匹配流程**:
```
1. 玩家发起匹配请求
2. 加入匹配队列
3. 根据 ELO 分数搜索对手
4. 找到合适对手后创建房间
5. 通知所有玩家进入游戏服务器
6. 启动比赛
```

#### 3.2.4 Game 服务器 (游戏逻辑)
**核心功能**:
- 比赛状态管理
- 球员位置同步
- 球的物理计算
- 碰撞检测
- 事件判定 (进球、犯规等)
- 反作弊检测

**帧同步设计**:
```csharp
// 帧率配置
public const int FrameRate = 60; // 60FPS
public const int FrameInterval = 16; // 16ms

// 输入缓冲
public class InputBuffer
{
    public long FrameIndex { get; set; }
    public PlayerInput Input { get; set; }
}

// 状态快照
public class GameStateSnapshot
{
    public long FrameIndex { get; set; }
    public Vector3 BallPosition { get; set; }
    public Vector3[] PlayerPositions { get; set; }
    public int Score { get; set; }
}
```

#### 3.2.5 DB 服务器 (数据库)
**功能**:
- 玩家数据持久化
- 比赛记录存储
- 排行榜数据
- 物品库存

**数据结构**:
```csharp
// 玩家数据
public class PlayerData
{
    public long Id { get; set; }
    public string Account { get; set; }
    public string Nickname { get; set; }
    public int Level { get; set; }
    public int Exp { get; set; }
    public int ELO { get; set; }
    public List<long> PlayerCards { get; set; }
    public Dictionary<string, object> Settings { get; set; }
    public DateTime CreateTime { get; set; }
    public DateTime LastLoginTime { get; set; }
}

// 比赛记录
public class MatchRecord
{
    public long Id { get; set; }
    public long MatchId { get; set; }
    public List<long> PlayerIds { get; set; }
    public int Team1Score { get; set; }
    public int Team2Score { get; set; }
    public DateTime StartTime { get; set; }
    public DateTime EndTime { get; set; }
    public MatchType MatchType { get; set; }
}
```

### 3.3 网络协议设计

#### 3.3.1 协议文件 (soccer.proto)
```protobuf
syntax = "proto3";

package soccer;

// ========== 基础消息 ==========

// 玩家输入
message PlayerInput {
    int32 playerId = 1;
    float moveX = 2;          // 移动 X 轴 (-1 ~ 1)
    float moveY = 3;          // 移动 Y 轴 (-1 ~ 1)
    bool sprint = 4;          // 是否冲刺
    int32 actionType = 5;     // 动作类型 (0:无，1:传球，2:射门...)
    float actionPower = 6;    // 动作力度 (0 ~ 1)
    float actionDirection = 7;// 动作方向 (角度)
    int64 frameIndex = 8;     // 帧索引
}

// 球员状态
message PlayerState {
    int32 playerId = 1;
    float posX = 2;
    float posY = 3;
    float posZ = 4;
    float rotY = 5;
    float speed = 6;
    float stamina = 7;
    int32 status = 8;       // 状态 (0:正常，1:倒地，2:庆祝...)
    bool hasBall = 9;
    int32 teamId = 10;
}

// 球的状态
message BallState {
    float posX = 1;
    float posY = 2;
    float posZ = 3;
    float velX = 4;
    float velY = 5;
    float velZ = 6;
    bool inPlay = 7;
}

// ========== 登录相关 ==========

message C2G_LoginRequest {
    string account = 1;
    string password = 2;
}

message G2C_LoginResponse {
    int32 errorCode = 1;
    string token = 2;
    int64 playerId = 3;
}

// ========== 匹配相关 ==========

message C2M_MatchRequest {
    int32 matchType = 1;  // 1:快速，2:排位，3:好友
    int32 elo = 2;
}

message M2C_MatchResult {
    int32 errorCode = 1;
    int64 roomId = 2;
    string serverAddress = 3;
    int32 serverPort = 4;
    string token = 5;
}

// ========== 游戏内消息 ==========

// 加入房间
message C2G_JoinRoomRequest {
    int64 roomId = 1;
    string token = 2;
}

// 房间信息
message RoomInfo {
    int64 roomId = 1;
    repeated PlayerInfo players = 2;
    int32 status = 3;  // 0:等待，1:比赛中，2:结束
}

// 比赛开始
message G2C_MatchStart {
    repeated PlayerState team1Players = 1;
    repeated PlayerState team2Players = 2;
    BallState ballState = 3;
}

// 帧数据同步
message G2C_FrameData {
    int64 frameIndex = 1;
    repeated PlayerInput inputs = 2;
    BallState ballState = 3;
    int32 score1 = 4;
    int32 score2 = 5;
    float time = 6;
}

// 事件通知
message G2C_EventNotify {
    int32 eventType = 1;  // 1:进球，2:犯规，3:换人...
    string eventData = 2;
    repeated int32 involvedPlayers = 3;
}

// 比赛结束
message G2C_MatchEnd {
    int32 score1 = 1;
    int32 score2 = 2;
    repeated PlayerStatistics statistics = 3;
    int32 expReward = 4;
    int32 coinReward = 5;
}

// 玩家统计
message PlayerStatistics {
    int64 playerId = 1;
    int32 goals = 2;
    int32 assists = 3;
    int32 shots = 4;
    int32 shotsOnTarget = 5;
    int32 passes = 6;
    int32 passAccuracy = 7;
    int32 tackles = 8;
    int32 interceptions = 9;
    float rating = 10;
}

// ========== 聊天相关 ==========

message C2G_ChatMessage {
    int32 channelType = 1;  // 1:队伍，2:全部，3:私聊
    string content = 2;
    int64 targetPlayerId = 3;
}

message G2C_ChatMessage {
    int64 senderId = 1;
    string senderName = 2;
    int32 channelType = 3;
    string content = 4;
    int64 timestamp = 5;
}
```

### 3.4 同步策略

#### 3.4.1 帧同步方案
- **确定性锁步**: 所有客户端执行相同逻辑
- **输入预测**: 本地立即执行，服务器验证
- **延迟补偿**: 处理网络延迟
- **状态回滚**: 检测到不一致时回滚

#### 3.4.2 关键代码实现
```csharp
// 帧同步管理器
public class FrameSyncManager : ComponentSystem
{
    public const int TickRate = 60;
    public const int MaxLatencyFrames = 5;
    
    private Queue<PlayerInput> _inputQueue = new();
    private long _currentFrame = 0;
    private Dictionary<long, PlayerInput> _playerInputs = new();
    
    // 收集输入
    public void CollectInput(long playerId, PlayerInput input)
    {
        if (!_playerInputs.ContainsKey(input.FrameIndex))
        {
            _playerInputs[input.FrameIndex] = input;
        }
        
        // 检查是否可以推进帧
        CheckAndAdvanceFrame();
    }
    
    // 推进帧
    private void CheckAndAdvanceFrame()
    {
        while (HasAllInputsForFrame(_currentFrame))
        {
            ExecuteFrame(_currentFrame);
            BroadcastFrameData(_currentFrame);
            _currentFrame++;
        }
    }
    
    // 执行帧逻辑
    private void ExecuteFrame(long frameIndex)
    {
        // 1. 应用所有玩家输入
        foreach (var input in GetInputsForFrame(frameIndex))
        {
            ApplyPlayerInput(input);
        }
        
        // 2. 更新球的物理
        UpdateBallPhysics();
        
        // 3. 检测碰撞
        DetectCollisions();
        
        // 4. 检查事件 (进球、犯规等)
        CheckEvents();
        
        // 5. 生成帧快照
        CreateSnapshot(frameIndex);
    }
}
```

---

## 4. 客户端实现

### 4.1 Unity 项目设置

#### 4.1.1 项目配置
- Unity 版本：2022.3.48 LTS
- 渲染管线：URP (Universal Render Pipeline)
- 物理引擎：Unity PhysX
- 网络库：ET 内置网络 + protobuf-net
- 输入系统：Unity New Input System

#### 4.1.2 资源规范
- 球员模型：LOD 3 级，骨骼数<60
- 球场模型：模块化设计
- 动画：Humanoid Rig，动画融合
- 特效：GPU 粒子系统

### 4.2 核心系统设计

#### 4.2.1 输入系统
```csharp
public class PlayerInputSystem : MonoBehaviour
{
    [Header("移动")]
    public float moveSpeed = 5f;
    public float sprintMultiplier = 1.5f;
    
    [Header("动作")]
    public float passPower = 10f;
    public float shootPower = 20f;
    
    private Vector2 moveInput;
    private bool sprintPressed;
    private float actionPower;
    private float actionDirection;
    
    void Update()
    {
        // 读取输入
        moveInput = new Vector2(
            Input.GetAxisRaw("Horizontal"),
            Input.GetAxisRaw("Vertical")
        );
        
        sprintPressed = Input.GetKey(KeyCode.LeftShift);
        
        // 力度条
        if (Input.GetKeyDown(KeyCode.J))
        {
            StartPowerMeter(ActionType.Pass);
        }
        else if (Input.GetKey(KeyCode.J))
        {
            UpdatePowerMeter();
        }
        else if (Input.GetKeyUp(KeyCode.J))
        {
            CompleteAction(ActionType.Pass);
        }
        
        // 发送输入到服务器
        SendInputToServer();
    }
    
    private void SendInputToServer()
    {
        var input = new PlayerInput
        {
            MoveX = moveInput.x,
            MoveY = moveInput.y,
            Sprint = sprintPressed,
            ActionPower = actionPower,
            ActionDirection = actionDirection,
            FrameIndex = FrameSyncManager.Instance.CurrentFrame
        };
        
        FrameSyncManager.Instance.SendInput(input);
    }
}
```

#### 4.2.2 球员控制器
```csharp
public class PlayerController : MonoBehaviour
{
    [Header("属性")]
    public float speed = 5f;
    public float acceleration = 3f;
    public float stamina = 100f;
    
    [Header("组件")]
    public Animator animator;
    public Rigidbody rb;
    
    private Vector3 velocity;
    private bool hasBall;
    private int teamId;
    private int playerId;
    
    public void ApplyInput(PlayerInput input)
    {
        // 计算目标速度
        Vector3 targetVelocity = new Vector3(input.MoveX, 0, input.MoveY) * speed;
        
        if (input.Sprint && stamina > 10)
        {
            targetVelocity *= 1.5f;
            stamina -= Time.deltaTime * 10;
        }
        else
        {
            stamina = Mathf.Min(stamina + Time.deltaTime * 5, 100);
        }
        
        // 平滑移动
        velocity = Vector3.Lerp(velocity, targetVelocity, acceleration * Time.deltaTime);
        rb.velocity = velocity;
        
        // 更新朝向
        if (velocity.magnitude > 0.1f)
        {
            transform.forward = velocity.normalized;
        }
        
        // 播放动画
        animator.SetFloat("Speed", velocity.magnitude / speed);
        animator.SetBool("Sprinting", input.Sprint);
    }
    
    public void PerformAction(int actionType, float power, float direction)
    {
        switch (actionType)
        {
            case 1: // 传球
                PassBall(power, direction);
                break;
            case 2: // 射门
                ShootBall(power, direction);
                break;
            case 3: // 盘带
                Dribble();
                break;
        }
    }
}
```

#### 4.2.3 球的物理
```csharp
public class BallPhysics : MonoBehaviour
{
    [Header("物理属性")]
    public float mass = 0.43f; // 标准足球重量
    public float drag = 0.5f;
    public float bounceFactor = 0.7f;
    
    [Header("场地边界")]
    public float fieldLength = 105f;
    public float fieldWidth = 68f;
    
    private Rigidbody rb;
    private bool inPlay = true;
    
    void Start()
    {
        rb = GetComponent<Rigidbody>();
        rb.mass = mass;
        rb.drag = drag;
    }
    
    public void Kick(Vector3 direction, float power)
    {
        rb.AddForce(direction * power, ForceMode.Impulse);
    }
    
    void OnCollisionEnter(Collision collision)
    {
        // 检测是否出界
        if (transform.position.x > fieldLength / 2 || 
            transform.position.x < -fieldLength / 2)
        {
            // 球门线外
            if (Mathf.Abs(transform.position.z) < 10f)
            {
                // 检查是否进球
                CheckGoal();
            }
            else
            {
                // 球门球
                ResetBall(BallResetType.GoalKick);
            }
        }
        
        if (transform.position.z > fieldWidth / 2 || 
            transform.position.z < -fieldWidth / 2)
        {
            // 边线球
            ResetBall(BallResetType.ThrowIn);
        }
    }
    
    private void CheckGoal()
    {
        // 判断进球队伍
        if (transform.position.x > 0)
        {
            // 队伍 2 得分
            GameManager.Instance.GoalScored(2);
        }
        else
        {
            // 队伍 1 得分
            GameManager.Instance.GoalScored(1);
        }
    }
}
```

#### 4.2.4 摄像机控制
```csharp
public class GameCamera : MonoBehaviour
{
    [Header("视角设置")]
    public Transform target;
    public float distance = 20f;
    public float height = 10f;
    public float rotationSpeed = 5f;
    
    [Header("动态调整")]
    public float followSpeed = 5f;
    public float lookAheadDistance = 10f;
    
    private float currentAngle = 0f;
    private Vector3 targetPosition;
    
    void LateUpdate()
    {
        if (target == null) return;
        
        // 计算理想位置
        float idealAngle = currentAngle;
        Quaternion rotation = Quaternion.Euler(30f, idealAngle, 0f);
        Vector3 offset = rotation * new Vector3(0, 0, -distance) + Vector3.up * height;
        
        targetPosition = target.position + offset;
        
        // 平滑跟随
        transform.position = Vector3.Lerp(transform.position, targetPosition, followSpeed * Time.deltaTime);
        
        // 始终看向球
        transform.LookAt(target.position);
    }
    
    public void RotateCamera(float angleDelta)
    {
        currentAngle += angleDelta * rotationSpeed;
    }
}
```

### 4.3 UI 系统

#### 4.3.1 HUD 布局
```
┌─────────────────────────────────────────────────────┐
│ [队伍 1 队徽]  3 - 2  [队伍 2 队徽]      ⏱️ 03:45       │
│  体力条 ████████░░                                │
├─────────────────────────────────────────────────────┤
│                                                     │
│                    [比赛区域]                        │
│                                                     │
│                                                     │
├─────────────────────────────────────────────────────┤
│ [小地图]                                          │
│  ● ○ ●                                              │
│    ●                                                │
│  ○   ○                                              │
└─────────────────────────────────────────────────────┘
```

#### 4.3.2 力度条实现
```csharp
public class PowerMeter : MonoBehaviour
{
    public Image fillImage;
    public Gradient colorGradient;
    
    private float currentValue = 0f;
    private float increaseSpeed = 2f;
    private bool isCharging = false;
    private ActionType currentAction;
    
    public void StartCharging(ActionType action)
    {
        currentAction = action;
        currentValue = 0f;
        isCharging = true;
    }
    
    public void UpdateCharging()
    {
        if (!isCharging) return;
        
        currentValue += increaseSpeed * Time.deltaTime;
        if (currentValue >= 1f)
        {
            currentValue = 1f;
            isCharging = false;
        }
        
        fillImage.fillAmount = currentValue;
        fillImage.color = colorGradient.Evaluate(currentValue);
    }
    
    public float Release()
    {
        isCharging = false;
        return currentValue;
    }
}
```

---

## 5. 美术资源需求

### 5.1 角色模型
- **球员**: 10 套不同风格的球衣，每套包含主客场
- **守门员**: 5 套专属守门员服装
- **面部**: 多种脸型、发型选项
- **动作**: 跑动、传球、射门、扑救、庆祝等 50+ 动画

### 5.2 场景资源
- **球场**: 3 种不同风格的球场 (现代、复古、街头)
- **观众**: 低多边形观众群
- **环境**: 白天、黄昏、夜晚光照预设
- **天气**: 晴天、雨天、雪天粒子效果

### 5.3 UI 资源
- **图标**: 技能图标、道具图标、成就图标
- **按钮**: 各种交互按钮状态
- **背景**: 菜单背景、加载界面
- **字体**: 支持多语言的清晰字体

### 5.4 音效资源
- **背景音乐**: 菜单、比赛、胜利、失败
- **音效**: 踢球声、欢呼声、哨声、解说片段
- **语音**: 球员呼喊、教练指令

---

## 6. 开发计划

### 阶段一：基础框架搭建 (2 周)
**Week 1:**
- [ ] 搭建 ET 服务器环境
- [ ] 创建 Unity 客户端项目
- [ ] 实现基础网络通信
- [ ] 完成登录注册功能

**Week 2:**
- [ ] 实现匹配系统
- [ ] 创建房间管理
- [ ] 基础帧同步框架
- [ ] 数据库集成

### 阶段二：核心玩法实现 (4 周)
**Week 3-4:**
- [ ] 球员移动和控球
- [ ] 球的物理系统
- [ ] 传球和射门机制
- [ ] 基础碰撞检测

**Week 5-6:**
- [ ] 完整操作映射
- [ ] 守门员 AI
- [ ] 队友 AI 行为
- [ ] 裁判系统

### 阶段三：游戏完善 (3 周)
**Week 7:**
- [ ] 完整 UI 系统
- [ ] 球员属性和成长
- [ ] 球队管理功能

**Week 8:**
- [ ] 多种游戏模式
- [ ] 排位赛系统
- [ ] 好友系统

**Week 9:**
- [ ] 音效和音乐
- [ ] 特效优化
- [ ] 性能优化

### 阶段四：测试与上线 (2 周)
**Week 10:**
- [ ] 内部测试
- [ ] Bug 修复
- [ ] 平衡性调整

**Week 11:**
- [ ] 公开测试
- [ ] 服务器压力测试
- [ ] 正式上线准备

---

## 7. 部署指南

### 7.1 服务器部署

#### 7.1.1 环境要求
- **操作系统**: Ubuntu 20.04 LTS 或更高
- **CPU**: 4 核以上
- **内存**: 8GB 以上
- **带宽**: 100Mbps 以上
- **.NET 版本**: .NET 6.0

#### 7.1.2 安装步骤
```bash
# 1. 安装依赖
sudo apt update
sudo apt install -y dotnet-sdk-6.0 mongodb nginx

# 2. 克隆项目
git clone https://github.com/your-repo/OpenSoccerOnline.git
cd OpenSoccerOnline/Server

# 3. 编译服务器
dotnet build -c Release

# 4. 配置文件
cp appsettings.json.example appsettings.json
# 编辑 appsettings.json 填入数据库连接等信息

# 5. 启动服务
# 启动各个服务器进程
dotnet run --project Gate
dotnet run --project Login
dotnet run --project Match
dotnet run --project Game
dotnet run --project DB

# 或使用 systemd 管理
sudo systemctl enable opensoccer-gate
sudo systemctl start opensoccer-gate
# ... 其他服务同理
```

#### 7.1.3 Nginx 配置
```nginx
server {
    listen 80;
    server_name soccer.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:10001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 7.2 客户端打包

#### 7.2.1 Windows
```bash
# 在 Unity 中
File -> Build Settings
Platform: Windows
Architecture: x86_64
Build
```

#### 7.2.2 Android
```bash
# 在 Unity 中
File -> Build Settings
Platform: Android
SDK/NDK 配置
Build
```

#### 7.2.3 iOS
```bash
# 在 Unity 中
File -> Build Settings
Platform: iOS
Build
# 在 Xcode 中签名打包
```

---

## 8. 测试计划

### 8.1 单元测试
- 球员移动逻辑测试
- 球的物理计算测试
- 碰撞检测测试
- 网络消息序列化测试

### 8.2 集成测试
- 登录流程测试
- 匹配流程测试
- 比赛全流程测试
- 断线重连测试

### 8.3 压力测试
- 单服务器承载测试 (目标：1000 并发)
- 多服务器集群测试
- 网络延迟模拟测试
- 内存泄漏检测

### 8.4 兼容性测试
- 不同分辨率测试
- 不同硬件配置测试
- 不同网络环境测试
- 跨平台测试

---

## 9. 运维监控

### 9.1 日志系统
```csharp
// 日志级别
- Debug: 详细调试信息
- Info: 一般信息
- Warning: 警告信息
- Error: 错误信息
- Critical: 严重错误

// 日志输出
- 控制台输出
- 文件日志 (按天分割)
- 远程日志服务器
```

### 9.2 监控指标
- **服务器性能**: CPU、内存、磁盘 IO
- **网络指标**: 延迟、带宽、连接数
- **业务指标**: 在线人数、匹配时间、比赛场次
- **错误率**: 异常次数、断开连接率

### 9.3 告警规则
- CPU 使用率 > 80% 持续 5 分钟
- 内存使用率 > 90%
- 错误率 > 1%
- 匹配时间 > 5 分钟

---

## 10. 扩展计划

### 10.1 短期扩展 (3 个月内)
- 更多球场和球衣
- 联赛系统
- 俱乐部系统
- 观战模式

### 10.2 中期扩展 (6 个月内)
- 移动端适配
- 电竞模式
- 直播集成
- VR 支持实验

### 10.3 长期扩展 (1 年内)
- AI 训练系统
- 自定义比赛规则
- 模组支持
- 全球化运营

---

## 附录

### A. 参考资料
- [ET 框架官方文档](https://github.com/egametang/ET)
- [Unity 官方文档](https://docs.unity3d.com/)
- [Protobuf 文档](https://developers.google.com/protocol-buffers)
- [Pro Soccer Online 游戏视频](https://store.steampowered.com/app/1289310/Pro_Soccer_Online/)

### B. 术语表
- **ELO**: 国际象棋等级分系统，用于匹配
- **帧同步**: 所有客户端同步执行相同逻辑
- **状态同步**: 服务器同步游戏状态到客户端
- **延迟补偿**: 处理网络延迟的技术

### C. 联系方式
- 项目负责人：[待填写]
- 技术支持：[待填写]
- 问题反馈：[待填写]

---

**文档版本**: v1.0  
**创建日期**: 2024 年  
**最后更新**: 2024 年  
**状态**: 初稿
