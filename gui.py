from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QLineEdit,
    QLabel,
)
from PyQt5 import QtSvg, QtCore
from PyQt5.QtGui import QPixmap
from lowpoly import *

'''
Author: Peiyi Hou
This file contains all gui components
'''

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.mode = "Delaunay"
        self.image = "wave.png"
        self.cull_pts = 2
        self.cull_sbl = 100
        self.dist = 10
        self.skew = 0
        self.frame = 0
        self.boundry = 0
        self.grey_weighted = 0

        self.setWindowTitle("Flat Style SVG Generator")
        self.setGeometry(50, 50, 400, 500)
        self.home()

    # open image file and set it as input for process
    # set preview of this image
    def file_open(self):
        name = QFileDialog.getOpenFileName(self, 'Open File')
        self.image = name[0]
        self.pic.setPixmap(QPixmap(self.image))
        self.pic.show()
        print(self.image)

    def set_mode(self, text):
        self.mode = text
        print(self.mode)

    def set_frame(self, state):
        if state == QtCore.Qt.Checked:
            self.frame = 1
        else :
            self.frame = 0

    def set_boundry(self, state):
        if state == QtCore.Qt.Checked:
            self.boundry = 1
        else :
            self.boundry = 0

    def set_grey_weight(self, state):
        if state == QtCore.Qt.Checked:
            self.grey_weighted = 1
        else :
            self.grey_weighted = 0

    # action function for button convert when clicked
    # gathers all parameters on MainWindow
    # call corresponding function to produce svg
    # if successfully prodeced svg, preview it
    def convert(self):
        self.cull_pts = int(self.cull_pts_perct_edit.text())
        self.cull_sbl = int(self.cull_sbl_perct_edit.text())
        self.dist = int(self.dist_edit.text())
        self.skew = int(self.skew_edit.text())
        converted = None
        if self.image == None:
            print("No image Selected")
            return
        if self.mode == "Delaunay":
            converted = draw_dealunay(self.image, cull_pts_perct=self.cull_pts, \
                            cull_sbl_perct=self.cull_sbl, frame=self.frame, \
                            boundry=self.boundry, grey_weighted=self.grey_weighted)
        elif self.mode == "Voronoi":
            converted = draw_voronoi(self.image, cull_pts_perct=self.cull_pts, \
                            cull_sbl_perct=self.cull_sbl, frame=self.frame, \
                            boundry=self.boundry, grey_weighted=self.grey_weighted)
        elif self.mode == "Tri-Grid":
            converted = draw_grid(self.image, dist=self.dist, sides=3, \
                                skew_dist=self.skew, boundry=self.boundry)
        elif self.mode == "Square-Grid":
            converted = draw_grid(self.image, dist=self.dist, sides=4, \
                                skew_dist=self.skew, boundry=self.boundry)
        elif self.mode == "Voronoi-Grid":
            converted = draw_grid(self.image, dist=self.dist, sides=4, \
                                skew_dist=self.skew, boundry=self.boundry, voronoi=1)
        elif self.mode == "Ortho-Tree":
            converted = draw_tree(self.image, dist=self.dist, skew_dist=self.skew, \
                                cull_pts_perct=self.cull_pts, \
                                cull_sbl_perct=self.cull_sbl, \
                                random=0, grey_weighted=0)
        elif self.mode == "Random-Tree":
            converted = draw_tree(self.image, dist=self.dist, skew_dist=self.skew, \
                                cull_pts_perct=self.cull_pts, \
                                cull_sbl_perct=self.cull_sbl, \
                                random=1, grey_weighted=self.grey_weighted)
        else:
            print("Mode Error")
            return
        if converted:
            self.picy = 600
            self.picx = self.picy * cv2.imread(self.image).shape[1]/cv2.imread(self.image).shape[0]
            self.svgWidget = QtSvg.QSvgWidget(converted)
            self.svgWidget.setGeometry(450,50,self.picx,self.picy)
            self.svgWidget.show()

    # all widgets on MainWindow
    def home(self):
        btno = QPushButton('Open', self)
        btno.clicked.connect(self.file_open)
        btno.resize(btno.sizeHint())
        btno.move(100, 410)

        btnc = QPushButton('Convert', self)
        btnc.clicked.connect(self.convert)
        btnc.resize(btnc.sizeHint())
        btnc.move(200, 410)

        cull_pts_perct_label = QLabel("Density", self)
        cull_pts_perct_label.move(50, 90)
        self.cull_pts_perct_edit = QLineEdit("2", self)
        self.cull_pts_perct_edit.move(150, 95)
        self.cull_pts_perct_edit.resize(30,20)

        cull_sbl_perct_label = QLabel("Threshold", self)
        cull_sbl_perct_label.move(200, 90)
        self.cull_sbl_perct_edit = QLineEdit("100", self)
        self.cull_sbl_perct_edit.move(300, 95)
        self.cull_sbl_perct_edit.resize(30,20)

        dist_label = QLabel("Grid Size", self)
        dist_label.move(50, 130)
        self.dist_edit = QLineEdit("10", self)
        self.dist_edit.move(150, 135)
        self.dist_edit.resize(30,20)

        skew_label = QLabel("Skew Distance", self)
        skew_label.move(200, 130)
        self.skew_edit = QLineEdit("0", self)
        self.skew_edit.move(300, 135)
        self.skew_edit.resize(30,20)

        pin_frame = QCheckBox("Pin Frame", self)
        pin_frame.resize(pin_frame.sizeHint())
        pin_frame.move(50, 60)
        pin_frame.stateChanged.connect(self.set_frame)

        edge_only = QCheckBox("Edge Only", self)
        edge_only.resize(edge_only.sizeHint())
        edge_only.move(150, 60)
        edge_only.stateChanged.connect(self.set_boundry)

        grey_weighted = QCheckBox("Grey_Weighted", self)
        grey_weighted.resize(edge_only.sizeHint())
        grey_weighted.move(250, 60)
        grey_weighted.stateChanged.connect(self.set_grey_weight)

        mode_lb = QLabel("Select Mode", self)
        mode_lb.move(50, 25)
        mode_lb.resize(mode_lb.sizeHint())
        mode_box = QComboBox(self)
        mode_box.addItem("Delaunay")
        mode_box.addItem("Voronoi")
        mode_box.addItem("Tri-Grid")
        mode_box.addItem("Square-Grid")
        mode_box.addItem("Voronoi-Grid")
        mode_box.addItem("Ortho-Tree")
        mode_box.addItem("Random-Tree")
        mode_box.move(150, 20)
        mode_box.resize(mode_box.sizeHint())
        mode_box.activated[str].connect(self.set_mode)

        pic_label = QLabel("Selected Raster Image", self)
        pic_label.move(50, 180)
        pic_label.resize(pic_label.sizeHint())
        self.pic = QLabel(self)
        #self.pic.setPixmap(QPixmap("wave.png"))
        self.pic.move(50, 200)
        self.pic.resize(300,200)
        self.pic.setScaledContents(True)
        self.pic.show()

        author_lb = QLabel("Peiyi Hou, 2018", self)
        author_lb.move(275, 450)
        pic_label.resize(400, 25)
