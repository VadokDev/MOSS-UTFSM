from os import listdir, path
from shutil import copytree, copy2


def sanitize(word):
    return (
        word.replace("Á", "a")
        .replace("É", "e")
        .replace("Í", "i")
        .replace("Ó", "o")
        .replace("Ú", "u")
    )


def getFileNames(directory):
    return [
        file for file in listdir(directory) if path.isfile(path.join(directory, file))
    ]


def getFileNameSection(fileName):
    return fileName.split("_")[2]


def copyEntireFolder(src, dst, symlinks=False, ignore=None):
    for item in listdir(src):
        s = path.join(src, item)
        d = path.join(dst, item)
        if path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            copy2(s, d)
