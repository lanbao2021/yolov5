import time
import threading
from tqdm import tqdm
from PyQt5 import QtCore, QtGui, QtWidgets
import lorem

class LogTextEdit(QtWidgets.QPlainTextEdit):
    def write(self, message):
        if not hasattr(self, "flag"):
            self.flag = False
        message = message.replace('\r', '').rstrip()
        if message:
            method = "replace_last_line" if self.flag else "appendPlainText"
            QtCore.QMetaObject.invokeMethod(self,
                method,
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, message))
            self.flag = True
        else:
            self.flag = False

    @QtCore.pyqtSlot(str)
    def replace_last_line(self, text):
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.select(QtGui.QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.insertBlock()
        self.setTextCursor(cursor)
        self.insertPlainText(text)

def foo(w):
    for i in tqdm(range(100), file=w):
        time.sleep(0.1)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = LogTextEdit(readOnly=True)
    w.appendPlainText(lorem.paragraph())
    w.appendHtml("Welcome to Stack Overflow")
    w.show()
    threading.Thread(target=foo, args=(w,), daemon=True).start()
    sys.exit(app.exec_())