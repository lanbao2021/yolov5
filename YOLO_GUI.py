# -*- coding:utf-8 -*-
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('YOLOv5_GUI_1.0')
        self.resize(256, 200)

        global_widget = QWidget(self)
        global_widget_layout = QVBoxLayout(global_widget)

        grid_layout = QGridLayout()
        vertical_layout = QVBoxLayout()

        self.source_button = QPushButton('...')
        self.source_button.clicked.connect(self.get_source_file)
        self.source_line_edit = QLineEdit()

        self.weights_button = QPushButton('...')
        self.weights_button.clicked.connect(self.get_weights_file)
        self.weights_line_edit = QLineEdit()

        grid_layout.addWidget(QLabel('Source'), 0, 0)
        grid_layout.addWidget(self.source_line_edit, 0, 1)
        grid_layout.addWidget(self.source_button, 0, 2)
        grid_layout.addWidget(QLabel('Weights'), 1, 0)
        grid_layout.addWidget(self.weights_line_edit, 1, 1)
        grid_layout.addWidget(self.weights_button, 1, 2)


        self.detect_image_button = QPushButton('detect images')
        #self.detect_image_button.clicked.connect()

        self.detect_videos_button = QPushButton('detect videos')
        self.detect_camera_button = QPushButton('detect camera')

        vertical_layout.addWidget(self.detect_image_button)
        vertical_layout.addWidget(self.detect_videos_button)
        vertical_layout.addWidget(self.detect_camera_button)

        global_widget_layout.addLayout(grid_layout)
        global_widget_layout.addLayout(vertical_layout)

    def get_source_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Image File')
        self.source_line_edit.setText(filename)
        print('源文件路径：',filename)
    def get_weights_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Weights File')
        self.weights_line_edit.setText(filename)
        print('权重文件路径：',filename)
    def detect_image(self):
        pass
    def detect_videos(self):
        pass
    def detect_camera(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())