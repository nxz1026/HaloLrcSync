# HALO OIXELBAR 歌词同步软件

🎵 自动获取网易云音乐歌词，同步显示到 HALO OIXELBAR 音箱上！

> 💡 **新方案**：使用内存读取技术，无需API，直接从网易云音乐进程中获取歌词

## ✨ 功能特点

- 🎵 **内存读取** - 直接从网易云音乐进程中读取歌词，无需API
- 📜 **LRC歌词解析** - 支持标准LRC格式歌词
- 🔌 **USB通信** - 与HALO OIXELBAR音箱通过USB连接通信
- ⚡ **实时同步** - 50ms级歌词同步显示
- 🪟 **Windows优化** - 专为Windows系统设计
- ⚙️ **多版本支持** - 支持网易云音乐多个版本
- 💾 **本地缓存** - 歌词缓存，减少重复读取
- 🔍 **自动检测** - 自动识别歌曲切换和播放状态

## 📋 系统要求

- **操作系统**: Windows 10/11
- **Python**: 3.8 或更高版本
- **网易云音乐**: 3.1.25 - 3.1.30 版本
- **硬件**: HALO OIXELBAR 音箱 + USB数据线

## 🚀 快速开始

### 方法一：Windows一键运行

1. 下载或克隆本项目
2. 双击运行 `run.bat`
3. 开始使用！

### 方法二：手动安装

```bash
# 克隆项目
git clone https://github.com/nxz1026/HaloLrcSync.git
cd HaloLrcSync

# 安装依赖
pip install -r requirements.txt

# 运行程序
python src/main.py
```

## 📖 使用说明

### 前提条件

1. **打开网易云音乐**
2. **播放任意歌曲**
3. **开启桌面歌词功能**（重要！）
4. **运行本程序**

### 基本命令

```bash
# 启动歌词同步
python src/main.py

# 检查状态
python src/main.py --status

# 列出USB设备
python src/main.py --list-devices

# 指定串口设备
python src/main.py --port COM3
```

## 🛠️ 工作原理

```
┌─────────────────────────────────────────────────────────┐
│              网易云音乐进程 (cloudmusic.exe)              │
│  ┌─────────────────────────────────────────────────┐    │
│  │           cloudmusic.dll (内存空间)               │    │
│  │  ┌─────────────────────────────────────────┐    │    │
│  │  │   歌词数据 (Unicode 字符串)              │    │    │
│  │  │   地址偏移: 0x01DF44D0 + 指针偏移        │    │    │
│  │  └─────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
                          │
                          │ ReadProcessMemory
                          ▼
┌─────────────────────────────────────────────────────────┐
│              HaloLrcSync (本软件)                       │
│  ┌──────────────────┐    ┌──────────────────────────┐  │
│  │ cloudmusic_reader│───▶│   USB 发送到音箱          │  │
│  │   内存读取器     │    │   显示歌词               │  │
│  └──────────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
HaloLrcSync/
├── src/
│   ├── __init__.py           # 包信息
│   ├── main.py               # 主程序入口
│   ├── config.py             # 配置管理
│   ├── cloudmusic_reader.py  # 内存读取器 ⭐核心
│   ├── lrc_parser.py         # 歌词解析器
│   └── usb_comm.py           # USB通信模块
├── docs/
│   └── usb_protocol.md       # USB协议说明
├── requirements.txt          # 依赖列表
├── run.bat                   # Windows启动脚本
└── README.md
```

## 🔧 支持的网易云音乐版本

| 版本 | 状态 |
|------|------|
| 3.1.30 | ✅ 支持 |
| 3.1.29 | ✅ 支持 |
| 3.1.28 | ✅ 支持 |
| 3.1.27 | ✅ 支持 |
| 3.1.26 | ✅ 支持 |
| 3.1.25 | ✅ 支持 |

> 📝 如果您的版本不在列表中，程序会尝试使用默认偏移，可能需要手动更新地址

## ⚙️ 配置说明

配置文件位于：`C:\Users\你的用户名\.halo_lrc_sync\config.json`

```json
{
  "lyrics": {
    "scroll_speed": 1,
    "display_duration": 3,
    "max_chars_per_line": 20
  },
  "usb": {
    "device_id": "",
    "baud_rate": 9600,
    "auto_detect": true
  }
}
```

## ❓ 常见问题

### Q: 提示"网易云音乐未运行"？

A: 请确保：
1. 网易云音乐已安装并运行
2. 网易云音乐开启了桌面歌词功能
3. 播放了一首歌曲

### Q: 歌词读取不到？

A: 检查以下几点：
1. 网易云音乐版本是否在支持列表中
2. 是否开启了桌面歌词功能
3. 程序是否以管理员权限运行（部分系统需要）

### Q: 如何开启桌面歌词？

A: 在网易云音乐中：
- 右键歌曲播放界面
- 选择"桌面歌词"选项

### Q: 程序需要管理员权限吗？

A: 内存读取需要足够的进程访问权限。如果遇到权限问题，请尝试以管理员身份运行。

## 🔧 开发说明

### 内存地址更新

如果网易云音乐更新后地址变化，可以更新 `cloudmusic_reader.py` 中的 `VERSION_ADDRESS_MAP`：

```python
VERSION_ADDRESS_MAP = {
    "3.1.31": (0x新的基地址, 偏移1, 偏移2, ...),
}
```

### 添加新版本支持

参考以下资源获取最新的内存地址：

- [地址查找指南](docs/address_guide.md) - 详细的步骤说明
- [HaloPixelToolBox](https://github.com/XFEstudio/HaloPixelToolBox) - 项目会持续更新地址
- [地址扫描脚本](docs/address_scanner.py) - 辅助工具

### 地址更新步骤

1. 网易云音乐发布新版本
2. 使用 Cheat Engine 查找新地址（见 `docs/address_guide.md`）
3. 更新 `src/cloudmusic_reader.py` 中的 `VERSION_ADDRESS_MAP`
4. 提交 PR 到本项目

## 📚 参考项目

- [HaloPixelToolBox](https://github.com/XFEstudio/HaloPixelToolBox) - C# 实现的歌词同步工具
- [NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi) - 网易云音乐API

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## ⚠️ 免责声明

- 本项目仅用于学习和研究目的
- 请勿用于商业用途
- 歌词版权归原作者所有

---

**Made with ❤️ for HALO OIXELBAR users**
