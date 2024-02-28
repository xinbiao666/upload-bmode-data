import base64
import re
import os
import subprocess
from lxml import etree

class Analysiser():

    def __init__(self, base_path):
        self.base_path = base_path
        self.path_to_execute = base_path + r'\xpdf'

    def analysis_pdf_to_txt(self, file):
        try:
            txt_name = 'new-pdf-data.txt'
            subprocess.run(
                f'pdftotext.exe -layout -enc GBK ../pdf/{file} ../txt/{txt_name}',
                stdout=subprocess.PIPE,
                text=True,
                shell=True,
                cwd=self.path_to_execute
            )
            return txt_name
        except subprocess.CalledProcessError as e:
            print(f"命令行执行错误: {e.returncode}")
            print(f"pdf提取txt文件失败: {e.output}")
        except Exception as e:
            print(f"pdf提取txt文件失败: {e}")

    def analysis_pdf_to_img(self, file, check_date, patient_info):
        try:
            subprocess.run(
                f'pdfimages.exe -j ../pdf/{file} ../img/{patient_info["name"]}-{patient_info["barcodeNum"]}({check_date})',
                stdout=subprocess.PIPE,
                text=True,
                shell=True,
                cwd=self.path_to_execute
            )
            return f"/img/{patient_info['name']}-{patient_info['barcodeNum']}({check_date})"
        except subprocess.CalledProcessError as e:
            print(f"命令行执行错误: {e.returncode}")
            print(f"pdf提取图片失败: {e.output}")
        except Exception as e:
            print(f"pdf提取图片失败: {e}")

    # file: '123456.txt'
    def analysis_txt_info(self, file):
        line_str = ''
        file_path = self.base_path + f'\\txt\\{file}'
        with open(file_path, 'r') as file:
            lines = file.readlines()
        for line in lines:
            line_str += line.rstrip()
        content = ''.join([i.strip(' ') for i in line_str])
        # content = line_str.replace(' ', '')
        return content
    
    def img_to_base64(self, file, patient_info):
        try:
            base64_list = []
            directory = self.base_path + '\\img'
            files = [file for file in os.listdir(
                directory) if file.startswith(f'{patient_info["name"]}-{patient_info["barcodeNum"]}')]
            for file in files:
                with open(directory + f'\\{file}', 'rb') as image_file:
                    image_data = image_file.read()
                    base64_encoded = "data:image/jpg;base64," + base64.b64encode(image_data).decode('utf-8')
                    base64_list.append(base64_encoded)
            return base64_list
        except Exception:
            print(f"图片转码失败: {Exception}")
    
    def img_to_base64_v2(self, img_path_list):
        try:
            base64_list = []
            for file in img_path_list:
                with open(file, 'rb') as image_file:
                    image_data = image_file.read()
                    base64_encoded = "data:image/jpg;base64," + base64.b64encode(image_data).decode('utf-8')
                    base64_list.append(base64_encoded)
            return base64_list
        except Exception as e:
            print(f"图片转码失败: {e}")

    def __extract_text(self, element):
        text = ""
        if element.text:
            text += element.text.strip()
        for child in element:
            text += self.__extract_text(child)
        if element.tail:
            text += element.tail.strip()
        return text

    def analysis_xml(self, file):
        namespaces = { "w": "http://schemas.microsoft.com/office/word/2003/wordml" }
        img_list = []
        try:
            tree = etree.parse(os.path.join(self.base_path + '/xml', file))
            root = tree.getroot()
            element_text = self.__extract_text(root)
            all_text_elements = root.findall(".//w:t", namespaces=namespaces)
            all_img_elements = root.findall(".//w:binData", namespaces=namespaces)
            for i in all_img_elements:
                if i.text:
                    img_list.append("data:image/jpg;base64," + i.text)
            full_text = "".join(t.text for t in all_text_elements if t.text).replace(" ", "")
            return {
                "all_element_text": element_text,
                "img_base64_list": img_list,
                "full_text": full_text
            }
        except Exception as e:
            print(f"error: {e}")
