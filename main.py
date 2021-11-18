import sys

import PyQt5
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QPoint, QDateTime
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QMainWindow, QApplication
from mainWindow import Ui_MainWindow
import numpy as np
import pandas as pd


class App(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.ClearAction.triggered.connect(self.clear)
        self.writeToBaseButton.clicked.connect(self.writeToBase)
        self.brushSizeSlider.valueChanged.connect(self.setBrushSize)
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
        self.learnArray.append([QDateTime.currentDateTime().time().hour(), QDateTime.currentDateTime().time().minute(),
                                QDateTime.currentDateTime().time().second(), QDateTime.currentDateTime().time().msec(),
                                self.lastPoint.x().real,
                                self.lastPoint.y().real])

    def writeToBase(self):
        df = pd.DataFrame(self.learnArray)
        df.to_csv('data.csv', index=False, header=False)
        np.save("Data/" + self.fileNameTextEdit.toPlainText(), self.learnArray)

    def clear(self):
        self.image.fill(Qt.white)
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    Application = App()
    Application.show()
    sys.exit(app.exec_())
