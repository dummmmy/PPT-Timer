## PPT 倒计时工具（Windows .exe）

轻量透明叠加窗口，适合在 PowerPoint 演示时显示倒计时。

### 功能
- 透明背景、无边框、始终置顶、可拖动
- 时间点击可编辑（1-180 分钟），显示格式 MM:SS
- 开始/暂停（同一按钮）、重置、关闭
- 悬停显示控制按钮
- 智能提醒：最后 30s 橙色；最后 10s 红色闪烁；结束明显提示
- 快捷键：空格开始/暂停、R 重置、Esc 退出

### 运行（开发）
```bash
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### 打包为 .exe
```bash
build.bat
```
生成文件：`dist/PPTCountdown.exe`

### 使用提示
- 拖动时间数字可移动窗口位置
- 单击时间进入编辑（运行状态下为避免误触，需先暂停）
- 颜色为：深红（正常）→ 橙色（<=30s）→ 红色闪烁（<=10s）

### 云端打包（GitHub Actions）
1. 推送代码到 GitHub 仓库（包含本项目文件）
2. 在仓库页面打开 Actions 标签 → 选择 “Build Windows EXE” → Run workflow
3. 运行完成后，在该 workflow 的 Artifacts 区域下载 `PPTCountdown-windows-exe`，其中包含 `PPTCountdown.exe`

### 自动发布 Release（含校验文件）
- 打标签触发发布：
```bash
git tag v1.0.0
git push origin v1.0.0
```
- 工作流会自动：构建 exe → 计算 SHA256 → 创建 GitHub Release → 上传 `PPTCountdown.exe` 与 `PPTCountdown.exe.sha256`
- 版本号可在 `VERSION` 文件中维护（推荐同步打标签）



