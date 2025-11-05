"""
PyInstaller 打包脚本 - 可在 PyCharm 中直接运行
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    print("=" * 50)
    print("PPT 倒计时工具 - PyInstaller 打包")
    print("=" * 50)
    
    # 检查是否安装了 PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller 已安装: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
        print("✓ PyInstaller 安装完成")
    
    # 检查 main.py 是否存在
    if not Path("main.py").exists():
        print("✗ 错误: 找不到 main.py 文件")
        sys.exit(1)
    
    print("\n开始打包...")
    print("-" * 50)
    
    # PyInstaller 命令
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name", "PPTCountdown",
        "main.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("✓ 打包成功！")
        print(f"输出文件: {Path('dist/PPTCountdown.exe').absolute()}")
        print("=" * 50)
        
        # 询问是否打开文件夹
        try:
            dist_path = Path("dist").absolute()
            if sys.platform == "win32":
                os.startfile(dist_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", dist_path])
            else:
                subprocess.run(["xdg-open", dist_path])
        except Exception as e:
            print(f"无法自动打开文件夹: {e}")
            
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("✗ 打包失败！")
        print(f"错误代码: {e.returncode}")
        print("=" * 50)
        sys.exit(1)

if __name__ == "__main__":
    main()

