#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pro Soccer Online - 自动化部署脚本
功能：
1. 克隆 ET 框架
2. 创建 Unity 项目结构
3. 生成 Protobuf 协议代码
4. 植入核心游戏代码
5. 启动服务器和客户端
"""

import os
import sys
import subprocess
import shutil
import platform
import time
from pathlib import Path

# ================= 配置区域 =================
PROJECT_NAME = "ProSoccerOnline"
ET_REPO_URL = "https://github.com/egametang/ET.git"
ET_BRANCH = "master"  # 或者指定特定版本 tag
UNITY_VERSION = "2022.3.48f1"
SERVER_PORT = 10001
MONGO_PORT = 27017

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

def log_success(msg):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.END} {msg}")

def log_warning(msg):
    print(f"{Colors.YELLOW}[WARNING]{Colors.END} {msg}")

def log_error(msg):
    print(f"{Colors.RED}[ERROR]{Colors.END} {msg}")

# ================= 工具函数 =================
def run_command(cmd, cwd=None, check=True):
    """执行命令行命令"""
    log_info(f"执行: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=isinstance(cmd, str),
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        log_error(f"命令执行失败: {e}")
        if e.stderr:
            print(e.stderr)
        if check:
            raise
        return None

def check_dependency(name, cmd):
    """检查依赖是否安装"""
    log_info(f"检查依赖: {name}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            log_success(f"{name} 已安装")
            return True
        else:
            log_warning(f"{name} 未安装或版本过低")
            return False
    except Exception:
        log_warning(f"{name} 未安装")
        return False

def download_file(url, dest):
    """下载文件（简化版，实际可用 requests）"""
    log_info(f"下载: {url} -> {dest}")
    # 这里用 curl 或 wget，实际生产环境建议用 requests 库
    if platform.system() == "Windows":
        run_command(f"curl -L -o {dest} {url}")
    else:
        run_command(f"wget -O {dest} {url}")

# ================= 核心部署步骤 =================
def step_check_environment():
    """步骤 1: 检查环境依赖"""
    log_info("========== 步骤 1: 检查环境依赖 ==========")
    
    deps = [
        ("Git", "git --version"),
        ("Python 3", "python3 --version" if platform.system() != "Windows" else "python --version"),
        (".NET 6.0", "dotnet --version"),
        ("Protoc", "protoc --version"),
    ]
    
    missing = []
    for name, cmd in deps:
        if not check_dependency(name, cmd):
            missing.append(name)
    
    if missing:
        log_error(f"缺少依赖: {', '.join(missing)}")
        log_info("请先安装上述依赖后重新运行脚本")
        return False
    
    # 检查 MongoDB (可选，服务器需要)
    if not check_dependency("MongoDB", "mongod --version"):
        log_warning("MongoDB 未安装，服务器可能无法启动")
    
    log_success("环境检查通过")
    return True

def step_clone_et_framework():
    """步骤 2: 克隆 ET 框架"""
    log_info("========== 步骤 2: 克隆 ET 框架 ==========")
    
    et_dir = Path("ET")
    if et_dir.exists():
        log_warning("ET 目录已存在，跳过克隆")
        log_info("如需重新克隆，请手动删除 ET 目录")
        return True
    
    log_info("正在克隆 ET 框架...")
    run_command(["git", "clone", "--depth", "1", "-b", ET_BRANCH, ET_REPO_URL, str(et_dir)])
    
    if not et_dir.exists():
        log_error("ET 框架克隆失败")
        return False
    
    log_success("ET 框架克隆完成")
    return True

def step_create_unity_project():
    """步骤 3: 创建 Unity 项目结构"""
    log_info("========== 步骤 3: 创建 Unity 项目结构 ==========")
    
    unity_dir = Path("UnityClient")
    if unity_dir.exists():
        log_warning("UnityClient 目录已存在，跳过创建")
        return True
    
    log_info("创建 Unity 项目目录结构...")
    
    # 创建基础目录
    dirs = [
        unity_dir / "Assets" / "Scripts" / "Game" / "FrameSync",
        unity_dir / "Assets" / "Scripts" / "Game" / "Player",
        unity_dir / "Assets" / "Scripts" / "Game" / "Ball",
        unity_dir / "Assets" / "Scripts" / "Game" / "Network",
        unity_dir / "Assets" / "Scripts" / "UI",
        unity_dir / "Assets" / "Scripts" / "Core",
        unity_dir / "Assets" / "Scripts" / "Protobuf",
        unity_dir / "Assets" / "Resources",
        unity_dir / "Assets" / "Scenes",
        unity_dir / "ProjectSettings",
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    
    # 创建 ProjectSettings 文件 (最小化配置)
    settings_file = unity_dir / "ProjectSettings" / "ProjectVersion.txt"
    with open(settings_file, 'w') as f:
        f.write(f"m_EditorVersion: {UNITY_VERSION}\n")
        f.write("m_EditorVersionWithRevision: 2022.3.48f1 (unknown)\n")
    
    log_success("Unity 项目结构创建完成")
    return True

def step_generate_protobuf():
    """步骤 4: 生成 Protobuf 协议代码"""
    log_info("========== 步骤 4: 生成 Protobuf 协议代码 ==========")
    
    proto_dir = Path("Proto")
    proto_dir.mkdir(exist_ok=True)
    
    # 写入 Protocol.proto
    proto_content = '''syntax = "proto3";
package Proto;

// 登录相关
message C2G_LoginGate {
    string Account = 1;
    string Password = 2;
}

message G2C_LoginGate {
    int32 ErrorCode = 1;
    string Message = 2;
    int64 ActorId = 3;
    bytes Key = 4;
    bytes GateSessionKey = 5;
}

// 匹配相关
message C2M_CreateMatch {
    int32 Mode = 1; // 0:快速匹配，1:好友对战，2:排位赛
}

message M2C_CreateMatch {
    int32 ErrorCode = 1;
    int64 RoomId = 2;
}

message C2M_JoinMatch {
    int64 RoomId = 1;
}

message M2C_JoinMatch {
    int32 ErrorCode = 1;
}

// 帧同步相关
message C2G_FrameInput {
    int64 ActorId = 1;
    int32 Frame = 2;
    bytes InputData = 3; // [移动方向 (4bit) + 技能 (3bit) + 保留 (1bit)]
}

message G2C_FrameNotify {
    int32 Frame = 1;
    int64 Timestamp = 2;
    repeated FramePlayerData Players = 3;
    FrameBallData Ball = 4;
}

message FramePlayerData {
    int64 ActorId = 1;
    Vector3 Position = 2;
    float Rotation = 3;
    int32 State = 4; // 0:正常，1:持球，2:倒地
    bytes Input = 5;
}

message FrameBallData {
    Vector3 Position = 1;
    Vector3 Velocity = 2;
    int64 OwnerId = 3;
}

message Vector3 {
    float X = 1;
    float Y = 2;
    float Z = 3;
}

// 游戏事件
message G2C_GameStart {
    int64 RoomId = 1;
    repeated int64 PlayerIds = 2;
    int32 BlueTeamScore = 3;
    int32 RedTeamScore = 4;
}

message G2C_GameOver {
    int32 WinnerTeam = 1; // 0:平局，1:蓝队，2:红队
    int32 BlueScore = 2;
    int32 RedScore = 3;
}
'''
    
    proto_file = proto_dir / "Protocol.proto"
    with open(proto_file, 'w') as f:
        f.write(proto_content)
    
    log_info("Protocol.proto 已创建")
    
    # 编译 Proto 到 C#
    cs_out_client = Path("UnityClient/Assets/Scripts/Protobuf")
    cs_out_server = Path("ET/Model/Proto")
    
    cs_out_client.mkdir(parents=True, exist_ok=True)
    cs_out_server.mkdir(parents=True, exist_ok=True)
    
    log_info("编译 Protobuf 到 C#...")
    
    # 为客户端生成
    run_command([
        "protoc",
        f"--csharp_out={cs_out_client}",
        f"-I={proto_dir}",
        str(proto_file)
    ])
    
    # 为服务端生成
    run_command([
        "protoc",
        f"--csharp_out={cs_out_server}",
        f"-I={proto_dir}",
        str(proto_file)
    ])
    
    # 检查生成结果
    generated_files = list(cs_out_client.glob("*.cs"))
    if len(generated_files) > 0:
        log_success(f"Protobuf 代码生成成功，生成 {len(generated_files)} 个文件")
        return True
    else:
        log_error("Protobuf 代码生成失败")
        return False

def step_inject_game_code():
    """步骤 5: 植入游戏核心代码"""
    log_info("========== 步骤 5: 植入游戏核心代码 ==========")
    
    # 定义要创建的文件和内容
    files_to_create = [
        # 客户端文件
        {
            "path": "UnityClient/Assets/Scripts/Game/FrameSync/FrameSyncManager.cs",
            "content": get_frame_sync_manager_code()
        },
        {
            "path": "UnityClient/Assets/Scripts/Game/Player/PlayerController.cs",
            "content": get_player_controller_code()
        },
        {
            "path": "UnityClient/Assets/Scripts/Game/Ball/BallPhysics.cs",
            "content": get_ball_physics_code()
        },
        {
            "path": "UnityClient/Assets/Scripts/Game/Network/ETNetworkManager.cs",
            "content": get_network_manager_code()
        },
        {
            "path": "UnityClient/Assets/Scripts/Core/GameManager.cs",
            "content": get_game_manager_code()
        },
        # 服务端文件
        {
            "path": "ET/Hotfix/Module/FrameSyncSystem.cs",
            "content": get_frame_sync_system_code()
        },
        {
            "path": "ET/Model/Module/FrameSyncComponent.cs",
            "content": get_frame_sync_component_code()
        },
    ]
    
    success_count = 0
    for file_info in files_to_create:
        path = Path(file_info["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(file_info["content"])
            log_success(f"创建: {file_info['path']}")
            success_count += 1
        except Exception as e:
            log_error(f"创建文件失败 {file_info['path']}: {e}")
    
    log_info(f"共创建 {success_count}/{len(files_to_create)} 个文件")
    return success_count == len(files_to_create)

def step_build_server():
    """步骤 6: 编译服务器"""
    log_info("========== 步骤 6: 编译服务器 ==========")
    
    server_dir = Path("ET")
    
    log_info("恢复 .NET 依赖...")
    run_command(["dotnet", "restore"], cwd=server_dir)
    
    log_info("编译服务器...")
    run_command(["dotnet", "build", "-c", "Release"], cwd=server_dir)
    
    # 检查编译结果
    dll_path = server_dir / "bin" / "Release" / "net6.0" / "ET.Gate.dll"
    if dll_path.exists():
        log_success("服务器编译成功")
        return True
    else:
        log_warning("服务器编译完成但未找到预期 DLL，可能是配置问题")
        return True  # 继续执行

def step_create_startup_scripts():
    """步骤 7: 创建启动脚本"""
    log_info("========== 步骤 7: 创建启动脚本 ==========")
    
    # Windows 启动脚本
    win_script = Path("start_server.bat")
    win_content = '''@echo off
title Pro Soccer Online - Server
echo ==========================================
echo Starting Pro Soccer Online Server
echo ==========================================

REM 启动 MongoDB (如果未作为服务运行)
REM start "" mongod --dbpath "data/db"

echo Starting ET Servers...
start "ET_Gate" dotnet run --project ET/Model/ET.Gate.csproj
start "ET_Login" dotnet run --project ET/Model/ET.Login.csproj
start "ET_Match" dotnet run --project ET/Model/ET.Match.csproj
start "ET_DB" dotnet run --project ET/Model/ET.DB.csproj

echo.
echo Servers are starting...
echo Please wait 5 seconds before starting Unity Client
echo.
pause
'''
    
    with open(win_script, 'w') as f:
        f.write(win_content)
    
    # Linux/Mac 启动脚本
    unix_script = Path("start_server.sh")
    unix_content = '''#!/bin/bash
echo "=========================================="
echo "Starting Pro Soccer Online Server"
echo "=========================================="

# 启动 MongoDB
# mongod --dbpath "data/db" &

echo "Starting ET Servers..."
dotnet run --project ET/Model/ET.Gate.csproj &
dotnet run --project ET/Model/ET.Login.csproj &
dotnet run --project ET/Model/ET.Match.csproj &
dotnet run --project ET/Model/ET.DB.csproj &

echo ""
echo "Servers are starting..."
echo "Please wait 5 seconds before starting Unity Client"
echo ""
wait
'''
    
    with open(unix_script, 'w') as f:
        f.write(unix_content)
    
    os.chmod(unix_script, 0o755)
    
    # Unity 启动脚本
    unity_launcher = Path("start_unity.bat" if platform.system() == "Windows" else "start_unity.sh")
    if platform.system() == "Windows":
        with open(unity_launcher, 'w') as f:
            f.write('@echo off\nstart "" "UnityClient"\necho Open Unity Hub and load the UnityClient project\npause\n')
    else:
        with open(unity_launcher, 'w') as f:
            f.write('#!/bin/bash\nopen -a "Unity Hub" UnityClient\n')
        os.chmod(unity_launcher, 0o755)
    
    log_success("启动脚本创建完成")
    log_info("Windows: 运行 start_server.bat 启动服务器")
    log_info("Linux/Mac: 运行 ./start_server.sh 启动服务器")
    return True

def step_show_instructions():
    """步骤 8: 显示使用说明"""
    log_info("========== 部署完成！==========")
    print("""
