#!/usr/bin/python

"""
author: lanfucai
time: 2022.01.29
"""

import logging
import os
import json
import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSignal, QEventLoop, QTimer, QThread
from PyQt5.QtGui import QTextCursor

import detect
import train
import atexit
from PyQt5.QtWidgets import (QWidget, QFileDialog, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton,
                             QTextEdit, QGridLayout, QApplication)

import train

CONFIG = {
    'source': '',
    'weight': '',
    'run_model': 'detect',  # detection or training
    'detect_config_type': 'images',
    'detect_config_size': 640,
    'detect_config_device': 'cpu',
    'train_config_data': '',
    'train_config_yaml': '',
    'train_config_epoch': 100,
    'train_config_batch_size': 4,
    'train_config_device': 'cpu'
}

temp = sys.stdout
temp_err = sys.stderr


def save_config():
    global CONFIG
    if not os.path.exists('config'):
        os.mkdir('config')
    with open('config/config.json', 'w', encoding='utf-8') as config_file:
        config_file.write(json.dumps(CONFIG, ensure_ascii=False))
    print('配置文件已保存')


def save_config_exit():
    global CONFIG
    global temp
    sys.stdout = temp
    if not os.path.exists('config'):
        os.mkdir('config')
    with open('config/config.json', 'w', encoding='utf-8') as config_file:
        config_file.write(json.dumps(CONFIG, ensure_ascii=False))
    print('配置文件已保存')


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


class Signal(QObject):
    text_update = pyqtSignal(str)

    def write(self, text):
        self.text_update.emit(str(text))

    def flush(self):
        pass


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__()
        init_config()
        atexit.register(save_config_exit)
        self.initUI(parent)

        sys.stdout = Signal()
        sys.stdout.text_update.connect(self.update_text)

    def update_text(self, text):
        cursor = self.logTextBox.widget.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.logTextBox.widget.appendPlainText(text)
        self.logTextBox.widget.setTextCursor(cursor)
        self.logTextBox.widget.ensureCursorVisible()

    def initUI(self, parent):
        grid = QGridLayout()
        grid.setSpacing(30)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 0)

        source = QLabel('Source')
        self.source_input = QLineEdit()
        self.source_input.setText(CONFIG['source'])
        self.source_input.setFixedHeight(30)
        source_button = QPushButton('...')
        source_button.clicked.connect(self.get_source_file)
        grid.addWidget(source, 1, 0)
        grid.addWidget(self.source_input, 1, 1, 1, 2)
        grid.addWidget(source_button, 1, 3)

        weight = QLabel('Weight')
        self.weight_input = QLineEdit()
        self.weight_input.setText(CONFIG['weight'])
        self.weight_input.setFixedHeight(30)
        weight_button = QPushButton('...')
        weight_button.clicked.connect(self.get_weight_file)
        grid.addWidget(weight, 2, 0)
        grid.addWidget(self.weight_input, 2, 1, 1, 2)
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
        start_button.clicked.connect(self.start)
        start_button.setFixedHeight(40)
        grid.addWidget(config_button, 4, 1)
        grid.addWidget(start_button, 4, 2)


        output = QLabel('Output')
        grid.addWidget(output, 5, 0)

        self.logTextBox = QTextEditLogger(self)
        self.logTextBox.setFormatter(logging.Formatter('%(message)s'))
        logging.getLogger().addHandler(self.logTextBox)
        logging.getLogger().setLevel(logging.INFO)

        grid.addWidget(self.logTextBox.widget, 5, 1, 5, 3)

        self.setLayout(grid)

        self.setGeometry(300, 300, 950, 700)
        self.setWindowTitle('YOLOv5_GUI')

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)

    def update_detect_radio(self):
        CONFIG['run_model'] = 'detect'

    def update_train_radio(self):
        CONFIG['run_model'] = 'train'

    def config(self):
        if CONFIG['run_model'] == 'detect':
            self.w = ConfigDetection()
            self.w.show()
            return None
        if CONFIG['run_model'] == 'train':
            self.w = ConfigTraining()
            self.w.show()
            return None

    def start(self):
        if CONFIG['run_model'] == 'detect':
            if CONFIG['detect_config_type'] == 'image':
                self.detect_images()
                return None
            if CONFIG['detect_config_type'] == 'images':
                self.detect_images()
                return None
            if CONFIG['detect_config_type'] == 'video':
                self.detect_images()
                return None
            if CONFIG['detect_config_type'] == 'camera':
                self.detect_camera()
                return None
        else:
            self.train_model()
            return None

    def train_model(self):
        thread = TrainingThread(self.logTextBox)
        thread.start()
        # train.run(weights=CONFIG['weight'],
        #           cfg=CONFIG['train_config_yaml'],
        #           data=CONFIG['train_config_data'],
        #           epoch=CONFIG['train_config_epoch'],
        #           batch_size=CONFIG['train_config_batch_size'],
        #           device=CONFIG['train_config_device']
        #           )
        QApplication.processEvents()
        return None

    def get_source_file(self):
        # QFileDialog.getExistingDirectory()
        if CONFIG['detect_config_type'] == 'image':
            filename, _ = QFileDialog.getOpenFileName(self, "Open Image File")
            self.source_input.setText(filename)
            CONFIG['source'] = filename
            print('待检测文件路径：', filename)
        else:
            filename = QFileDialog.getExistingDirectory(self, "Open Image Directory")
            self.source_input.setText(filename)
            CONFIG['source'] = filename
            print('待检测文件夹路径：', filename)

    def get_weight_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Open Weights File')
        self.weight_input.setText(filename)
        CONFIG['weight'] = filename
        print('权重文件路径：', filename)

    def detect_images(self):
        source = CONFIG['source']
        weight = CONFIG['weight']
        if source == '' or weight == '':
            print('未设置待检测文件或权重文件路径！')
            return None
        save_dir = detect.run(weights=weight, source=source)
        print('检测结果保存路径：', save_dir)

    def detect_camera(self):
        weight = CONFIG['weight']
        if weight == '':
            print('未设置权重文件路径！')
            return None
        detect.run(weights=weight, source=0)


