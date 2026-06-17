#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# ===== 请在这里修改你的路径 =====
# Windows 默认路径（请将 "你的用户名" 替换为你的实际 Windows 用户名）
TARGET_DIR = r"C:\Users\你的用户名\AppData\Roaming\Unity\Asset Store-5.x"
OUTPUT_DIR = r"C:\Users\你的用户名\Downloads\UnityPackage_Manifests"
# ================================

def main():
    root = Path(TARGET_DIR)
    out = Path(OUTPUT_DIR)
    out.mkdir(parents=True, exist_ok=True)

    pkg_files = list(root.rglob('*.unitypackage'))
    print(f"🔍 找到 {len(pkg_files)} 个 .unitypackage 文件")

    for idx, pkg in enumerate(pkg_files, 1):
        print(f"[{idx}/{len(pkg_files)}] 处理: {pkg.name}")
        cmd = [sys.executable, 'extract_package_info.py', str(pkg), '-o', str(out)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"   ❌ 失败: {result.stderr}")
        else:
            print(f"   ✅ 完成")

if __name__ == '__main__':
    main()