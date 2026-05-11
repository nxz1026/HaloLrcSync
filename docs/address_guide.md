# 网易云音乐歌词内存地址查找指南

> 当网易云音乐更新后，按照以下步骤查找新的内存地址

## 📋 工具准备

### 1. Cheat Engine (推荐)

下载链接：https://www.cheatengine.org/downloads.php

功能强大的内存扫描工具，支持：
- 精确值扫描
- 指针扫描
- 内存区域浏览

### 2. x64dbg (可选)

下载链接：https://x64dbg.com/

调试器，可用于更深入的内存分析

---

## 🎯 查找步骤

### 第一步：准备工作

1. 打开网易云音乐
2. 播放一首歌
3. **开启桌面歌词功能**（必须！）
4. 打开 Cheat Engine
5. 点击 "Process List" (左上角图标)
6. 找到 `cloudmusic.exe` 并点击 Open

### 第二步：扫描歌词字符串

1. 确保桌面歌词显示的是单行歌词
2. 在 Cheat Engine 中输入歌词文本内容
3. 选择 String (字符串) 扫描类型
4. 点击 First Scan

```
示例歌词：窗外的麻雀在电线杆上站
```

### 第三步：缩小范围

1. 稍微改变歌词（比如等歌词自动滚动）
2. 输入新的歌词内容
3. 点击 Next Scan
4. 重复直到剩下少量结果

### 第四步：验证地址

1. 双击每个结果查看内存内容
2. 找到包含完整歌词文本的地址
3. 这个地址就是**基地址**

```
示例找到的地址：cloudmusic.dll+0x01DF44D0
```

### 第五步：找出指针偏移

由于基地址会变化，需要找出**静态指针**：

1. 右键找到的地址
2. 选择 "Find what accesses this address"
3. 查看哪些代码访问了这个地址
4. 分析访问模式，找出指针链

### 第六步：验证指针链

典型的歌词指针链结构：

```
cloudmusic.dll + 基地址偏移
    ↓ [指针偏移1]
第二级地址
    ↓ [指针偏移2]
第三级地址
    ↓ ...
    ↓ [最终偏移]
歌词文本地址
```

---

## 📝 地址格式说明

在代码中的格式：

```python
# 格式：(基地址偏移, 指针偏移1, 指针偏移2, ..., 最终偏移)
VERSION_ADDRESS_MAP = {
    "3.1.30": (0x01DF44D0, 0x120, 0x8, 0x0),
}
```

### 解析：

```
0x01DF44D0  - cloudmusic.dll 的基地址偏移
     ↓
    +0x120   - 第一级指针偏移
     ↓
    +0x8     - 第二级指针偏移
     ↓
    +0x0     - 最终偏移（歌词文本）
```

---

## 🔧 快速验证方法

### 使用已知的地址模式

1. 打开 Cheat Engine
2. 选择 `cloudmusic.exe` 进程
3. 使用 "Memory View" 窗口
4. Ctrl+G 跳转到基地址

```
示例：cloudmusic.dll + 0x01DF44D0
```

5. 查看该地址附近的数据
6. 如果是歌词数据，说明地址正确

---

## 📊 查找演示（以版本 3.1.30 为例）

### 原始数据

```
基地址：cloudmusic.dll + 0x01DF44D0
指针偏移链：[0x120, 0x8, 0x0]
```

### 代码表示

```python
VERSION_ADDRESS_MAP = {
    "3.1.30": (0x01DF44D0, 0x120, 0x8, 0x0),
}
```

### 读取过程

```python
# 1. 获取 cloudmusic.dll 的加载基址
dll_base = get_module_base("cloudmusic.dll")

# 2. 加上基地址偏移
address = dll_base + 0x01DF44D0

# 3. 读取第一级指针
pointer1 = read_memory(address)

# 4. 加上第一级偏移
address = pointer1 + 0x120

# 5. 读取第二级指针
pointer2 = read_memory(address)

# 6. 加上第二级偏移
address = pointer2 + 0x8

# 7. 读取歌词文本
lyrics = read_string(address)
```

---

## ⚠️ 注意事项

### 1. 版本匹配

每个网易云音乐版本可能有不同的地址，**必须确认版本号**：

```bash
# 查看网易云音乐版本
# 设置 -> 关于 -> 版本号
```

### 2. 桌面歌词必须开启

网易云音乐只有在开启桌面歌词时才会将歌词加载到内存中

### 3. 内存权限

读取其他进程的内存可能需要**管理员权限**

### 4. 地址会变化

每次网易云音乐更新后：
- 基地址可能变化
- 偏移量可能变化
- 需要重新查找

---

## 🔄 更新代码

找到新地址后，更新 `cloudmusic_reader.py`：

```python
VERSION_ADDRESS_MAP = {
    # 旧版本
    "3.1.30": (0x01DF44D0, 0x120, 0x8, 0x0),
    
    # 新版本（添加这里）
    "3.2.0": (0x新的基地址, 偏移1, 偏移2, ...),
}
```

---

## 🛠️ 自动化工具

项目中包含了一个地址扫描脚本（见 `docs/address_scanner.py`）

使用方法：

```bash
python docs/address_scanner.py
```

脚本会：
1. 自动检测网易云音乐进程
2. 扫描内存中的歌词字符串
3. 输出可能的地址和偏移

---

## 📞 获取帮助

如果查找遇到问题：

1. 查看 [HaloPixelToolBox Issues](https://github.com/XFEstudio/HaloPixelToolBox/issues)
2. 查看 [Cheat Engine 教程](https://wiki.cheatengine.org/)
3. 提交 Issue 到本项目

---

## 📚 参考资源

- [Cheat Engine 官方文档](https://wiki.cheatengine.org/)
- [内存读取基础教程](https://guidedhacking.com/)
- [指针扫描教程](https://wiki.cheatengine.org/index.php?title=Pointer_scanning)
