from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PySide6.QtGui import QPalette, QColor

app = QApplication([])

# 创建主窗口
window = QWidget()
window.setWindowTitle("QSS with QPalette Example")
window.resize(300, 200)

# 定义调色板
palette = QPalette()
palette.setColor(QPalette.Window, QColor("#FFFFFF"))       # 背景色
palette.setColor(QPalette.WindowText, QColor("#333333"))   # 文本色
palette.setColor(QPalette.Button, QColor("#3F51B5"))       # 按钮背景色
palette.setColor(QPalette.ButtonText, QColor("#FFFFFF"))   # 按钮文本色

# 应用调色板
app.setPalette(palette)

# 设置 QSS
app.setStyleSheet("""
    QPushButton:hover {
        background-color: #757de8;
    }
""")

# 创建按钮
button = QPushButton("Click Me")

# 设置布局
layout = QVBoxLayout()
layout.addWidget(button)
window.setLayout(layout)

# 显示窗口
window.show()

app.exec()