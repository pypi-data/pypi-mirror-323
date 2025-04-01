import os


def check_can_put_file(path: str):
    if os.path.isdir(path):
        raise RuntimeError(f"cannot put file at path {path}: is a directory")


def check_can_put_directory(path: str):
    if os.path.isfile(path):
        raise RuntimeError(f"cannot put directory at path {path}: is a file")


def softlink_exists(source, destination):
    if not os.path.islink(destination):
        return False

    return os.path.realpath(os.readlink(destination)) == os.path.realpath(source)
