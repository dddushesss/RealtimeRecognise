import sys

import PyQt5
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QPoint, QDateTime
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QMainWindow, QApplication
from scipy.signal import find_peaks

from mainWindow import Ui_MainWindow


class App(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.ClearAction.triggered.connect(self.clear)
        self.writeToBaseButton.clicked.connect(self.writeToBase)

        self.brushSizeSlider.valueChanged.connect(self.setBrushSize)
        self.bordersButton.clicked.connect(self.drawBorders)
        self.setFixedSize(self.size())
        self.image = PyQt5.QtGui.QImage(self.size(), PyQt5.QtGui.QImage.Format_RGB32)
        self.ClearButton.clicked.connect(self.clear)
        self.image.fill(Qt.white)
        self.drawing = False
        self.brushSize = self.brushSizeSlider.value().real
        self.brushSizeLabel.setText("Размер кисти " + str(self.brushSize.real))
        self.brushColor = Qt.black
        self.lastPoint = QPoint()
        self.learnArray = []
        self.data = []

    def drawBorders(self):
        borders = []

        painter = PyQt5.QtGui.QPainter(self.image)
        painter.setPen(PyQt5.QtGui.QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        a = np.array(self.learnArray)
        met = a[:, int(self.metricTextEdit.toPlainText())]
        fig, ax = plt.subplots()

        plt1, = ax.plot(a[:, 6], label='По расстоянию')
        plt2, = ax.plot(a[:, 7], label='По времени')

        peaks, _ = find_peaks(met, height=int(self.borderTextEdit.toPlainText()))
        peaks1, _ = find_peaks(a[:, 6], height=int(self.borderTextEdit.toPlainText()))
        peaks2, _ = find_peaks(a[:, 7], height=int(self.borderTextEdit.toPlainText()))

        plt3, = ax.plot(peaks1, a[:, 6][peaks1], "x", label='Пики расстояний')
        plt4, = ax.plot(peaks2, a[:, 7][peaks2], "*", label='Пики времени')

        ax.legend(handles=[plt1, plt2, plt3, plt4])
        plt.grid(True)
        plt.show()
        if len(peaks) > 0:
            res = self.learnArray[0:peaks[0]]
            self.bordersAdd(borders, res)
            for i in range(0, len(peaks) - 1):
                res = self.learnArray[peaks[i]:peaks[i + 1]]
                self.bordersAdd(borders, res)

            res = self.learnArray[peaks[len(peaks) - 1]:len(self.learnArray) - 1]
            self.bordersAdd(borders, res)
        else:
            self.bordersAdd(borders, self.learnArray)

        print("**********")
        for j in range(0, len(borders)):
            painter.drawRect(int(borders[j][1]), int(borders[j][2]), int(borders[j][3]), int(borders[j][4]))
            print(borders[j][1], borders[j][2], borders[j][3], borders[j][4], sep=" ")
            b = np.array(borders[j][0])
            b[:, 4] = b[:, 4] - borders[j][1]
            b[:, 5] = b[:, 5] - borders[j][2]
            self.data.append([self.charTextEdit.toPlainText(), b[:, 4], b[:, 5], b[:, 6], b[:, 7]])

        self.update()

    def bordersAdd(self, borders: list, res: list):
        borders.append([res, min(res, key=lambda e: e[4])[4],
                        min(res, key=lambda e: e[5])[5],
                        max(res, key=lambda e: e[4])[4] - min(res, key=lambda e: e[4])[4],
                        max(res, key=lambda e: e[5])[5] - min(res, key=lambda e: e[5])[5]])

    def resizeImage(self):
        self.image.rect().setSize(self.size())

    def setBrushSize(self):
        self.brushSize = self.brushSizeSlider.value().real
        self.brushSizeLabel.setText("Размер кисти " + str(self.brushSize.real))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.pos()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.LeftButton) & self.drawing:
            painter = PyQt5.QtGui.QPainter(self.image)
            painter.setPen(PyQt5.QtGui.QPen(self.brushColor, self.brushSize, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.pos())
            self.lastPoint = event.pos()

            self.writeArray()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        canvasPainter = QPainter(self)
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())

    def tabletEvent(self, event: QtGui.QTabletEvent) -> None:
        if event.type() == event.TabletPress and not self.drawing:
            self.lastPoint = event.posF()
            self.drawing = True
        elif event.type() == event.TabletRelease:
            self.drawing = False

        if event.type() == event.TabletMove and self.drawing:
            painter = PyQt5.QtGui.QPainter(self.image)
            painter.setPen(
                PyQt5.QtGui.QPen(self.brushColor, event.pressure().real * 7., Qt.SolidLine, Qt.RoundCap,
                                 Qt.RoundJoin))
            painter.drawLine(self.lastPoint, event.posF())
            self.lastPoint = event.posF()
            self.writeArray()
            self.update()

    def writeArray(self):
        if len(self.learnArray) < 1:
            self.learnArray.append(
                [QDateTime.currentDateTime().time().hour(), QDateTime.currentDateTime().time().minute(),
                 QDateTime.currentDateTime().time().second(), QDateTime.currentDateTime().time().msec(),
                 self.lastPoint.x().real,
                 self.lastPoint.y().real,
                 0., 0.])
        else:
            t = self.learnArray[len(self.learnArray) - 1][0] * 10000000 + self.learnArray[len(self.learnArray) - 1][
                1] * 100000 + self.learnArray[len(self.learnArray) - 1][
                    2] * 1000 + self.learnArray[len(self.learnArray) - 1][3]
            time = QDateTime.currentDateTime().time()
            t1 = time.hour() * 10000000 + time.minute() * 100000 + time.second() * 1000 + time.msec()
            x = self.learnArray[len(self.learnArray) - 1][4]
            y = self.learnArray[len(self.learnArray) - 1][5]
            self.learnArray.append(
                [QDateTime.currentDateTime().time().hour(), QDateTime.currentDateTime().time().minute(),
                 QDateTime.currentDateTime().time().second(), QDateTime.currentDateTime().time().msec(),
                 self.lastPoint.x().real,
                 self.lastPoint.y().real,
                 ((self.lastPoint.x() - x) ** 2 + (self.lastPoint.y() - y) ** 2) ** 0.5, t1 - t])

    def writeToBase(self):
        # df = pd.DataFrame(self.learnArray)
        # df.to_csv('Data/data.csv', index=False, header=False)
        file = pd.DataFrame(self.data, columns=['Char', 'x', 'y', 'distance', 'time'])
        file.to_csv('Data/data.csv', mode='a', index=False, header=False,
                    columns=['Char', 'x', 'y', 'distance', 'time'])
        # self.data.tofile(f'Data/{self.charTextEdit.toPlainText()}')

    def clear(self):
        self.image.fill(Qt.white)
        self.learnArray = []
        self.data = []
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Application = App()
    Application.show()
    sys.exit(app.exec_())
