import importlib.util

def is_opencv_installed():
    return importlib.util.find_spec("cv2") is not None