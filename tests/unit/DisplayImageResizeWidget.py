from PyQt5 import QtGui, QtCore, QtWidgets
import cv2
import sys
import os

import numpy as np


class DisplayImageResizeWidget(QtWidgets.QWidget):
    KEY_PRESSED = QtCore.pyqtSignal(int)
    BASE_RES = (0, 0)
    CURR_RES = (0, 0)
    BASE_CENTER = (0, 0)
    CURR_CENTER = (0, 0)

    BASE_IMAGE = None
    BORDER = 5

    def __init__(self, parent=None, img_file=None):
        super(DisplayImageResizeWidget, self).__init__(parent)

        self.image_file = img_file
        self.image_frame = QtWidgets.QLabel()
        self.image_frame.setAlignment(QtCore.Qt.AlignCenter)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)    
    
        self.KEY_PRESSED.connect(self.on_key)
        self.GAMMA = 1.0

        if os.path.exists(self.image_file):
            self.BASE_IMAGE = cv2.imread(self.image_file)
            self.BASE_RES = (self.BASE_IMAGE.shape[1], self.BASE_IMAGE.shape[0])  # note swap here
            self.CURR_RES = self.BASE_RES
            self.resize(
                self.BASE_RES[0] + self.BORDER, 
                self.BASE_RES[1] + self.BORDER
            )
            self._fx = 1.0
            self._fy = 1.0
            self._shift_x = 0
            self._shift_y = 0

        else:
            print("Could not find image {}".format(self.image))

        # show the image
        self.show_image()

    def keyPressEvent(self, event):
        super(DisplayImageResizeWidget, self).keyPressEvent(event)
        self.KEY_PRESSED.emit(event.key())

    def on_key(self, key):
        # test for a specific key
        if key == QtCore.Qt.Key_I:
            print('zoom +10%')
            self.show_image(scale_inc=0.1)
        elif key == QtCore.Qt.Key_O:
            print('zoom -10%')
            self.show_image(scale_inc=-0.1)
        elif key == QtCore.Qt.Key_Left:
            print('shift left 10 pixels')
            self.show_image(shift=(10, 0))
        elif key == QtCore.Qt.Key_Right:
            print('shift right 10 pixels')
            self.show_image(shift=(-10, 0))
        elif key == QtCore.Qt.Key_Up:
            print('shift up 10 pixels')
            self.show_image(shift=(0, 10))
        elif key == QtCore.Qt.Key_Down:
            print('shift down 10 pixels')
            self.show_image(shift=(0, -10))
        elif key == QtCore.Qt.Key_R:
            print('zoom reset')
            self.show_image(reset=True)
        else:
            print('key pressed: %i' % key)

    def show_image(self, scale_inc=0.0, shift=(0, 0), reset=False):
        if self.BASE_IMAGE is not None:
            image = self.BASE_IMAGE.copy()
            sw = 0
            sh = 0
            # resize image and get new top let corner pos
            if not reset:
                self._fx += scale_inc
                self._fy += scale_inc
                self._shift_x += shift[0]
                self._shift_y += shift[1]
                image = cv2.resize(image, None, fx=self._fx, fy=self._fy, interpolation = cv2.INTER_AREA).copy()
                W, H = image.shape[1], image.shape[0]
                sw = int((W - self.BASE_RES[0])/2) + self._shift_x
                sh = int((H - self.BASE_RES[1])/2) + self._shift_y
            else:
                self._shift_x = self._shift_y = 0
                self._fx = self._fy = 1.0

            # set qt pixmap
            self.q_image = QtGui.QImage(
                image.data, 
                image.shape[1], image.shape[0],
                QtGui.QImage.Format_RGB888
            ).rgbSwapped()
            pixmap = QtGui.QPixmap.fromImage(self.q_image)

            # crop pixmap
            xform = QtGui.QTransform()
            xform.translate(sw, sh)
            rect = QtCore.QRect(
                QtCore.QPoint(sw, sh), QtCore.QSize(self.BASE_RES[0], self.BASE_RES[1])
            )
            pixmap = pixmap.copy(rect)            
            xformed_pixmap = pixmap.transformed(xform, QtCore.Qt.SmoothTransformation)
            self.image_frame.setPixmap(xformed_pixmap)

            # re-align frame if necessary
            print(sw, sh)
            if not reset:
                if sw > 0:
                    self.image_frame.setAlignment(QtCore.Qt.AlignLeft)
                elif sw < 0: 
                    self.image_frame.setAlignment(QtCore.Qt.AlignRight)
                if sh > 0:
                    self.image_frame.setAlignment(QtCore.Qt.AlignTop)
                elif sh < 0:
                    self.image_frame.setAlignment(QtCore.Qt.AlignBottom)
