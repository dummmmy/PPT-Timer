@echo off
setlocal

REM 创建虚拟环境（可选）
if not exist .venv (
    py -3 -m venv .venv
)
call .venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r requirements.txt

REM 打包为单文件无控制台窗口的 exe
pyinstaller --noconfirm --clean --onefile --windowed --name PPTCountdown main.py

echo 输出文件位于 dist\PPTCountdown.exe
pause