class TrainingThread(QThread):
    def __init__(self, output):
        super(TrainingThread, self).__init__()

    def run(self):
        train.run(weights=CONFIG['weight'],
                  cfg=CONFIG['train_config_yaml'],
                  data=CONFIG['train_config_data'],
                  epoch=CONFIG['train_config_epoch'],
                  batch_size=CONFIG['train_config_batch_size'],
                  device=CONFIG['train_config_device']
                  )


class ConfigDetection(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

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
        size1.setChecked(CONFIG['detect_config_size'] == 640)
        size1.clicked.connect(self.update_image_size1)
        size2 = QRadioButton('320')
        size2.setChecked(CONFIG['detect_config_size'] == 320)
        size2.clicked.connect(self.update_image_size2)
        size3 = QRadioButton('240')
        size3.setChecked(CONFIG['detect_config_size'] == 240)
        size3.clicked.connect(self.update_image_size3)
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
        device1.setChecked(CONFIG['detect_config_device'] == 'cpu')
        device1.clicked.connect(self.update_device1)
        device2 = QRadioButton('GPU')
        device2.setChecked(CONFIG['detect_config_device'] == 'gpu')
        device2.clicked.connect(self.update_device2)
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
        ok.clicked.connect(self.ok)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.cancel)
        cancel.setFixedHeight(50)
        grid.addWidget(ok, 4, 1, 1, 2)
        grid.addWidget(cancel, 4, 3, 1, 2)

        self.setLayout(grid)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Configure Detection')

    def ok(self):
        self.save_config()
        self.close()

    def cancel(self):
        self.close()

    def save_config(self):
        global CONFIG
        if not os.path.exists('config'):
            os.mkdir('config')
        with open('config/config.json', 'w', encoding='utf-8') as config_file:
            config_file.write(json.dumps(CONFIG, ensure_ascii=False))
        print('配置文件已保存')

    def update_type_image(self):
        CONFIG['detect_config_type'] = 'image'

    def update_type_images(self):
        CONFIG['detect_config_type'] = 'images'

    def update_type_video(self):
        CONFIG['detect_config_type'] = 'video'

    def update_type_camera(self):
        CONFIG['detect_config_type'] = 'camera'

    def update_image_size1(self):
        CONFIG['detect_config_size'] = 640

    def update_image_size2(self):
        CONFIG['detect_config_size'] = 320

    def update_image_size3(self):
        CONFIG['detect_config_size'] = 240

    def update_device1(self):
        CONFIG['detect_config_device'] = 'cpu'

    def update_device2(self):
        CONFIG['detect_config_device'] = 'gpu'


