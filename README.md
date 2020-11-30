# video

# first clone the repo (linux based instructions, Ubuntu 20.+):
cd ~
git clone https://github.com/aruilova/video.git

# run video test (currently core dumps when terminated, ok for now)
pytest-3 -s tests/unit/test_gui.py::test_ui_gamma_video

# run image test
pytest-3 -s tests/unit/test_gui.py::test_ui_gamma_image
