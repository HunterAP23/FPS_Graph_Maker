from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys

# class GUI_PyQt:
#     def __init__():
#         app = QApplication(sys.argv)
#         win = QMainWindow()
#         win.setGeometry(400, 400, 300, 300)
#         win.setWindowTitle("GameBench Graph Maker")
#         return
#
#     def show():
#         print(line.text())
#
#     def create_button(window, text, x, y):
#         button = QtWidgets.QPushButton(window)
#         button.setText(str(text))
#         button.move(int(x), int(y))
#         return button

from PyQt5 import QtWidgets, uic
import sys

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("test.ui", self)
        self.show()

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
