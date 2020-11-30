def pytest_addoption(parser):
    parser.addoption("--test_image", action="store", 
        default="./data/starry_night_grey_scale.jpg")
    parser.addoption("--test_avi", action="store", 
        default="./data/vtest.avi"
    )
    
