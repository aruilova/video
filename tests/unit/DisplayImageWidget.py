from PyQt5 import QtGui, QtCore, QtWidgets
import cv2
import sys
import os
import numpy as np

def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
	invGamma = 1.0 / gamma
	table = np.array([((i / 255.0) ** invGamma) * 255
		for i in np.arange(0, 256)]).astype("uint8")
	# apply gamma correction using the lookup table
	return cv2.LUT(image, table)


class DisplayImageWidget(QtWidgets.QWidget):
    KEY_PRESSED = QtCore.pyqtSignal(int)
    BASE_IMAGE = None
    GAMMA = 1.0

    def __init__(self, parent=None, img_file=None):
        super(DisplayImageWidget, self).__init__(parent)

        self.image_file = img_file
        self.image_frame = QtWidgets.QLabel()

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)    
    
        self.KEY_PRESSED.connect(self.on_key)
        self.GAMMA = 1.0
        
        if os.path.exists(self.image_file):
            self.BASE_IMAGE = cv2.imread(self.image_file)
        else:
            print("Could not find image {}".format(self.image_file))

        # show the image
        self.show_image()

    def keyPressEvent(self, event):
        super(DisplayImageWidget, self).keyPressEvent(event)
        self.KEY_PRESSED.emit(event.key())

    def on_key(self, key):
        # test for a specific key
        if key == QtCore.Qt.Key_G:
            print('gamma +10%')
            self.show_image(gamma_shift=0.1)
        elif key == QtCore.Qt.Key_R:
            print('zoom reset')
            self.show_image(reset=True)
        else:
            print('key pressed: %i' % key)

    def show_image(self, gamma_shift=0.0, reset=False):
        if self.BASE_IMAGE is not None:
            image = self.BASE_IMAGE.copy()

            # gamma image
            if not reset and gamma_shift > 0.0:
                self.GAMMA += gamma_shift
                image = adjust_gamma(image, gamma=self.GAMMA)
            else:
                self.GAMMA = 1.0

            # update pix map
            self.q_image = QtGui.QImage(
                image.data, 
                image.shape[1], image.shape[0],
                QtGui.QImage.Format_RGB888).rgbSwapped()
            self.image_frame.setPixmap(QtGui.QPixmap.fromImage(self.q_image)) 

