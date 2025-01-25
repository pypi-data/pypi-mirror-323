from PySide6.QtWidgets import (
    QMainWindow, QMdiArea, QToolBar,
    QDialog, QVBoxLayout, QLineEdit,
    QPushButton, QFormLayout
)
from PySide6.QtGui import QAction
from .liteboty_stream import MainWindow


class NewStreamDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加新的视频流")

        layout = QFormLayout()

        self.broker = QLineEdit()
        self.broker.setPlaceholderText("例如: 10.8.2.2:6379")
        layout.addRow("Redis地址:", self.broker)

        self.channel = QLineEdit()
        self.channel.setPlaceholderText("例如: /video/raw")
        layout.addRow("订阅频道:", self.channel)

        self.decode = QLineEdit()
        self.decode.setText("RGB")
        layout.addRow("解码格式:", self.decode)

        buttons = QVBoxLayout()
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)

        buttons.addWidget(ok_button)
        buttons.addWidget(cancel_button)
        layout.addRow("", buttons)

        self.setLayout(layout)


class StreamUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("视频流监控系统")
        self.setGeometry(100, 100, 1200, 800)

        # 创建MDI区域
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        # 创建菜单栏
        self.create_menu_bar()

        # 创建工具栏
        self.create_tool_bar()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        new_stream = QAction("新建视频流", self)
        new_stream.setShortcut("Ctrl+N")
        new_stream.triggered.connect(self.add_new_stream)
        file_menu.addAction(new_stream)

        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 窗口菜单
        window_menu = menubar.addMenu("窗口")

        cascade = QAction("层叠排列", self)
        cascade.triggered.connect(self.mdi.cascadeSubWindows)
        window_menu.addAction(cascade)

        tile = QAction("平铺排列", self)
        tile.triggered.connect(self.mdi.tileSubWindows)
        window_menu.addAction(tile)

    def create_tool_bar(self):
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        new_stream_btn = QAction("新建视频流", self)
        new_stream_btn.triggered.connect(self.add_new_stream)
        toolbar.addAction(new_stream_btn)

    def add_new_stream(self):
        dialog = NewStreamDialog(self)
        if dialog.exec() == QDialog.Accepted:
            broker = dialog.broker.text()
            channel = dialog.channel.text()
            decode = dialog.decode.text()

            # 创建新的视频流窗口
            sub_window = MainWindow(broker, channel, decode)
            mdi_window = self.mdi.addSubWindow(sub_window)
            mdi_window.setWindowTitle(f"视频流 - {channel}")
            mdi_window.show()