╔══════════════════════════════════════════════════════════╗
║           Pro Soccer Online 部署成功！                    ║
╠══════════════════════════════════════════════════════════╣
║ 下一步操作：                                              ║
║                                                          ║
║ 1. 启动 MongoDB:                                          ║
║    - Windows: net start MongoDB                          ║
║    - Mac: brew services start mongodb-community          ║
║    - Linux: sudo systemctl start mongod                  ║
║                                                          ║
║ 2. 启动服务器:                                            ║
║    - Windows: 双击 start_server.bat                      ║
║    - Mac/Linux: ./start_server.sh                        ║
║                                                          ║
║ 3. 打开 Unity:                                            ║
║    - 打开 Unity Hub                                      ║
║    - 添加项目：选择 UnityClient 目录                     ║
║    - 使用 Unity 2022.3.48f1 打开                         ║
║    - 点击 Play 按钮                                      ║
║                                                          ║
║ 4. 测试:                                                  ║
║    - 打开多个 Unity 实例进行测试                         ║
║    - 检查控制台日志确认连接成功                          ║
║                                                          ║
╠══════════════════════════════════════════════════════════╣
║ 常见问题：                                                ║
║ - 如果 protoc 报错，请确保已安装 protobuf 编译器          ║
║ - 如果 dotnet 报错，请确保已安装 .NET 6.0 SDK             ║
║ - 如果 Unity 报错，请检查版本是否为 2022.3.48f1           ║
╚══════════════════════════════════════════════════════════╝
    """)

# ================= 代码模板生成器 =================
def get_frame_sync_manager_code():
    return '''using System.Collections.Generic;
using UnityEngine;

namespace ProSoccer.FrameSync
{
    public class FrameSyncManager : MonoBehaviour
    {
        private static FrameSyncManager _instance;
        public static FrameSyncManager Instance => _instance;

        private Dictionary<int, FrameData> _frameBuffer = new Dictionary<int, FrameData>();
        private int _currentFrame = 0;
        private const int FRAME_RATE = 20;
        private const int BUFFER_SIZE = 3;

        [System.Serializable]
        public class FrameData
        {
            public int FrameNumber;
            public long Timestamp;
            public Dictionary<long, PlayerFrameState> PlayerStates = new Dictionary<long, PlayerFrameState>();
            public BallFrameState BallState;
        }

        [System.Serializable]
        public class PlayerFrameState
        {
            public long ActorId;
            public Vector3 Position;
            public float Rotation;
            public int State;
            public byte[] Input;
        }

        [System.Serializable]
        public class BallFrameState
        {
            public Vector3 Position;
            public Vector3 Velocity;
            public long OwnerId;
        }

        void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
            }
        }

        void Start()
        {
            InvokeRepeating(nameof(ProcessFrame), 0, 1f / FRAME_RATE);
        }

        void ProcessFrame()
        {
            if (_frameBuffer.ContainsKey(_currentFrame))
            {
                ApplyFrame(_frameBuffer[_currentFrame]);
                _frameBuffer.Remove(_currentFrame);
                _currentFrame++;
            }
        }

        public void AddFrameData(FrameData data)
        {
            if (!_frameBuffer.ContainsKey(data.FrameNumber))
            {
                _frameBuffer[data.FrameNumber] = data;
            }
        }

        void ApplyFrame(FrameData data)
        {
            // 应用玩家状态
            foreach (var kvp in data.PlayerStates)
            {
                var player = GameManager.Instance.GetPlayer(kvp.Key);
                if (player != null)
                {
                    player.ApplyState(kvp.Value);
                }
            }

            // 应用球状态
            if (data.BallState != null && BallPhysics.Instance != null)
            {
                BallPhysics.Instance.ApplyState(data.BallState);
            }
        }

        public int GetCurrentFrame() => _currentFrame;
    }
}
'''

def get_player_controller_code():
    return '''using UnityEngine;

namespace ProSoccer.Player
{
    public class PlayerController : MonoBehaviour
    {
        public long ActorId { get; set; }
        public bool IsLocalPlayer { get; set; }

        [Header("Movement")]
        public float MoveSpeed = 8f;
        public float RotationSpeed = 180f;

        private Rigidbody _rb;
        private Vector3 _targetVelocity;
        private float _targetRotation;
        private byte _inputState;

        void Start()
        {
            _rb = GetComponent<Rigidbody>();
            if (_rb == null)
            {
                _rb = gameObject.AddComponent<Rigidbody>();
                _rb.useGravity = true;
                _rb.constraints = RigidbodyConstraints.FreezeRotationX | RigidbodyConstraints.FreezeRotationZ;
            }
        }

        void Update()
        {
            if (IsLocalPlayer)
            {
                HandleInput();
            }
        }

        void FixedUpdate()
        {
            Move();
        }

        void HandleInput()
        {
            float h = Input.GetAxisRaw("Horizontal");
            float v = Input.GetAxisRaw("Vertical");
            
            bool skillJ = Input.GetButton("Fire1"); // J
            bool skillK = Input.GetButton("Fire2"); // K
            bool skillL = Input.GetButton("Fire3"); // L

            _inputState = 0;
            if (h > 0) _inputState |= 1;
            if (h < 0) _inputState |= 2;
            if (v > 0) _inputState |= 4;
            if (v < 0) _inputState |= 8;
            if (skillJ) _inputState |= 16;
            if (skillK) _inputState |= 32;
            if (skillL) _inputState |= 64;

            Vector3 dir = new Vector3(h, 0, v).normalized;
            _targetVelocity = dir * MoveSpeed;
            
            if (dir != Vector3.zero)
            {
                _targetRotation = Mathf.Atan2(dir.x, dir.z) * Mathf.Rad2Deg;
            }

            // 发送输入到服务器
            if (GameManager.Instance.NetworkManager != null)
            {
                GameManager.Instance.NetworkManager.SendFrameInput(_inputState);
            }
        }

        void Move()
        {
            if (_rb != null)
            {
                _rb.velocity = _targetVelocity;
                float currentRot = transform.eulerAngles.y;
                float targetRot = Mathf.MoveTowardsAngle(currentRot, _targetRotation, RotationSpeed * Time.fixedDeltaTime);
                transform.eulerAngles = new Vector3(0, targetRot, 0);
            }
        }

        public void ApplyState(FrameSyncManager.PlayerFrameState state)
        {
            transform.position = state.Position;
            transform.eulerAngles = new Vector3(0, state.Rotation, 0);
            _inputState = state.Input != null && state.Input.Length > 0 ? state.Input[0] : (byte)0;
        }
    }
}
'''

def get_ball_physics_code():
    return '''using UnityEngine;

namespace ProSoccer.Ball
{
    public class BallPhysics : MonoBehaviour
    {
        private static BallPhysics _instance;
        public static BallPhysics Instance => _instance;

        [Header("Physics")]
        public float Friction = 0.98f;
        public float MaxSpeed = 20f;

        private Rigidbody _rb;
        private long _ownerId;

        void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
            }
            else
            {
                Destroy(gameObject);
                return;
            }

            _rb = GetComponent<Rigidbody>();
            if (_rb == null)
            {
                _rb = gameObject.AddComponent<Rigidbody>();
                _rb.useGravity = true;
                _rb.drag = 0.1f;
            }
        }

        void FixedUpdate()
        {
            if (_rb.velocity.magnitude > MaxSpeed)
            {
                _rb.velocity = _rb.velocity.normalized * MaxSpeed;
            }

            // 摩擦力
            _rb.velocity = new Vector3(
                _rb.velocity.x * Friction,
                _rb.velocity.y,
                _rb.velocity.z * Friction
            );
        }

        public void ApplyState(FrameSyncManager.BallFrameState state)
        {
            transform.position = state.Position;
            _rb.velocity = state.Velocity;
            _ownerId = state.OwnerId;
        }

        public long GetOwnerId() => _ownerId;
    }
}
'''

def get_network_manager_code():
    return '''using UnityEngine;
using ET;

namespace ProSoccer.Network
{
    public class ETNetworkManager : MonoBehaviour
    {
        private Session _session;
        private string _serverIP = "127.0.0.1";
        private int _serverPort = 10001;

        public bool IsConnected { get; private set; }

        void Awake()
        {
            Game.Initialize();
        }

        public async void Connect()
        {
            try
            {
                _session = await Game.Scene.GetComponent<NetComponent>().CreateSession(_serverIP, _serverPort);
                IsConnected = true;
                Debug.Log("连接到服务器成功!");

                _session.AddCallback<Proto.G2C_FrameNotify>(OnFrameNotify);
                
                await Login();
            }
            catch (System.Exception e)
            {
                Debug.LogError($"连接失败：{e.Message}");
                IsConnected = false;
            }
        }

        async System.Threading.Tasks.Task Login()
        {
            var request = new Proto.C2G_LoginGate { Account = "Player1" };
            var response = await _session.Call<Proto.G2C_LoginGate>(request);
            
            if (response.ErrorCode == 0)
            {
                Debug.Log($"登录成功，ActorId: {response.ActorId}");
                GameManager.Instance.ActorId = response.ActorId;
            }
        }

        public void SendFrameInput(byte inputData)
        {
            if (_session == null || !_session.IsDisposed)
            {
                var msg = new Proto.C2G_FrameInput
                {
                    ActorId = GameManager.Instance.ActorId,
                    Frame = FrameSyncManager.Instance.GetCurrentFrame(),
                    InputData = new byte[] { inputData }
                };
                _session.Send(msg);
            }
        }

        void OnFrameNotify(Proto.G2C_FrameNotify notify)
        {
            var frameData = ConvertToFrameData(notify);
            FrameSyncManager.Instance.AddFrameData(frameData);
        }

        FrameSyncManager.FrameData ConvertToFrameData(Proto.G2C_FrameNotify notify)
        {
            var data = new FrameSyncManager.FrameData
            {
                FrameNumber = notify.Frame,
                Timestamp = notify.Timestamp
            };

            foreach (var p in notify.Players)
            {
                var state = new FrameSyncManager.PlayerFrameState
                {
                    ActorId = p.ActorId,
                    Position = new Vector3(p.Position.X, p.Position.Y, p.Position.Z),
                    Rotation = p.Rotation,
                    State = p.State,
                    Input = p.Input.ToByteArray()
                };
                data.PlayerStates[state.ActorId] = state;
            }

            if (notify.Ball != null)
            {
                data.BallState = new FrameSyncManager.BallFrameState
                {
                    Position = new Vector3(notify.Ball.Position.X, notify.Ball.Position.Y, notify.Ball.Position.Z),
                    Velocity = new Vector3(notify.Ball.Velocity.X, notify.Ball.Velocity.Y, notify.Ball.Velocity.Z),
                    OwnerId = notify.Ball.OwnerId
                };
            }

            return data;
        }

        void Update()
        {
            Game.Update();
        }

        void LateUpdate()
        {
            Game.LateUpdate();
        }

        void FixedUpdate()
        {
            Game.FixedUpdate();
        }
    }
}
'''

def get_game_manager_code():
    return '''using UnityEngine;

namespace ProSoccer.Core
{
    public class GameManager : MonoBehaviour
    {
        private static GameManager _instance;
        public static GameManager Instance => _instance;

        public long ActorId { get; set; }
        public Network.ETNetworkManager NetworkManager { get; private set; }

        void Awake()
        {
            if (_instance == null)
            {
                _instance = this;
                DontDestroyOnLoad(gameObject);
            }
            else
            {
                Destroy(gameObject);
            }
        }

        void Start()
        {
            NetworkManager = FindObjectOfType<Network.ETNetworkManager>();
            if (NetworkManager != null)
            {
                NetworkManager.Connect();
            }
        }

        public Player.PlayerController GetPlayer(long actorId)
        {
            var players = FindObjectsOfType<Player.PlayerController>();
            foreach (var player in players)
            {
                if (player.ActorId == actorId)
                    return player;
            }
            return null;
        }
    }
}
'''

def get_frame_sync_component_code():
    return '''using ET;

namespace Model
{
    [ComponentOf(typeof(Scene))]
    public class FrameSyncComponent : Entity, IAwake, IUpdate
    {
        public int FrameNumber { get; set; }
        public long LastFrameTime { get; set; }
        
        public override void Dispose()
        {
            if (this.IsDisposed) return;
            base.Dispose();
        }
    }
}
'''

def get_frame_sync_system_code():
    return '''using System.Collections.Generic;
using ET;

namespace ET
{
    [FriendOf(typeof(FrameSyncComponent))]
    public static class FrameSyncSystem
    {
        private const int FRAME_RATE = 20;
        private const int FRAME_INTERVAL_MS = 1000 / FRAME_RATE;

        [ObjectSystem]
        public class FrameSyncComponentAwakeSystem : AwakeSystem<FrameSyncComponent>
        {
            public override void Awake(FrameSyncComponent self)
            {
                self.FrameNumber = 0;
                self.LastFrameTime = TimeHelper.ClientNow();
            }
        }

        [ObjectSystem]
        public class FrameSyncComponentUpdateSystem : UpdateSystem<FrameSyncComponent>, IUpdate
        {
            public void Update(FrameSyncComponent self)
            {
                long now = TimeHelper.ClientNow();
                if (now - self.LastFrameTime >= FRAME_INTERVAL_MS)
                {
                    self.LastFrameTime += FRAME_INTERVAL_MS;
                    Tick(self);
                }
            }

            void Tick(FrameSyncComponent self)
            {
                int frame = ++self.FrameNumber;
                
                // 简化的帧同步逻辑
                // 实际项目中需要从 UnitComponent 获取所有单位状态
                // 并广播给所有客户端
                
                Log.Debug($"Frame {frame} processed");
            }
        }
    }
}
'''

# ================= 主程序 =================
def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║     Pro Soccer Online - 自动化部署工具                    ║
║     基于 Unity 2022.3.48 + ET 框架                        ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    steps = [
        ("环境检查", step_check_environment),
        ("克隆 ET 框架", step_clone_et_framework),
        ("创建 Unity 项目", step_create_unity_project),
        ("生成 Protobuf 代码", step_generate_protobuf),
        ("植入游戏代码", step_inject_game_code),
        ("编译服务器", step_build_server),
        ("创建启动脚本", step_create_startup_scripts),
        ("显示说明", step_show_instructions),
    ]
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                log_error(f"{step_name} 失败，终止部署")
                return False
        except Exception as e:
            log_error(f"{step_name} 发生异常：{e}")
            return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
