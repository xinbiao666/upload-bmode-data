import os
from file_handler import FileHandler

handler = FileHandler()

folder_name = ('/img','/pdf','/rtf','/txt','/xml')
collect_fail_folder = '/uploadFailed'

base_path = os.getcwd()

for folder in folder_name:
    if not handler.is_exist(base_path + folder):
        handler.generate_folder(base_path + folder)
    if folder == '/pdf' or folder == '/rtf' or folder == '/xml':
        if not handler.is_exist(base_path + folder + collect_fail_folder):
            handler.generate_folder(base_path + folder + collect_fail_folder)
    