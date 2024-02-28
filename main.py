import os
import time
import configparser
import intercept_info
from datetime import datetime

config = configparser.ConfigParser()
config.read('config.ini', 'utf-8')

hosp_adr = config.get('address', 'current')

base_path = os.getcwd()
directory_path = base_path + config.get('folder', hosp_adr)

suffix = config.get('suffix', hosp_adr)

base_url = config.get('host', hosp_adr)

def handler(directory):
    files = [file for file in os.listdir(directory) if file.endswith(suffix)]
    for file in files:
        file_path = os.path.join(directory, file)
        if hosp_adr == 'stxgy':
            while not intercept_info.pdf_content_is_ready(file_path):
                time.sleep(1)
            txt_str, txt_name = intercept_info.analysis_txt_str(base_path, file)
            patient_info = intercept_info.get_patient_info_txt_stxgy(txt_str)
            intercept_info.get_img_in_pdf(base_path, patient_info, file)
            patient_info = intercept_info.get_base64_list(file, base_path, patient_info)
            check_date = datetime.strptime(patient_info['checkDate'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            intercept_info.file_rename(f"{base_path}/txt", txt_name, f"{patient_info['name']}-{patient_info['barcodeNum']}({check_date}).txt")
            post_flag = intercept_info.post_info_to_pc(base_url, patient_info)
            date_folder = intercept_info.open_folder(patient_info, directory)
            intercept_info.move_file(post_flag, file_path, date_folder, directory, patient_info, suffix)
        elif hosp_adr == 'fstn':
            patient_info = intercept_info.analysis_xml_str(base_path, file)
            post_flag = intercept_info.post_info_to_pc(base_url, patient_info)
            date_folder = intercept_info.open_folder(patient_info, directory)
            intercept_info.move_file(post_flag, file_path, date_folder, directory, patient_info, suffix)
        elif hosp_adr == "huazhou":
            content, check_date_time = intercept_info.get_str_from_rtf(file_path)
            patient_info = {}
            patient_info = intercept_info.get_patient_info_rtf(content, patient_info, check_date_time)
            file_date_name = datetime.strptime(patient_info["checkDate"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            folder_name = os.path.join(directory, f"{patient_info['name']}({file_date_name})")
            file_name = f"{patient_info['name']}-{patient_info['barcodeNum']}({file_date_name})"
            os.makedirs(folder_name, exist_ok=True)
            intercept_info.convert_rtf_to_html(os.path.join(directory, file), f"{folder_name}/{file_name}.html")
            patient_info = intercept_info.get_bmode_result_html(f"{folder_name}/{file_name}.html", patient_info)
            patient_info = intercept_info.get_img_list_html(base_path, directory, f"{folder_name}/{file_name}.html", patient_info)
            post_flag = intercept_info.post_info_to_pc(base_url, patient_info)
            date_folder = intercept_info.open_folder(patient_info, directory)
            intercept_info.move_file(post_flag, file_path, date_folder, directory, patient_info, suffix)
            intercept_info.move_file(post_flag, f"{directory}/{patient_info['name']}({file_date_name})", date_folder, directory, patient_info, '')

if __name__ == "__main__":
    print("上传程序已启动")
    while True:
        handler(directory_path)
        time.sleep(3)
