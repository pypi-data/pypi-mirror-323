import os
import shutil
def createfile(filename, filecontent):
    with open(filename, "w") as f:
        f.write(filecontent)

def deletefile(filepath):
    if os.path.exists(filepath):
        os.remove(filepath)
    else:
        print(f"betterfilesystemerr-file {filepath} not found")

def readfile(filepath):
    filecontent = ""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            filecontent = f.read()
    return filecontent

def editfile(filename, filecontent):
    createfile(filename, filecontent)

def move(currentpath, movedpath):
    if not os.path.exists(movedpath):
        try:
            os.mkdir(os.path.dirname(movedpath))
            os.rename(currentpath, movedpath)
        except FileExistsError:
            os.rename(currentpath, movedpath)

def create_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        print("betterfilesystemerr-directory or file already there.")

def delete_dir(directory):
    if not os.path.exists(directory):
        print("betterfilesystemerr-directory or file was not found.")
    else:
        shutil.rmtree(directory)