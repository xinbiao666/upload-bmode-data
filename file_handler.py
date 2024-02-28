import os
import shutil

class FileHandler():
    def remove(self, path):
        if os.path.exists(path):
            os.remove(path)
        else:
            raise '没有指定文件，无法删除'
        
    def rename(self, old_path, new_path):
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
        else:
            raise '没有指定文件，无法重命名'
        
    def is_exist(self, path):
        return os.path.exists(path)

    def generate_folder(self, folder_name):
        os.makedirs(folder_name, exist_ok=True)

    def move_file(self, origin, target):
        if os.path.exists(target) and os.path.isdir(target):
            shutil.rmtree(target)
        elif os.path.exists(target):
            os.remove(target)
        shutil.move(origin, target)