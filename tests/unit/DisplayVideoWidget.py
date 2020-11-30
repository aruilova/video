from PyQt5 import QtGui, QtCore, QtWidgets
import cv2
import sys
import os
import numpy as np
import time

def adjust_gamma(image, gamma=1.0):
	# build a lookup table mapping the pixel values [0, 255] to
	# their adjusted gamma values
    _gamma = 1.0 if gamma <= 0.001 else gamma
    invGamma = 1.0 / _gamma
    table = np.array([((i / 255.0) ** invGamma) * 255 
        for i in np.arange(0, 256)]).astype("uint8")
	# apply gamma correction using the lookup table
    return cv2.LUT(image, table)


class Thread(QtCore.QThread):
    CHANGE_PIXMAP = QtCore.pyqtSignal(QtGui.QImage)
    PARENT_UI = None

    VIDEO_FPS = 24
    VIDEO_WIDTH = 640
    VIDEO_HEIGHT = 480
    VIDEO_FRAME_COUNT = 100

    def __init__(self, parent=None, parent_ui=None, video_file=None):
        super(Thread, self).__init__(parent)
        self.video_file = video_file
        self.PARENT_UI = parent_ui

        # get mp4 stats
        cap = cv2.VideoCapture(self.video_file)
        self.VIDEO_FRAME_COUNT = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.VIDEO_FPS = cap.get(cv2.CAP_PROP_FPS)
        self.VIDEO_WIDTH = int(0.5 * cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.VIDEO_HEIGHT = int(0.5 * cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()

        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        cap = cv2.VideoCapture(self.video_file)
        fcount = 0
        prev_time = 0

        while self._running:
            # get time inc and continue if time corresponds to frame rate
            time_inc = time.time() - prev_time
            if time_inc <= 1.0 / self.VIDEO_FPS:
                continue

            # continue w image
            prev_time = time.time()
            ret, frame = cap.read()
            fcount += 1
            if ret:
                # get frame counter and reset if necessary
                if fcount == self.VIDEO_FRAME_COUNT:
                    fcount = 0
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                
                # adjust frame data
                _image = frame.copy()
                _image = adjust_gamma(_image, self.PARENT_UI.GAMMA)

                # set image pixmap
                frame_image = cv2.cvtColor(_image, cv2.COLOR_BGR2RGB)
                h, w, ch = frame_image.shape
                bytesPerLine = ch * w
                convertToQtFormat = QtGui.QImage(frame_image.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                p = convertToQtFormat.scaled(
                    self.VIDEO_WIDTH, self.VIDEO_HEIGHT, QtCore.Qt.KeepAspectRatio
                )
                self.CHANGE_PIXMAP.emit(p)
        
        cap.release()


class DisplayVideoWidget(QtWidgets.QWidget):
    KEY_PRESSED = QtCore.pyqtSignal(int)
    BASE_IMAGE = None
    GAMMA = 1.0
    THREAD = None

    def __init__(self, parent=None, video_file=None):
        super(DisplayVideoWidget, self).__init__(parent)

        self.image_file = video_file
        self.image_frame = QtWidgets.QLabel()

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)    
    
        self.KEY_PRESSED.connect(self.on_key)
        self.GAMMA = 1.0
        
        if os.path.exists(self.image_file):
            self.BASE_IMAGE = self.image_file
        else:
            print("Could not find image {}".format(self.image_file))

        # show the image
        self.show_image()

    def keyPressEvent(self, event):
        super(DisplayVideoWidget, self).keyPressEvent(event)
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

    @QtCore.pyqtSlot(QtGui.QImage)
    def set_image(self, image):
        self.image_frame.setPixmap(QtGui.QPixmap.fromImage(image))

    def show_image(self, gamma_shift=0.0, reset=False):
        if self.BASE_IMAGE is not None:
            # gamma image
            if not reset and gamma_shift > 0.0:
                self.GAMMA += gamma_shift
            else:
                self.GAMMA = 1.0

            # update pix map
            if self.THREAD:
                self.THREAD.terminate()

            self.THREAD = Thread(self, parent_ui=self, video_file=self.BASE_IMAGE)
            self.THREAD.CHANGE_PIXMAP.connect(self.set_image)
            self.THREAD.start()
