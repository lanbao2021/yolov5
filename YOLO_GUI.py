# -*- coding:utf-8 -*-
import json
import atexit
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import detect
import sys
import os

CONFIG = dict()


def init_config():
    global CONFIG
    if not os.path.exists('config'):
        os.mkdir('config')
        return
    try:
        with open('config/config.json', 'r', encoding='utf-8') as config_file:
            CONFIG = json.load(config_file)
            print('已打开上次保存的配置')
    except FileNotFoundError as error:
        print('配置文件不存在 ', str(error))


def save_config():
    global CONFIG
    if not os.path.exists('config'):
        os.mkdir('config')
    with open('config/config.json', 'w', encoding='utf-8') as config_file:
        config_file.write(json.dumps(CONFIG, ensure_ascii=False))
    print('配置文件已保存')



class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('YOLOv5_GUI_1.0')
        self.resize(256, 200)

        init_config()
        atexit.register(self.open_failed)

        global_widget = QWidget(self)
        global_widget_layout = QVBoxLayout(global_widget)

        grid_layout = QGridLayout()
        vertical_layout = QVBoxLayout()

        self.source_button = QPushButton('...')
        self.source_button.clicked.connect(self.get_source_file)
        self.source_line_edit = QLineEdit()
        if CONFIG.get('source_file'):
            self.source_line_edit.setText(CONFIG['source_file'])

        self.weights_button = QPushButton('...')
        self.weights_button.clicked.connect(self.get_weights_file)
        self.weights_line_edit = QLineEdit()
        if CONFIG.get('weights_file'):
            self.weights_line_edit.setText(CONFIG['weights_file'])


        grid_layout.addWidget(QLabel('Source'), 0, 0)
        grid_layout.addWidget(self.source_line_edit, 0, 1)
        grid_layout.addWidget(self.source_button, 0, 2)
        grid_layout.addWidget(QLabel('Weights'), 1, 0)
        grid_layout.addWidget(self.weights_line_edit, 1, 1)
        grid_layout.addWidget(self.weights_button, 1, 2)

        self.detect_image_button = QPushButton('detect images')
        self.detect_image_button.clicked.connect(self.detect_image)

        self.detect_videos_button = QPushButton('detect videos')
        self.detect_videos_button.clicked.connect(self.detect_videos)

        self.detect_camera_button = QPushButton('detect camera')
        self.detect_camera_button.clicked.connect(self.detect_camera)

        vertical_layout.addWidget(self.detect_image_button)
        vertical_layout.addWidget(self.detect_videos_button)
        vertical_layout.addWidget(self.detect_camera_button)

        global_widget_layout.addLayout(grid_layout)
        global_widget_layout.addLayout(vertical_layout)

    def open_failed(self):
        try:
            print('无法在析构函数里正常使用open')
        finally:
            save_config()

    def get_source_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Image File')
        self.source_line_edit.setText(filename)
        CONFIG['source_file'] = self.source_line_edit.text()
        print('源文件路径：',filename)

    def get_weights_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Weights File')
        self.weights_line_edit.setText(filename)
        CONFIG['weights_file'] = self.weights_line_edit.text()
        print('权重文件路径：', filename)

    def detect_image(self):
        source_filename = self.source_line_edit.text()
        weights_filename = self.weights_line_edit.text()
        if source_filename == '' or weights_filename == '':
            print('未设置源文件或权重文件路径！')
            return None
        save_dir = detect.run(weights=weights_filename, source=source_filename)
        print('结果保存路径：', save_dir)

        self.child_window = Child(save_dir)
        self.child_window.show()

    def detect_videos(self, filepath):
        thread = VideoThread()
        thread.run(self.weights_line_edit.text(), self.source_line_edit.text())

    def detect_camera(self):
        thread = CameraThread()
        print(self.weights_line_edit.text())
        thread.run(self.weights_line_edit.text())


class Child(QWidget):
    def __init__(self, filepath=''):
        super().__init__()
        self.setWindowTitle("图片检测结果浏览器")
        self.filepath = filepath
        print('屏幕宽度：', QApplication.desktop().width()) # 1440
        print('屏幕高度', QApplication.desktop().height()) # 900
        self.setFixedSize(1440*0.9, 900*0.9)
        self.move((QApplication.desktop().width() - self.width())/2, (QApplication.desktop().height() - self.height())/2)

        self.image_label = QLabel()
        print('label的宽：', self.image_label.width())
        print('label的高：', self.image_label.height())

        for i, j, self.images in os.walk(self.filepath):
            print(i, j, self.images)
        self.image_num = len(self.images)
        self.pos = 0;

        img = QImage(str(self.filepath) + '/' + self.images[self.pos])
        result = img.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(QPixmap.fromImage(result))
        self.image_label.setAlignment(Qt.AlignCenter)


        self.previous_button = QPushButton('上一张')
        self.previous_button.clicked.connect(self.previous_image)
        self.next_button = QPushButton('下一张')
        self.next_button.clicked.connect(self.next_image)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.image_label)
        vertical_layout.addWidget(self.previous_button)
        vertical_layout.addWidget(self.next_button)

        self.setLayout(vertical_layout)

    def previous_image(self):
        if self.pos == 0:
            return
        if self.pos > 0:
            self.pos -= 1
            img = QImage(str(self.filepath) + '/' + self.images[self.pos])
            result = img.scaled(self.image_label.width(), self.image_label.height(),
                                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(QPixmap.fromImage(result))

    def next_image(self):
        if self.pos == self.image_num-1:
            return
        if self.pos < self.image_num-1:
            self.pos += 1
            img = QImage(str(self.filepath) + '/' + self.images[self.pos])
            result = img.scaled(self.image_label.width(), self.image_label.height(),
                                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(QPixmap.fromImage(result))


class CameraThread(QThread):
    def __init__(self):
        super(CameraThread, self).__init__()

    def run(self, weights_filename):
        detect.run(weights=weights_filename, source=0)


class VideoThread(QThread):
    def __init__(self):
        super(VideoThread, self).__init__()

    def run(self, weights_filename, source_filename):
        try:
            detect.run(weights=weights_filename, source=source_filename, view_img=True) # 实时检测视频需要view-img打开
        finally:
            print('摄像头关闭！')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())