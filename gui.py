# imports
import base64
import binascii
import os
from PyQt6.QtWidgets import * 
from PyQt6.QtGui import * 
from PyQt6.QtCore import *
import qdarktheme
import subprocess
import sys

class DemoWindow(QMainWindow):

    def __init__(self):

        # login to ttn
        os.system("..\\ttn-lw-cli\\ttn-lw-cli.exe login")

        # basic init stuff
        super().__init__()
        self.setWindowTitle("CS 402 Group 30 Demo GUI")
        self.setWindowState(Qt.WindowState.WindowMaximized)
        self.setStyleSheet(qdarktheme.load_stylesheet("dark"))

        # configure main layout
        self.main_layout = QVBoxLayout()

        # status bar
        self.status = QStatusBar()
        self.status.setStyleSheet("background-color: cornflowerblue")
        self.status_msg = QLabel("Waiting for User Input ...")
        self.status_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.addWidget(self.status_msg, Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.status)

        # layout and widget for uplink/downlink boxes
        self.link_widget = QWidget()
        self.link_layout = QHBoxLayout()

        # box and button for downlink send
        self.down_widget = QWidget()
        self.down_layout = QVBoxLayout()
        self.down_box = QTextEdit()
        self.downbtn_widget = QWidget()
        self.downbtn_layout = QHBoxLayout()
        self.down_button = QPushButton("Send Downlink to End-Device")
        self.down_button.setStyleSheet("background-color: cornflowerblue; color: white")
        self.down_button.clicked.connect(lambda: self.sendDownlink())
        self.down_refresh = QPushButton("Refresh")
        self.down_refresh.setStyleSheet("background-color: cornflowerblue; color: white")
        self.down_refresh.clicked.connect(lambda: self.refreshDownlink())
        self.downbtn_layout.addWidget(self.down_button, 1)
        self.downbtn_layout.addWidget(self.down_refresh, 1)
        self.downbtn_widget.setLayout(self.downbtn_layout)
        self.down_layout.addWidget(self.down_box, 1)
        self.down_layout.addWidget(self.downbtn_widget)
        self.down_widget.setLayout(self.down_layout)
        self.link_layout.addWidget(self.down_widget)

        # set link widget's layout
        self.link_widget.setLayout(self.link_layout)
        self.main_layout.addWidget(self.link_widget, 1)

        # configure main widget here
        self.gui_widget = QWidget()
        self.gui_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.gui_widget)
    
    def sendDownlink(self):

        # get message text and encode
        hex = binascii.hexlify(bytes(self.down_box.toPlainText(), encoding="utf-8"))
        hex = hex.decode()
        os.system("..\\ttn-lw-cli\\ttn-lw-cli.exe end-devices downlink push cs402-group30 cosc402-eui-ac1f09fffe083205 --f-port 3 --frm-payload " + hex)
        
        # update status bar
        self.status.setStyleSheet("background-color: darkolivegreen")
        self.status_msg.setText("Successfully Sent Downlink to End Device")

    def refreshDownlink(self):
        
        # clear text box
        self.down_box.setText("")

        # reset status bar
        self.status.setStyleSheet("background-color: cornflowerblue")
        self.status_msg.setText("Waiting for User Input ...")

if __name__ == "__main__":

    app = QApplication(sys.argv)
    fd = open("uplinks.txt", "w")
    fd.close()
    # subprocess.Popen("..\\ttn-lw-cli\\ttn-lw-cli.exe applications subscribe cs402-group30 > uplinks.txt", shell=True, stdin=None, stdout=None, stderr=None, close_fds=True)
    window = DemoWindow()
    window.show()
    sys.exit(app.exec())