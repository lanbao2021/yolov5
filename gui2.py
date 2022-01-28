#!/usr/bin/python

"""
ZetCode PyQt5 tutorial

In this example, we create a bit
more complicated window layout using
the QGridLayout manager.

Author: Jan Bodnar
Website: zetcode.com
"""
import os
import json
import sys
import atexit
from PyQt5.QtWidgets import (QWidget, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton,
                             QTextEdit, QGridLayout, QApplication)

CONFIG = {
    'source': '',
    'weight': '',
    'run_model': 'detect',  # detection or training
    'detect_config_type': 'images',
    'detect_config_size': 640,
    'detect_config_device': 'cpu'
}


def init_config():
    global CONFIG
    if not os.path.exists('config'):
        os.mkdir('config')
        return
    try:
        with open('config/config.json', 'r', encoding='utf-8') as config_file:
            CONFIG = json.load(config_file)
            print('已加载上次保存的配置')
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
        init_config()
        atexit.register(save_config)
        self.initUI()

    def update_detect_radio(self):
        CONFIG['run_model'] = 'detect'

    def update_train_radio(self):
        CONFIG['run_model'] = 'train'


    def initUI(self):
        grid = QGridLayout()
        grid.setSpacing(30)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 0)

        source = QLabel('Source')
        source_input = QLineEdit()
        source_input.setText(CONFIG['source'])
        source_input.setFixedHeight(30)
        source_button = QPushButton('...')
        grid.addWidget(source, 1, 0)
        grid.addWidget(source_input, 1, 1, 1, 2)
        grid.addWidget(source_button, 1, 3)

        weight = QLabel('Weight')
        weight_input = QLineEdit()
        weight_input.setText(CONFIG['weight'])
        weight_input.setFixedHeight(30)
        weight_button = QPushButton('...')
        grid.addWidget(weight, 2, 0)
        grid.addWidget(weight_input, 2, 1, 1, 2)
        grid.addWidget(weight_button, 2, 3)

        model = QLabel('Model')
        detect_radio = QRadioButton('Detection')
        detect_radio.setChecked(CONFIG['run_model'] == 'detect')
        detect_radio.clicked.connect(self.update_detect_radio)
        train_radio = QRadioButton('Training')
        train_radio.setChecked(CONFIG['run_model'] == 'train')
        train_radio.clicked.connect(self.update_train_radio)
        hlayout = QHBoxLayout()
        hlayout.addWidget(detect_radio)
        hlayout.addWidget(train_radio)
        groupbox = QGroupBox()
        groupbox.setLayout(hlayout)
        grid.addWidget(model, 3, 0)
        grid.addWidget(groupbox, 3, 1)

        config_button = QPushButton('Config')
        config_button.setFixedHeight(40)
        config_button.clicked.connect(self.config)
        start_button = QPushButton('Start')
        start_button.setFixedHeight(40)
        grid.addWidget(config_button, 4, 1)
        grid.addWidget(start_button, 4, 2)


        output = QLabel('Output')
        output_text = QTextEdit()
        grid.addWidget(output, 5, 0)
        grid.addWidget(output_text, 5, 1, 5, 3)

        self.setLayout(grid)

        self.setGeometry(300, 300, 950, 700)
        self.setWindowTitle('YOLOv5_GUI')

    def config(self):
        self.w = ConfigDetection()
        self.w.show()


class ConfigDetection(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def update_type_image(self):
        CONFIG['detect_config_type'] = 'image'

    def update_type_images(self):
        CONFIG['detect_config_type'] = 'images'

    def update_type_video(self):
        CONFIG['detect_config_type'] = 'video'

    def update_type_camera(self):
        CONFIG['detect_config_type'] = 'camera'

    def initUI(self):
        grid = QGridLayout()

        type = QLabel('Type')
        type_image = QRadioButton('image')
        type_image.setChecked(CONFIG['detect_config_type'] == 'image')
        type_image.clicked.connect(self.update_type_image)

        type_images = QRadioButton('images')
        type_images.setChecked(CONFIG['detect_config_type'] == 'images')
        type_images.clicked.connect(self.update_type_images)

        type_video = QRadioButton('video')
        type_video.setChecked(CONFIG['detect_config_type'] == 'video')
        type_video.clicked.connect(self.update_type_video)

        type_camera = QRadioButton('camera')
        type_camera.setChecked(CONFIG['detect_config_type'] == 'camera')
        type_camera.clicked.connect(self.update_type_camera)

        grid.addWidget(type, 1, 0)
        hlayout = QHBoxLayout()
        hlayout.addWidget(type_image)
        hlayout.addWidget(type_images)
        hlayout.addWidget(type_video)
        hlayout.addWidget(type_camera)
        groupBox = QGroupBox()
        groupBox.setLayout(hlayout)
        groupBox.setFixedHeight(50)
        grid.addWidget(groupBox, 1, 1, 1, 4)

        image_size = QLabel('Size')
        size1 = QRadioButton('640')
        size1.setChecked(True)
        size2 = QRadioButton('320')
        size3 = QRadioButton('240')
        hlayout = QHBoxLayout()
        hlayout.addWidget(size1)
        hlayout.addWidget(size2)
        hlayout.addWidget(size3)
        groupBox = QGroupBox()
        groupBox.setLayout(hlayout)
        groupBox.setFixedHeight(50)
        grid.addWidget(image_size, 2, 0)
        grid.addWidget(groupBox, 2, 1, 1, 4)

        device = QLabel('Device')
        device1 = QRadioButton('CPU')
        device1.setChecked(True)
        device2 = QRadioButton('GPU')
        hlayout = QHBoxLayout()
        hlayout.addWidget(device1)
        hlayout.addWidget(device2)
        groupBox = QGroupBox()
        groupBox.setLayout(hlayout)
        groupBox.setFixedHeight(50)
        grid.addWidget(device, 3, 0)
        grid.addWidget(groupBox, 3, 1, 1, 2)

        ok = QPushButton('OK')
        ok.setFixedHeight(50)
        cancel = QPushButton('Cancel')
        cancel.setFixedHeight(50)
        grid.addWidget(ok, 4, 1, 1, 2)
        grid.addWidget(cancel, 4, 3, 1, 2)

        self.setLayout(grid)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Configure Detection')




class ConfigTraining(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
