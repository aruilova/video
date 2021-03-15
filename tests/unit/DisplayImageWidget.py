from PyQt5 import QtGui, QtCore, QtWidgets
import cv2
import sys
import os
import numpy as np


def adjust_brightness_contrast(input_img: np.ndarray, brightness: int = 0, contrast: int = 0):
    """this function basically does a blend between brightest pixels in the image (highlights)
    and the lowest (shadows). The values -127,127 basically set the bounds for those values.
    it's just 0-256 center shifted

    Taken from:
    https://ie.nitk.ac.in/blog/2020/01/19/algorithms-for-adjusting-brightness-and-contrast-of-an-image/
    """
    print("Brightness = ", brightness)
    print("Contrast = ", contrast)
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        # get multipliers which are proportional to the brightness adjustment
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow

        # blend (cross dissolve) between image scaled by alpha_b and same image scaled by gamma_b
        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()

    if contrast != 0:
        # use 1/2 contrast correction factor (131, 127 instead of 259, 255)
        # recommended for high dynamic range images and looks better than original values
        f = 131 * (contrast + 127) / (127 * (131 - contrast))
        alpha_c = f
        gamma_c = 127 * (1 - f)

        # blend (cross dissolve) between image scaled by contrast factor 'f' and its inverse
        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf


def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
    invGamma = gamma
    print("Gamma = ", str(round(invGamma, 2)))
    table = np.array([((i / 255.0) ** invGamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)


class DisplayImageWidget(QtWidgets.QWidget):
    KEY_PRESSED = QtCore.pyqtSignal(int)
    BASE_IMAGE = None
    GAMMA = 1.0
    BRIGHTNESS = 0.0
    CONTRAST = 0.0

    def __init__(self, parent=None, img_file=None):
        super(DisplayImageWidget, self).__init__(parent)

        self.image_file = img_file
        self.image_frame = QtWidgets.QLabel()

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)    
    
        self.KEY_PRESSED.connect(self.on_key)
        self.GAMMA = 1.0
        self.BRIGHTNESS = 0.0
        self.CONTRAST = 0.0

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
            self.show_image(gamma_shift=0.1, bright_shift=0.0, contrast_shift=0.0)
        elif key == QtCore.Qt.Key_H:
            self.show_image(gamma_shift=-0.1, bright_shift=0.0, contrast_shift=0.0)
        elif key == QtCore.Qt.Key_C:
            self.show_image(gamma_shift=0.0, bright_shift=0.0, contrast_shift=0.1)
        elif key == QtCore.Qt.Key_V:
            self.show_image(gamma_shift=0.0, bright_shift=0.0, contrast_shift=-0.1)
        elif key == QtCore.Qt.Key_B:
            self.show_image(gamma_shift=0.0, bright_shift=0.1, contrast_shift=0.0)
        elif key == QtCore.Qt.Key_N:
            self.show_image(gamma_shift=0.0, bright_shift=-0.1, contrast_shift=0.0)
        elif key == QtCore.Qt.Key_R:
            self.show_image(reset=True)
        else:
            print('key pressed: %i' % key)

    def show_image(self, gamma_shift=0.0, bright_shift=0.0, contrast_shift=0.0, reset=False):
        if self.BASE_IMAGE is not None:
            image = self.BASE_IMAGE.copy()
            
            # gamma image
            if not reset:
                print ("\n-------- Updating image --------")
                if abs(gamma_shift) > 0.0:
                    self.GAMMA += gamma_shift
                elif abs(bright_shift) > 0.0:
                    self.BRIGHTNESS += int(bright_shift * 127)
                elif abs(contrast_shift) > 0.0:
                    self.CONTRAST += int(contrast_shift * 127)
            else:
                print ("\n-------- Reset --------")
                self.GAMMA = 1.0
                self.BRIGHTNESS = 0.0
                self.CONTRAST = 0.0

            image = adjust_gamma(image, gamma=self.GAMMA)
            image = adjust_brightness_contrast(image, brightness=self.BRIGHTNESS, contrast=self.CONTRAST)
            
            # update pix map
            self.q_image = QtGui.QImage(
                image.data, 
                image.shape[1], image.shape[0],
                QtGui.QImage.Format_RGB888).rgbSwapped()
            self.image_frame.setPixmap(QtGui.QPixmap.fromImage(self.q_image)) 

