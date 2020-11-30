"""Test module or qt5 gui"""
from PyQt5 import QtGui, QtCore, QtWidgets
import cv2   # make sure this is opencv 4.1+
import sys
import os
import numpy as np

import pytest

# local imports
from .DisplayImageWidget import DisplayImageWidget
from .DisplayVideoWidget import DisplayVideoWidget
from .DisplayImageResizeWidget import DisplayImageResizeWidget

@pytest.fixture()
def base_image(pytestconfig):
    return pytestconfig.getoption("test_image")

@pytest.fixture()
def base_video(pytestconfig):
    return pytestconfig.getoption("test_avi")

def test_ui_gamma_image(base_image):
    # import ilos_viewer.ui as ui
    app = QtWidgets.QApplication([])
    display_image_widget = DisplayImageWidget(img_file=base_image)
    display_image_widget.show()
    ret = app.exec_()
    assert ret == 0

def test_ui_resize_image(base_image):
    # import ilos_viewer.ui as ui
    app = QtWidgets.QApplication([])
    display_image_widget = DisplayImageResizeWidget(img_file=base_image)
    display_image_widget.show()
    ret = app.exec_()
    assert ret == 0


def test_ui_gamma_video(base_video):
    # import ilos_viewer.ui as ui
    app = QtWidgets.QApplication([])
    display_image_widget = DisplayVideoWidget(video_file=base_video)
    display_image_widget.show()
    ret = app.exec_()
    assert ret == 0
