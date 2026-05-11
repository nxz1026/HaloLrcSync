#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HALO OIXELBAR 歌词同步主程序
直接从网易云音乐进程中读取歌词，无需API

参考项目：HaloPixelToolBox (https://github.com/XFEstudio/HaloPixelToolBox)
"""

import sys
import time
import threading
import signal
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.config import get_config
from src.cloudmusic_reader import CloudMusicMemoryReader, find_cloudmusic_version, get_supported_versions
from src.lrc_parser import parse_lrc
from src.usb_comm import get_usb_communicator


class LyricSynchronizer:
    """歌词同步器 - 使用内存读取方式"""
    
    def __init__(self):
        """初始化"""
        self.config = get_config()
        self.reader = CloudMusicMemoryReader()
        self.usb = get_usb_communicator()
        self.running = False
        self.current_song_id = None
        self.current_lyric = None
        self.current_position_ms = 0
        self.last_lyric_index = -1
        self.last_lyrics_text = ""
        self._lock = threading.Lock()
    
    def start(self):
        """启动同步器"""
        if self.running:
            print("[Sync] 已在运行中")
            return
        
        self.running = True
        print("[Sync] 开始歌词同步...")
        
        # 初始化网易云音乐内存读取器
        print("[Sync] 初始化网易云音乐内存读取器...")
        if not self.reader.initialize():
            print("[Sync] 网易云音乐未运行或版本不支持")
            print(f"[Sync] 支持的版本: {', '.join(get_supported_versions())}")
            return
        
        # 连接USB设备
        if not self.usb.connect():
            print("[Sync] USB设备连接失败，使用模拟模式")
        
        # 启动主循环线程
        sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        sync_thread.start()
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._handle_interrupt)
        signal.signal(signal.SIGTERM, self._handle_interrupt)
    
    def stop(self):
        """停止同步器"""
        print("[Sync] 正在停止...")
        self.running = False
        self.usb.clear_display()
        self.usb.disconnect()
        print("[Sync] 已停止")
    
    def _handle_interrupt(self, signum, frame):
        """处理中断信号"""
        print("\n[Sync] 收到中断信号")
        self.stop()
        sys.exit(0)
    
    def _sync_loop(self):
        """主同步循环"""
        show_startup = True
        
        while self.running:
            try:
                # 检查网易云音乐是否还在运行
                if not self.reader.is_ready():
                    print("[Sync] 网易云音乐已关闭，等待重新启动...")
                    time.sleep(2)
                    # 尝试重新初始化
                    if self.reader.initialize():
                        print("[Sync] 网易云音乐已重新连接")
                        show_startup = True
                    continue
                
                # 读取歌词
                lyrics = self.reader.read_lyrics()
                
                if lyrics and lyrics != self.last_lyrics_text:
                    self.last_lyrics_text = lyrics
                    
                    # 显示启动信息
                    if show_startup:
                        print(f"\n{'='*60}")
                        print("[Sync] 网易云歌词同步已启动!")
                        print(f"[Sync] 版本: {self.reader.version}")
                        print(f"{'='*60}\n")
                        show_startup = False
                    
                    # 解析歌词（如果包含时间戳）
                    self._process_lyrics(lyrics)
                
                time.sleep(0.05)  # 50ms刷新间隔
                
            except Exception as e:
                print(f"[Sync] 同步错误: {e}")
                time.sleep(1)
    
    def _process_lyrics(self, lyrics: str):
        """
        处理歌词文本
        
        Args:
            lyrics: 原始歌词文本
        """
        # 检查是否包含时间戳（[mm:ss.xx] 格式）
        if '[' in lyrics and ']' in lyrics:
            # 尝试解析LRC格式
            try:
                parser = parse_lrc(lyrics)
                if len(parser) > 0:
                    # 取当前行
                    current_line = parser[0]
                    self._display_lyric(current_line.text, current_line.index, len(parser))
                    return
            except Exception:
                pass
        
        # 直接显示原始歌词
        self._display_lyric(lyrics.strip(), 0, 1)
    
    def _display_lyric(self, text: str, line_index: int = 0, total_lines: int = 1):
        """
        显示歌词
        
        Args:
            text: 歌词文本
            line_index: 行索引
            total_lines: 总行数
        """
        if not text:
            return
        
        print(f"[Lyric] {text}")
        
        # 发送到USB设备
        success = self.usb.send_lyric_line(
            text=text,
            line_index=line_index,
            total_lines=total_lines
        )
        
        if not success:
            print("[Sync] 歌词发送失败")
    
    def _clear_display(self):
        """清空显示"""
        self.usb.clear_display()
        self.current_lyric = None
        self.last_lyrics_text = ""


def list_devices():
    """列出所有USB设备"""
    print("可用的串口设备:")
    devices = get_usb_communicator().list_devices()
    
    if not devices:
        print("  未找到设备")
        return
    
    for i, device in enumerate(devices, 1):
        print(f"  {i}. {device.port} - {device.description}")
        print(f"     HWID: {device.hwid}")


def check_status():
    """检查状态"""
    print("=" * 60)
    print("状态检查")
    print("=" * 60)
    
    # 检查网易云音乐
    version = find_cloudmusic_version()
    if version:
        print(f"✅ 网易云音乐: 运行中 (版本: {version})")
        supported = get_supported_versions()
        if version in supported:
            print("  └── 版本支持: ✅")
        else:
            print("  └── 版本支持: ⚠️  可能需要更新地址偏移")
    else:
        print("❌ 网易云音乐: 未运行")
        print("   请确保已安装并运行网易云音乐，且开启了桌面歌词功能")
    
    print()
    print("支持的网易云音乐版本:")
    for v in get_supported_versions():
        print(f"  - {v}")
    
    print()
    print("使用方法:")
    print("  1. 打开网易云音乐")
    print("  2. 播放任意歌曲")
    print("  3. 开启桌面歌词功能")
    print("  4. 运行本程序")


def main():
    """主函数"""
    print("=" * 60)
    print("HALO OIXELBAR 歌词同步器")
    print("(内存读取模式 - 无需API)")
    print("=" * 60)
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description="HALO OIXELBAR 歌词同步器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python src/main.py              # 启动同步器
  python src/main.py --status     # 检查状态
  python src/main.py --list-devices  # 列出USB设备
  python src/main.py --port COM3  # 指定串口设备

前提条件:
  1. 网易云音乐已安装并运行
  2. 网易云音乐开启了桌面歌词功能
  3. 电脑已连接 HALO OIXELBAR 音箱
        """
    )
    parser.add_argument("--list-devices", action="store_true", help="列出可用的串口设备")
    parser.add_argument("--status", action="store_true", help="检查网易云音乐状态")
    parser.add_argument("--port", type=str, help="指定串口设备")
    parser.add_argument("--config", type=str, help="配置文件路径")
    
    args = parser.parse_args()
    
    if args.list_devices:
        list_devices()
        return
    
    if args.status:
        check_status()
        return
    
    # 初始化
    if args.config:
        get_config(args.config)
    
    # 创建并启动同步器
    synchronizer = LyricSynchronizer()
    
    # 如果指定了端口
    if args.port:
        print(f"[Main] 使用指定端口: {args.port}")
        get_usb_communicator().connect(args.port)
    
    try:
        synchronizer.start()
        
        # 保持主线程运行
        while synchronizer.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[Main] 用户中断")
    finally:
        synchronizer.stop()


if __name__ == "__main__":
    main()