class ConfigTraining(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def update_config_eopch1(self):
        CONFIG['train_config_epoch'] == 100
        return None

    def update_config_eopch2(self):
        CONFIG['train_config_epoch'] == 200
        return None

    def update_config_eopch3(self):
        CONFIG['train_config_epoch'] == 300
        return None

    def update_config_eopch4(self):
        CONFIG['train_config_epoch'] == 400
        return None

    def update_config_batch_size1(self):
        CONFIG['train_config_batch_size'] = 4
        return None

    def update_config_batch_size2(self):
        CONFIG['train_config_batch_size'] = 8
        return None

    def update_config_batch_size3(self):
        CONFIG['train_config_batch_size'] = 16
        return None

    def update_config_batch_size4(self):
        CONFIG['train_config_batch_size'] = 32
        return None

    def update_config_device1(self):
        CONFIG['train_config_device'] = 'cpu'
        return None

    def update_config_device2(self):
        CONFIG['train_config_device'] = 'gpu'
        return None

    def update_config_device3(self):
        CONFIG['train_config_device'] = 'gpus'
        return None

    def get_yaml_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open YAML File")
        self.yaml_input.setText(filename)
        CONFIG['train_config_yaml'] = filename
        print('YAML配置文件路径：', filename)

    def get_data_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Data File")
        self.data_input.setText(filename)
        CONFIG['train_config_data'] = filename
        print('Data文件路径：', filename)
        return None

    def initUI(self):
        grid = QGridLayout()
        grid.setSpacing(30)
        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(4, 1)
        # grid.setColumnStretch(5, 1)

        data = QLabel('Data')
        self.data_input = QLineEdit()
        self.data_input.setText(CONFIG['train_config_data'])
        self.data_input.setFixedHeight(30)
        data_button = QPushButton('...')
        data_button.setFixedHeight(30)
        data_button.setMaximumWidth(50)
        CONFIG['detect_config_type'] = 'images'
        data_button.clicked.connect(self.get_data_file)
        grid.addWidget(data, 0, 0)
        grid.addWidget(self.data_input, 0, 1, 1, 3)
        grid.addWidget(data_button, 0, 4)

        yaml = QLabel('YAML')
        self.yaml_input = QLineEdit()
        self.yaml_input.setText(CONFIG['train_config_yaml'])
        self.yaml_input.setFixedHeight(30)
        yaml_button = QPushButton('...')
        yaml_button.setFixedHeight(30)
        yaml_button.setMaximumWidth(50)
        CONFIG['detect_config_type'] = 'images'
        yaml_button.clicked.connect(self.get_yaml_file)
        grid.addWidget(yaml, 1, 0)
        grid.addWidget(self.yaml_input, 1, 1, 1, 3)
        grid.addWidget(yaml_button, 1, 4)



        epoch = QLabel('Epoch')
        epoch1 = QRadioButton('100')
        epoch1.setChecked(CONFIG['train_config_epoch'] == 100)
        epoch1.clicked.connect(self.update_config_eopch1)

        epoch2 = QRadioButton('200')
        epoch2.setChecked(CONFIG['train_config_epoch'] == 200)
        epoch2.clicked.connect(self.update_config_eopch2)

        epoch3 = QRadioButton('300')
        epoch3.setChecked(CONFIG['train_config_epoch'] == 300)
        epoch3.clicked.connect(self.update_config_eopch3)

        epoch4 = QRadioButton('400')
        epoch4.setChecked(CONFIG['train_config_epoch'] == 400)
        epoch4.clicked.connect(self.update_config_eopch4)

        grid.addWidget(epoch, 2, 0)
        hlayout = QHBoxLayout()
        hlayout.addWidget(epoch1)
        hlayout.addWidget(epoch2)
        hlayout.addWidget(epoch3)
        hlayout.addWidget(epoch4)
        groupBox = QGroupBox()
        groupBox.setLayout(hlayout)
        groupBox.setFixedHeight(50)
        grid.addWidget(groupBox, 2, 1, 1, 4)

        batch_size = QLabel('Batch_Size')
        batch_size1 = QRadioButton('4')
        batch_size1.setChecked(CONFIG['train_config_batch_size'] == 4)
        batch_size1.clicked.connect(self.update_config_batch_size1)
        batch_size2 = QRadioButton('8')
        batch_size2.setChecked(CONFIG['train_config_batch_size'] == 8)
        batch_size2.clicked.connect(self.update_config_batch_size2)
        batch_size3 = QRadioButton('16')
        batch_size3.setChecked(CONFIG['train_config_batch_size'] == 16)
        batch_size3.clicked.connect(self.update_config_batch_size3)
        batch_size4 = QRadioButton('32')
        batch_size4.setChecked(CONFIG['train_config_batch_size'] == 32)
        batch_size4.clicked.connect(self.update_config_batch_size4)
        hlayout = QHBoxLayout()
        hlayout.addWidget(batch_size1)
        hlayout.addWidget(batch_size2)
        hlayout.addWidget(batch_size3)
        hlayout.addWidget(batch_size4)
        groupBox = QGroupBox()
        groupBox.setLayout(hlayout)
        groupBox.setFixedHeight(50)
        grid.addWidget(batch_size, 3, 0)
        grid.addWidget(groupBox, 3, 1, 1, 4)

        device = QLabel('Device')
        device1 = QRadioButton('CPU')
        device1.setChecked(CONFIG['train_config_device'] == 'cpu')
        device1.clicked.connect(self.update_config_device1)
        device2 = QRadioButton('GPU')
        device2.setChecked(CONFIG['train_config_device'] == 'gpu')
        device2.clicked.connect(self.update_config_device2)
        device3 = QRadioButton('GPUs')
        device3.setChecked(CONFIG['train_config_device'] == 'gpus')
        device3.clicked.connect(self.update_config_device3)
        hlayout = QHBoxLayout()
        hlayout.addWidget(device1)
        hlayout.addWidget(device2)
        hlayout.addWidget(device3)
        groupBox = QGroupBox()
        groupBox.setLayout(hlayout)
        groupBox.setFixedHeight(50)
        grid.addWidget(device, 4, 0)
        grid.addWidget(groupBox, 4, 1, 1, 4)

        ok = QPushButton('OK')
        ok.setFixedHeight(50)
        ok.clicked.connect(self.ok)
        cancel = QPushButton('Cancel')
        cancel.clicked.connect(self.cancel)
        cancel.setFixedHeight(50)
        grid.addWidget(ok, 5, 1, 1, 2)
        grid.addWidget(cancel, 5, 3, 1, 2)

        self.setLayout(grid)
        self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('Configure Training')

    def ok(self):
        save_config()
        self.close()

    def cancel(self):
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
