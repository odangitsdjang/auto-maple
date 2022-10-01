import shutil
import os

path = 'C:/Users/david jang/Downloads/auto-maple'

for directories, subfolder, files in os.walk(path):
    if os.path.isdir(directories):
        if directories[::-1][:11][::-1] == '__pycache__':
            shutil.rmtree(directories)