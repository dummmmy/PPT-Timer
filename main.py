import sys
from PySide6.QtCore import Qt, QTimer, QPoint, QEvent
from PySide6.QtGui import QFont, QCursor, QGuiApplication, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
)

class CountdownWindow(QWidget):
    MIN_MINUTES = 1
    MAX_MINUTES = 180

    COLOR_NORMAL = "#8B0000"  # 深红
    COLOR_ORANGE = "#FF8C00"
    COLOR_RED = "#FF0000"

    def __init__(self):
        super().__init__()

        # 窗口属性：无边框、透明背景、始终置顶
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)

        # 状态
        self.total_seconds = 15 * 60
        self.remaining_seconds = self.total_seconds
        self.is_running = False
        self.dragging = False
        self.drag_offset = QPoint()
        self._press_pos = None
        self._moved = False
        self.blink_state = False

        # 定时器
        self.tick_timer = QTimer(self)
        self.tick_timer.setInterval(1000)
        self.tick_timer.timeout.connect(self.on_tick)

        self.blink_timer = QTimer(self)
        self.blink_timer.setInterval(500)
        self.blink_timer.timeout.connect(self.on_blink)

        # 主要显示：时间
        self.time_label = QLabel(self.format_time(self.remaining_seconds))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet(
            f"QLabel{{color:{self.COLOR_NORMAL}; background: transparent;}}"
        )
        font = QFont("Segoe UI", 40, QFont.Bold)
        self.time_label.setFont(font)
        self.time_label.setCursor(QCursor(Qt.IBeamCursor))
        self.time_label.setMouseTracking(True)

        # 时间编辑框（点击时切换）
        self.time_edit = QLineEdit()
        self.time_edit.setVisible(False)
        self.time_edit.setFixedWidth(120)
        self.time_edit.setAlignment(Qt.AlignCenter)
        self.time_edit.setStyleSheet(
            "QLineEdit{color:#111; background: rgba(255,255,255,230); border:1px solid #aaa; border-radius:6px; padding:4px;}"
        )
        self.time_edit.returnPressed.connect(self.apply_edit_minutes)
        self.time_edit.editingFinished.connect(self.apply_edit_minutes)

        # 开始/暂停主按钮（常显）
        self.start_button = QPushButton("▶")
        self.start_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.start_button.setFixedSize(40, 40)
        self.start_button.setStyleSheet(
            "QPushButton{background:#ffffff; color:#111; border:none; border-radius:20px; font-size:18px;}"
            "QPushButton:hover{background:#f0f0f0;}"
            "QPushButton:pressed{background:#e6e6e6;}"
        )
        self.start_button.clicked.connect(self.toggle_start_pause)

        # 顶部行：时间显示 + 开始按钮
        top_row = QHBoxLayout()
        top_row.setContentsMargins(12, 12, 12, 12)
        top_row.setSpacing(8)

        # 简化：直接在布局中切换 label 与 edit 的可见性
        time_box = QVBoxLayout()
        time_box.setContentsMargins(0, 0, 0, 0)
        time_box.setSpacing(0)
        time_box.addWidget(self.time_label)
        time_box.addWidget(self.time_edit)
        self.time_edit.setVisible(False)

        top_row.addLayout(time_box, 1)
        top_row.addWidget(self.start_button, 0, Qt.AlignVCenter)

        # 根布局（删除了底部悬浮控制区）
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)
        root.addLayout(top_row)

        # 快捷键
        QShortcut(QKeySequence(Qt.Key_Space), self, activated=self.toggle_start_pause)
        QShortcut(QKeySequence("R"), self, activated=self.reset_timer)
        QShortcut(QKeySequence(Qt.Key_Escape), self, activated=self.safe_close)

        # 初始大小与位置
        self.adjustSize()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(int(screen.width() * 0.7), int(screen.height() * 0.1))

    # 计时逻辑
    def on_tick(self):
        if self.remaining_seconds <= 0:
            self.finish_timer()
            return
        self.remaining_seconds -= 1
        self.update_time_view()
        if self.remaining_seconds <= 10 and not self.blink_timer.isActive():
            self.blink_timer.start()

    def on_blink(self):
        if self.remaining_seconds <= 10:
            self.blink_state = not self.blink_state
            self.update_time_view()
        else:
            self.blink_timer.stop()
            self.blink_state = False

    def format_time(self, seconds: int) -> str:
        m, s = divmod(max(0, seconds), 60)
        return f"{m:02d}:{s:02d}"

    def update_time_view(self):
        if self.remaining_seconds <= 10:
            color = self.COLOR_RED if self.blink_state else "#AA0000"
        elif self.remaining_seconds <= 30:
            color = self.COLOR_ORANGE
        else:
            color = self.COLOR_NORMAL
        self.time_label.setStyleSheet(f"QLabel{{color:{color}; background: transparent;}}")
        self.time_label.setText(self.format_time(self.remaining_seconds))

    def toggle_start_pause(self):
        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        if self.remaining_seconds <= 0:
            self.remaining_seconds = self.total_seconds
        self.tick_timer.start()
        self.is_running = True
        self.start_button.setText("⏸")

    def pause_timer(self):
        self.tick_timer.stop()
        self.is_running = False
        self.start_button.setText("▶")

    def reset_timer(self):
        self.pause_timer()
        self.remaining_seconds = self.total_seconds
        self.blink_timer.stop()
        self.blink_state = False
        self.update_time_view()

    def finish_timer(self):
        self.pause_timer()
        self.remaining_seconds = 0
        self.update_time_view()
        self.blink_state = False
        self.blink_timer.start()
        QTimer.singleShot(2200, self.blink_timer.stop)

    # 进入编辑（仅当未运行）
    def enter_edit_mode(self):
        minutes = max(1, self.total_seconds // 60)
        self.time_edit.setText(str(minutes))
        self.time_label.setVisible(False)
        self.time_edit.setVisible(True)
        self.time_edit.setFocus()
        self.time_edit.selectAll()

    def apply_edit_minutes(self):
        text = self.time_edit.text().strip()
        try:
            minutes = int(text)
        except ValueError:
            minutes = max(self.MIN_MINUTES, min(self.MAX_MINUTES, self.total_seconds // 60))
        minutes = max(self.MIN_MINUTES, min(self.MAX_MINUTES, minutes))
        self.total_seconds = minutes * 60
        self.remaining_seconds = self.total_seconds
        self.blink_timer.stop()
        self.blink_state = False
        self.update_time_view()
        self.time_edit.setVisible(False)
        self.time_label.setVisible(True)

    def safe_close(self):
        self.close()

    # 拖动逻辑：窗口任意区域左键按住可拖动（编辑框激活时不拖动）
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 如果正在编辑输入框且鼠标在输入框内，则不拦截拖动，交给输入框处理
            if self.time_edit.isVisible() and self.time_edit.underMouse():
                return super().mousePressEvent(event)
            self._press_pos = event.globalPosition().toPoint()
            self._moved = False
            self.dragging = True
            self.drag_offset = self._press_pos - self.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging and (event.buttons() & Qt.LeftButton):
            now_pos = event.globalPosition().toPoint()
            if self._press_pos is not None and (now_pos - self._press_pos).manhattanLength() > 3:
                self._moved = True
            self.move(now_pos - self.drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            was_moved = self._moved
            self.dragging = False
            event.accept()
            # 未移动且在时间标签上，且未运行时，进入编辑
            if not was_moved and not self.is_running and self.time_label.underMouse():
                self.enter_edit_mode()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.time_label.underMouse() and not self.is_running:
            self.enter_edit_mode()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

def main():
    app = QApplication(sys.argv)
    win = CountdownWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
