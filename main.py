import sys
from PySide6.QtCore import Qt, QTimer, QPoint, QEasingCurve, Property, QEvent
from PySide6.QtGui import QFont, QCursor, QGuiApplication, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QGraphicsOpacityEffect,
)

class FadeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._opacity_effect.setOpacity(0.0)
        self._opacity = 0.0

    def getOpacity(self):
        return self._opacity

    def setOpacity(self, value):
        self._opacity = value
        self._opacity_effect.setOpacity(value)

    opacity = Property(float, getOpacity, setOpacity)

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

        # 开始/暂停主按钮（始终可见）
        self.start_button = QPushButton("▶")
        self.start_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.start_button.setFixedSize(40, 40)
        self.start_button.setStyleSheet(
            "QPushButton{background:#ffffff; color:#111; border:none; border-radius:20px; font-size:18px;}"
            "QPushButton:hover{background:#f0f0f0;}"
            "QPushButton:pressed{background:#e6e6e6;}"
        )
        self.start_button.clicked.connect(self.toggle_start_pause)

        # 悬停控制区（重置、暂停、关闭）
        self.hover_controls = FadeWidget()
        self.hover_controls.setVisible(True)
        hover_layout = QHBoxLayout(self.hover_controls)
        hover_layout.setContentsMargins(0, 0, 0, 0)
        hover_layout.setSpacing(8)

        self.pause_button = QPushButton("⏸")
        self.reset_button = QPushButton("⟲")
        self.close_button = QPushButton("✕")
        for b in (self.pause_button, self.reset_button, self.close_button):
            b.setFixedSize(32, 32)
            b.setCursor(QCursor(Qt.PointingHandCursor))
            b.setStyleSheet(
                "QPushButton{background:#ffffff; color:#111; border:none; border-radius:16px; font-size:14px;}"
                "QPushButton:hover{background:#f0f0f0;}"
                "QPushButton:pressed{background:#e6e6e6;}"
            )
        self.pause_button.clicked.connect(self.toggle_start_pause)
        self.reset_button.clicked.connect(self.reset_timer)
        self.close_button.clicked.connect(self.safe_close)

        hover_layout.addWidget(self.pause_button)
        hover_layout.addWidget(self.reset_button)
        hover_layout.addWidget(self.close_button)

        # 顶部行：时间显示 + 开始按钮
        top_row = QHBoxLayout()
        top_row.setContentsMargins(12, 12, 12, 6)
        top_row.setSpacing(8)

        self.time_container = QWidget()
        time_stack = QStackedLayoutCompat(self.time_container)
        time_stack.addWidget(self.time_label)
        time_stack.addWidget(self.time_edit)
        self.time_stack = time_stack

        top_row.addWidget(self.time_container)
        top_row.addWidget(self.start_button, 0, Qt.AlignVCenter)

        # 底部行：悬停控制
        bottom_row = QHBoxLayout()
        bottom_row.setContentsMargins(12, 0, 12, 10)
        bottom_row.addWidget(self.hover_controls, 0, Qt.AlignLeft)

        # 根布局
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(0)
        root.addLayout(top_row)
        root.addLayout(bottom_row)

        # 初始：控制隐藏（透明）
        self.set_hover_visible(False, instant=True)

        # 交互：事件过滤用于 hover 显示
        self.installEventFilter(self)
        self.time_label.installEventFilter(self)
        self.hover_controls.installEventFilter(self)

        # 快捷键
        QShortcut(QKeySequence(Qt.Key_Space), self, activated=self.toggle_start_pause)
        QShortcut(QKeySequence("R"), self, activated=self.reset_timer)
        QShortcut(QKeySequence(Qt.Key_Escape), self, activated=self.safe_close)

        # 初始大小与位置
        self.adjustSize()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(int(screen.width() * 0.7), int(screen.height() * 0.1))

    # 事件过滤：控制 hover 可见性
    def eventFilter(self, obj, event):
        et = event.type()
        if et in (QEvent.Enter, QEvent.HoverEnter):
            self.set_hover_visible(True)
        elif et in (QEvent.Leave, QEvent.HoverLeave):
            if not self.rect().contains(self.mapFromGlobal(QCursor.pos())):
                self.set_hover_visible(False)
        return super().eventFilter(obj, event)

    # 拖动与点击编辑
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.time_label.underMouse():
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
            if (now_pos - self._press_pos).manhattanLength() > 3:
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
            if not was_moved and not self.is_running and self.time_label.underMouse():
                self.enter_edit_mode()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.time_label.underMouse():
            self.enter_edit_mode()
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    def set_hover_visible(self, visible: bool, instant: bool = False):
        target = 1.0 if visible else 0.0
        if instant:
            self.hover_controls.setVisible(True)
            self.hover_controls.setOpacity(target)
            if target == 0.0:
                self.hover_controls.setVisible(False)
            return
        from PySide6.QtCore import QPropertyAnimation

        self.hover_controls.setVisible(True)
        anim = QPropertyAnimation(self.hover_controls, b"opacity", self)
        anim.setDuration(180)
        anim.setStartValue(self.hover_controls.getOpacity())
        anim.setEndValue(target)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        def on_finished():
            if target == 0.0:
                self.hover_controls.setVisible(False)
        anim.finished.connect(on_finished)
        anim.start()

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
        self.pause_button.setText("⏸")

    def pause_timer(self):
        self.tick_timer.stop()
        self.is_running = False
        self.start_button.setText("▶")
        self.pause_button.setText("▶")

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

    def enter_edit_mode(self):
        minutes = max(1, self.total_seconds // 60)
        self.time_edit.setText(str(minutes))
        self.time_stack.setCurrentWidget(self.time_edit)
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
        self.time_stack.setCurrentWidget(self.time_label)

    def safe_close(self):
        self.close()

class QStackedLayoutCompat(QVBoxLayout):
    """
    轻量替代：用切换可见性模拟堆叠布局。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(0)
        self._widgets = []

    def addWidget(self, w):
        self._widgets.append(w)
        self.addWidget_(w)

    def addWidget_(self, w):
        super().addWidget(w)

    def setCurrentWidget(self, w):
        for each in self._widgets:
            each.setVisible(each is w)

def main():
    app = QApplication(sys.argv)
    win = CountdownWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
