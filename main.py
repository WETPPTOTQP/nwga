import sys
import random
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QComboBox, QInputDialog, QGridLayout, QDialog, QDialogButtonBox, QGraphicsBlurEffect

class BlurEffect(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.blur_effect = QGraphicsBlurEffect()
        self.blur_effect.setBlurRadius(10)
        self.setGraphicsEffect(self.blur_effect)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 150);")

class GameOverDialog(QDialog):
    def __init__(self, won, score, parent=None):
        super().__init__(parent)
        self.setWindowTitle("游戏结束")
        self.layout = QVBoxLayout(self)

        if won:
            self.layout.addWidget(QLabel(f"恭喜你，你赢了！得分: {score}"))
        else:
            self.layout.addWidget(QLabel(f"很遗憾，时间到了。得分: {score}"))

        self.button_box = QDialogButtonBox(QDialogButtonBox.Retry | QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Retry).setText("重新开始")
        self.button_box.button(QDialogButtonBox.Ok).setText("菜单")
        self.button_box.button(QDialogButtonBox.Cancel).setText("返回")

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.Retry).clicked.connect(self.retry)

        self.layout.addWidget(self.button_box)

    def retry(self):
        self.done(2)

class GameWindow(QMainWindow):
    def __init__(self, game_type, grid_size, time_limit):
        super().__init__()
        self.game_type = game_type
        self.grid_size = grid_size
        self.time_limit = time_limit
        self.setWindowTitle(f"{self.game_type} - {self.time_limit}秒")

        if self.game_type == "苏尔特方格":
            self.setup_schulte_game()
        else:
            self.setup_color_text_game()

    def setup_schulte_game(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.timer_label = QLabel(f"Time left: {self.time_limit}")
        self.layout.addWidget(self.timer_label)

        self.grid_layout = QGridLayout()
        self.layout.addLayout(self.grid_layout)

        self.numbers = list(range(1, self.grid_size + 1))
        random.shuffle(self.numbers)

        self.buttons = []
        grid_dim = int(self.grid_size**0.5)
        for i in range(self.grid_size):
            button = QPushButton(str(self.numbers[i]))
            button.clicked.connect(lambda checked, b=button: self.button_clicked(b))
            self.buttons.append(button)
            self.grid_layout.addWidget(button, i // grid_dim, i % grid_dim)

        self.next_number = 1
        self.remaining_time = self.time_limit

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def setup_color_text_game(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.timer_label = QLabel(f"Time left: {self.time_limit}")
        self.layout.addWidget(self.timer_label)

        self.color_word_label = QLabel()
        self.color_word_label.setStyleSheet("font-size: 48px;")
        self.layout.addWidget(self.color_word_label)

        self.color_buttons_layout = QGridLayout()
        self.layout.addLayout(self.color_buttons_layout)

        self.colors = {"红色": "red", "绿色": "green", "蓝色": "blue", "黄色": "yellow"}
        self.buttons = []
        for i, (color_name, color_value) in enumerate(self.colors.items()):
            button = QPushButton(color_name)
            button.setStyleSheet(f"background-color: {color_value}")
            button.clicked.connect(lambda checked, c=color_name: self.color_text_button_clicked(c))
            self.buttons.append(button)
            self.color_buttons_layout.addWidget(button, i // 2, i % 2)

        self.score = 0
        self.remaining_time = self.time_limit

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        self.next_round()

    def next_round(self):
        self.correct_color_name = random.choice(list(self.colors.keys()))
        self.correct_color_value = self.colors[self.correct_color_name]

        word = random.choice(list(self.colors.keys()))

        self.color_word_label.setText(word)
        self.color_word_label.setStyleSheet(f"font-size: 48px; color: {self.correct_color_value}; qproperty-alignment: 'AlignCenter';")

    def color_text_button_clicked(self, clicked_color):
        if clicked_color == self.correct_color_name:
            self.score += 1
        self.next_round()

    def button_clicked(self, button):
        if self.game_type == "苏尔特方格":
            if int(button.text()) == self.next_number:
                button.setEnabled(False)
                self.next_number += 1
                if self.next_number > self.grid_size:
                    self.game_over(True)

    def update_timer(self):
        self.remaining_time -= 1
        self.timer_label.setText(f"Time left: {self.remaining_time}")
        if self.remaining_time == 0:
            self.game_over(False)

    def game_over(self, won):
        self.timer.stop()

        self.blur_widget = BlurEffect(self.central_widget)
        self.blur_widget.setGeometry(self.central_widget.rect())
        self.blur_widget.show()

        score = 0
        if self.game_type == "苏尔特方格":
            score = self.next_number - 1
        else:
            score = self.score

        dialog = GameOverDialog(won, score, self)
        result = dialog.exec()

        self.blur_widget.hide()

        if result == QDialog.Accepted:  # Menu
            self.main_menu = MainMenu()
            self.main_menu.show()
            self.close()
        elif result == 2:  # Retry
            self.new_game = GameWindow(self.game_type, self.grid_size, self.time_limit)
            self.new_game.show()
            self.close()
        else:  # Back
            self.close()

class TimerSelectionWindow(QMainWindow):
    def __init__(self, game_type, grid_size):
        super().__init__()
        self.game_type = game_type
        self.grid_size = grid_size
        self.setWindowTitle("定时选择")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.time_selector = QComboBox()
        self.time_selector.addItems(["10秒", "30秒", "自定义"])

        self.start_button = QPushButton("开始")

        self.layout.addWidget(QLabel("选择时间:"))
        self.layout.addWidget(self.time_selector)
        self.layout.addWidget(self.start_button)

        self.start_button.clicked.connect(self.start_game)
        self.time_selector.currentTextChanged.connect(self.handle_time_selection)

    def handle_time_selection(self, text):
        if text == "自定义":
            time, ok = QInputDialog.getInt(self, "自定义时间", "请输入时间（秒）:", 1, 1, 600, 1)
            if ok:
                self.time_selector.setItemText(2, f"{time}秒")

    def start_game(self):
        time_text = self.time_selector.currentText().replace("秒", "")
        time_in_seconds = int(time_text)
        self.game_window = GameWindow(self.game_type, self.grid_size, time_in_seconds)
        self.game_window.show()
        self.close()


class ModeSelectionWindow(QMainWindow):
    def __init__(self, game_type):
        super().__init__()
        self.setWindowTitle(f"{game_type} 模式选择")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.grid_3x3_button = QPushButton("3x3")
        self.grid_4x4_button = QPushButton("4x4")
        self.grid_5x5_button = QPushButton("5x5")
        self.custom_button = QPushButton("自定义")

        self.layout.addWidget(self.grid_3x3_button)
        self.layout.addWidget(self.grid_4x4_button)
        self.layout.addWidget(self.grid_5x5_button)
        self.layout.addWidget(self.custom_button)

        self.grid_3x3_button.clicked.connect(lambda: self.open_timer_selection(9))
        self.grid_4x4_button.clicked.connect(lambda: self.open_timer_selection(16))
        self.grid_5x5_button.clicked.connect(lambda: self.open_timer_selection(25))
        self.custom_button.clicked.connect(self.open_custom_mode_selection)

    def open_timer_selection(self, grid_size):
        self.timer_selection_window = TimerSelectionWindow(self.windowTitle().split(' ')[0], grid_size)
        self.timer_selection_window.show()
        self.close()

    def open_custom_mode_selection(self):
        print("打开自定义模式选择")


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("游戏选择")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.schulte_button = QPushButton("苏尔特方格")
        self.color_text_button = QPushButton("彩色文字")

        self.layout.addWidget(self.schulte_button)
        self.layout.addWidget(self.color_text_button)

        self.schulte_button.clicked.connect(self.open_schulte_mode_selection)
        self.color_text_button.clicked.connect(self.open_color_text_mode_selection)

    def open_schulte_mode_selection(self):
        self.mode_selection_window = ModeSelectionWindow("苏尔特方格")
        self.mode_selection_window.show()
        self.close()

    def open_color_text_mode_selection(self):
        self.mode_selection_window = ModeSelectionWindow("彩色文字")
        self.mode_selection_window.show()
        self.close()


import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    stylesheet_path = resource_path("stylesheet.qss")
    with open(stylesheet_path, "r") as f:
        app.setStyleSheet(f.read())

    main_menu = MainMenu()
    main_menu.show()
    sys.exit(app.exec())