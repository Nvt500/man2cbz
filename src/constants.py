import os


def get_root_dir() -> str:
    """Get the root directory"""

    return os.getcwd()

def get_temp_images_dir() -> str:
    """Get the directory of temp_images"""

    temp_images_dir = os.path.join(get_root_dir(), "temp_images")
    if not os.path.exists(temp_images_dir):
        os.makedirs(temp_images_dir)
    return temp_images_dir
