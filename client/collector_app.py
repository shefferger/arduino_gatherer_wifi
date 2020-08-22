from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem
import appform
import threading
import requests
import pandas as pd
import time
import datetime
import matplotlib as plt
from drawnow import *


class application(QtWidgets.QMainWindow, appform.Ui_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.send)
        self.stat = False
        self.df = pd.DataFrame()
        self.counter = 0
        self.x = []
        self.d1 = []
        self.d2 = []
        self.thread = threading.Thread(target=self.recieve)


    def makeFig(self):  # Create a function that makes our desired plot
        plt.ylim(90, 1024)  # Set y min and max values
        plt.title('')  # Plot the title
        plt.grid(True)  # Turn the grid on
        plt.ylabel('p1')  # Set ylabels
        plt.plot(self.d1, 'ro-', label='Potentiometr_1')
        plt.legend(loc='upper left')  # plot the legend
        plt2 = plt.twinx()  # Create a second y axis
        plt.ylim(90, 1024)  # Set limits of second y axis- adjust to readings you are getting
        plt2.plot(self.d2, 'b^-', label='Potentiometr_2')
        plt2.set_ylabel('p2')  # label second y axis
        plt2.ticklabel_format(useOffset=False)  # Force matplotlib to NOT autoscale y axis
        plt2.legend(loc='upper right')  # plot the legend

    def recieve(self):
        plt.ion()
        while 1:
            if self.stat:
                addr = self.lineEdit.text()
                port = self.lineEdit_2.text()
                response = requests.get('http://' + addr + ':' + port + '/get_data')
                if response.status_code == 200:
                    self.df = pd.DataFrame.from_dict(response.json())
                    self.label_3.setText('Подключенных устройств: ' + str(len(self.df.index)))
                    print('\n')
                    print(str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
                    print(self.df)
                    if self.tableWidget.rowCount() < self.df.shape[0]:
                        self.tableWidget.setRowCount(self.df.shape[0])
                    for i in range(0, self.df.shape[0]):
                        for i2 in range(0, 4):
                            self.tableWidget.setItem(i, i2, QTableWidgetItem(str(self.df.iloc[i, i2])))
                    self.tableWidget.reset()
                    self.textBrowser_2.append(str(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')) + '\n' +
                                              self.df.to_string() + '\n')

                    self.d1.append(int(self.df.iloc[0][3]))
                    self.d2.append(int(self.df.iloc[1][3]))
                    drawnow(self.makeFig, stop_on_close=True)
                    plt.pause(.000001)
                    self.counter += 1
                    if self.counter > 50:
                        self.d1.pop(0)
                        self.d2.pop(0)
            else:
                return 0
            time.sleep(0.4)

    def send(self):
        if not self.thread.is_alive():
            self.thread = threading.Thread(target=self.recieve)
        if not self.stat:
            addr = self.lineEdit.text()
            port = self.lineEdit_2.text()
            try:
                response = requests.get('http://' + addr + ':' + port + '/get_data')
                print(response.status_code)
                if response.status_code == 200:
                    self.label.setText('Статус сервера: подключен')
                    self.df = pd.DataFrame.from_dict(response.json())
                    print(self.df)
                    self.label_3.setText('Подключенных устройств: ' + str(len(self.df.index)))
                    self.stat = True
                    self.thread.start()
                self.lineEdit.setEnabled(False)
                self.lineEdit_2.setEnabled(False)
                self.pushButton.setText('Отключиться')
            except:
                self.stat = False
                self.lineEdit.setEnabled(True)
                self.lineEdit_2.setEnabled(True)
                self.pushButton.setText('Подключиться')
                self.label.setText('Статус сервера: ошибка')
                self.label_3.setText('Подключенных устройств: 0')
                print('smthng went wrong')
        else:
            self.stat = False
            self.lineEdit.setEnabled(True)
            self.lineEdit_2.setEnabled(True)
            self.pushButton.setText('Подключиться')
            self.label.setText('Статус сервера: отключен')
            self.label_3.setText('Подключенных устройств: 0')


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = application()
    window.show()
    app.exec_()
