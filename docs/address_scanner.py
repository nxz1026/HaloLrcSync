#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网易云音乐歌词内存地址扫描器
自动扫描内存中的歌词地址

使用方法：
    python address_scanner.py

需要：
    - 网易云音乐运行中
    - 已开启桌面歌词
    - 播放一首歌曲
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import psutil
except ImportError:
    print("[错误] 需要安装 psutil: pip install psutil")
    sys.exit(1)


def find_cloudmusic_process():
    """查找网易云音乐进程"""
    print("[扫描] 查找网易云音乐进程...")
    
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            if proc.info['name'] and 'cloudmusic' in proc.info['name'].lower():
                print(f"[找到] 进程: {proc.info['name']} (PID: {proc.info['pid']})")
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return None


def get_cloudmusic_version():
    """获取网易云音乐版本"""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\cloudmusic.exe"
        )
        version, _ = winreg.QueryValueEx(key, "Version")
        winreg.CloseKey(key)
        return version
    except:
        return "未知"


def scan_memory_for_lyrics(process):
    """
    扫描进程内存查找歌词
    
    这是一个简化版本，真正定位需要使用 Cheat Engine
    """
    print("\n[提示] 这是一个演示脚本")
    print("[提示] 真正的内存地址定位需要使用 Cheat Engine")
    print()
    print("=" * 60)
    print("手动定位步骤：")
    print("=" * 60)
    print("""
1. 下载 Cheat Engine: https://www.cheatengine.org/downloads.php

2. 打开 Cheat Engine，点击 "Open Process"
   选择 cloudmusic.exe

3. 确保网易云音乐开启了桌面歌词功能

4. 在 Cheat Engine 中：
   - Value Type 选择 "String"
   - 输入当前显示的歌词文本
   - 点击 "First Scan"

5. 等待扫描完成，右键结果查看内存

6. 找到包含歌词的地址后：
   - 右键选择 "Find what accesses this address"
   - 分析访问代码找出指针链

7. 最终得到地址格式：
   cloudmusic.dll + 0x01DF44D0
   
8. 提交 Issue 或 PR 更新到项目中
""")
    print("=" * 60)


def find_dll_base(process, dll_name="cloudmusic.dll"):
    """查找DLL加载基址"""
    try:
        for module in process.memory_maps():
            if dll_name.lower() in module.path.lower():
                return int(module.addr, 16)
    except:
        pass
    return None


def print_status():
    """打印当前状态"""
    print("=" * 60)
    print("网易云音乐歌词地址扫描器")
    print("=" * 60)
    
    # 检查进程
    process = find_cloudmusic_process()
    if not process:
        print("\n[错误] 未找到网易云音乐进程")
        print("[提示] 请确保：")
        print("  1. 网易云音乐已安装")
        print("  2. 网易云音乐正在运行")
        return False
    
    # 获取版本
    version = get_cloudmusic_version()
    print(f"[信息] 版本: {version}")
    
    # 查找DLL基址
    dll_base = find_dll_base(process)
    if dll_base:
        print(f"[信息] cloudmusic.dll 基址: 0x{dll_base:X}")
    
    return True


def main():
    """主函数"""
    print()
    
    # 检查系统
    if sys.platform != 'win32':
        print("[错误] 此工具仅支持 Windows 系统")
        sys.exit(1)
    
    # 打印状态
    if not print_status():
        sys.exit(1)
    
    # 获取进程
    process = find_cloudmusic_process()
    if not process:
        sys.exit(1)
    
    # 扫描内存
    scan_memory_for_lyrics(process)
    
    print()
    print("[提示] 查找完成后，请提交 Issue 帮助完善项目")
    print("[提示] 或者直接提交 Pull Request 更新代码")


if __name__ == "__main__":
    main()
