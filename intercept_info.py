import os
import re
import fitz
import requests
import pythoncom
import file_handler
import file_analysiser
import win32com.client
from lxml import etree
from datetime import datetime
from striprtf.striprtf import rtf_to_text


def analysis_xml_str(base_path, file):
    analy = file_analysiser.Analysiser(base_path)
    xml_info = analy.analysis_xml(file)
    patient_info = get_patient_info_xml(xml_info['full_text'])
    prompt = get_prompt(xml_info['all_element_text'])
    patient_info["prompt"] = prompt
    patient_info['bmodeImgList'] = xml_info['img_base64_list']
    return patient_info

def get_patient_info_xml(content):
    patient_info = {}
    name_start = content.find("姓名:") + len("姓名:")
    name_end = content.find("性别")
    barcode_num_start = content.find("床号：") + len("床号：")
    barcode_num_end = content.find("床申检医生")
    check_result_start = content.find("超声所见:") + len("超声所见:")
    check_result_end = content.find("超声提示")
    check_position_start = content.find("申检项:") + len("申检项:")
    check_position_end = content.find("超声所见")
    check_date_start = content.find("报告日期:") + len("报告日期:")
    check_date_end = content.find("此报告仅供临床参考")
    # 姓名
    name = content[name_start:name_end].strip()
    # 体检编号
    barcode_num = content[barcode_num_start:barcode_num_end].strip()
    # 检查所见
    check_result = content[check_result_start:check_result_end].strip()
    # 检查部位
    check_position = content[check_position_start:check_position_end].strip()
    # 检查日期
    check_date = content[check_date_start:check_date_end].strip()
    check_date = datetime.strptime(check_date, "%Y年%m月%d日%H::%M").strftime("%Y-%m-%d %H:%M:%S")

    patient_info["name"] = name
    patient_info["barcodeNum"] = barcode_num
    patient_info["checkDate"] = check_date
    patient_info["testPart"] = check_position
    patient_info["testResult"] = check_result

    return patient_info

def get_prompt(text):
    check_tips_start = text.find('"图像诊断" \\* MERGEFORMAT') + len('"图像诊断" \\* MERGEFORMAT')
    check_tips_end = text.find("丰顺县汤南镇中心卫生院")
    check_tips = text[check_tips_start:check_tips_end].strip()
    return check_tips

def analysis_txt_str(base_path, file):
    analy = file_analysiser.Analysiser(base_path)
    txt_name = analy.analysis_pdf_to_txt(file)
    txt_str = analy.analysis_txt_info(txt_name)
    return txt_str, txt_name

def get_img_in_pdf(base_path, patient_info, file):
    analy = file_analysiser.Analysiser(base_path)
    check_date = datetime.strptime(patient_info['checkDate'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
    analy.analysis_pdf_to_img(file, check_date , patient_info)

def get_base64_list(file, base_path, patient_info):
    analy = file_analysiser.Analysiser(base_path)
    img_base64_list = analy.img_to_base64(file, patient_info)
    patient_info['bmodeImgList'] = img_base64_list
    return patient_info

def get_base64_list_v2(base_path, img_path_list):
    analy = file_analysiser.Analysiser(base_path)
    base64_list = analy.img_to_base64_v2(img_path_list)
    return base64_list

def pdf_content_is_ready(file_path):
    try:
        doc = fitz.open(file_path)
        # 检查PDF内容是否已经准备好
        return len(doc) > 0
    except Exception as e:
        print(f"pdf生成出现错误: {e}")
        return False

# directory: os.getcwd() + '/pdf'
def open_folder(patient_info, directory):
    f_handle = file_handler.FileHandler()
    check_date = datetime.strptime(patient_info['checkDate'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")

    date_folder = os.path.join(directory, str(check_date))
    f_handle.generate_folder(date_folder)

    return date_folder

def file_rename(origin_folder, old_name, new_name):
    f_handle = file_handler.FileHandler()

    old_path = f"{origin_folder}/{old_name}"
    new_path = f"{origin_folder}/{new_name}"

    if f_handle.is_exist(new_path):
        f_handle.remove(new_path)
    f_handle.rename(old_path, new_path)

def move_file(post_flag, file_path, date_folder, directory, patient_info, suffix):
    check_date = datetime.strptime(patient_info['checkDate'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
    f_handle = file_handler.FileHandler()
    # 移动文件到对应的文件夹
    origin = file_path
    target = ''
    if post_flag:
        target = os.path.join(date_folder, f'{patient_info["name"]}-{patient_info["barcodeNum"]}({check_date}){suffix}')
    else:
        target = os.path.join(directory, f'uploadFailed/{patient_info["name"]}-{patient_info["barcodeNum"]}({check_date}){suffix}')
    f_handle.move_file(origin, target)
    return post_flag

def get_patient_info_txt_stxgy(content):
    patient_info = {}
    name_start = content.find("姓名:") + len("姓名:")
    name_end = content.find("性别:")
    barcode_num_start = content.find("床号:") + len("床号:")
    barcode_num_end = content.find("病人来源")
    check_result_start = content.find("超声所见") + len("超声所见")
    check_result_end = content.find("超声提示")
    check_tips_start = content.find("超声提示") + len("超声提示")
    check_tips_end = content.find("检查医生")
    check_position_start = content.find("检查部位:") + len("检查部位:")
    check_position_end = content.find('检查图像')
    check_date_start = content.find("检查时间:") + len("检查时间:")
    check_date_end = content.find('打印时间')
    # 姓名
    name = content[name_start:name_end].strip()
    # 体检编号
    barcode_num = content[barcode_num_start:barcode_num_end].strip()
    # 检查所见
    check_result = content[check_result_start:check_result_end].strip()
    # 检查提示
    check_tips = content[check_tips_start:check_tips_end].strip()
    # 检查部位
    check_position = content[check_position_start:check_position_end].strip()
    # 检查日期
    check_date = content[check_date_start:check_date_end].strip()
    check_date = datetime.strptime(check_date, "%Y-%m-%d").strftime("%Y-%m-%d %H:%M:%S")

    patient_info["name"] = name
    patient_info["barcodeNum"] = barcode_num
    patient_info["checkDate"] = check_date
    patient_info["testPart"] = check_position
    patient_info["testResult"] = check_result
    patient_info["prompt"] = check_tips

    return patient_info

def get_patient_info_txt_hz(content):
    patient_info = {}
    barcode_num_flag = content.find("床号：")
    name_start = content.find("姓名：") + len("姓名：")
    name_end = content.find("性别：")
    barcode_num_start = content.find("住院号：") + len("住院号：")
    barcode_num_end = content.find("送检科室") if barcode_num_flag == -1 else content.find("床号：")
    check_position_start = content.find("检查部位：") + len("检查部位：")
    check_position_end = content.find('图像所见')
    check_date_start = content.find("检查日期：") + len("检查日期：")
    check_date_end = content.find("审核医生")
    # 姓名
    name = content[name_start:name_end].strip()
    # 体检编号
    barcode_num = content[barcode_num_start:barcode_num_end].strip()
    # 检查部位
    check_position = content[check_position_start:check_position_end].strip()
    # 检查日期
    check_date = content[check_date_start:check_date_end].strip()
    check_date = datetime.strptime(check_date, "%Y/%m/%d%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

    patient_info["name"] = name
    patient_info["barcodeNum"] = barcode_num
    patient_info["checkDate"] = check_date
    patient_info["testPart"] = check_position

    return patient_info

def post_info_to_pc(base_url, patient_info):
    data_list = []
    data_list.append(patient_info)
    try:
        response = requests.post(
            base_url + '/lianan-pc/upload/pc/checklst/uploadBmData',
            json=data_list,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            if response.json()['code'] == 200:
                print('终端提示:', patient_info['name'] + ' ' + response.json()["msg"])
                return True
            else:
                print('终端提示:', patient_info['name'] + ' ' + response.json()["msg"])
                return False
        else:
            print('终端提示:', f"{patient_info['name']}上传失败，错误码：{response.status_code}，错误信息{response.json()['msg']}")
            return False
    except requests.exceptions.RequestException as e: 
        print('网络错误:', e)
        return False
    
def convert_rtf_to_html(rtf_path, html_path):
    pythoncom.CoInitialize()

    word_app = win32com.client.Dispatch("Word.Application")
    word_app.Visible = False

    try:
        doc = word_app.Documents.Open(rtf_path)
        doc.SaveAs2(html_path, FileFormat=8)
        doc.Close()
    except Exception as e:
        print(f"转换失败: {e}")
    finally:
        word_app.Quit()

def get_str_from_rtf(file_path):
    text = ""
    with open(file_path) as open_file:
        rtf_content = open_file.read()
        text = rtf_to_text(rtf_content)
    pattern = r'\b\d{4}/\d{1,2}/\d{1,2} \d{1,2}:\d{1,2}:\d{1,2}\b'
    matches = re.findall(pattern, text) if re.findall(pattern, text) else ""
    content = "".join(re.findall(r"\b\w+\b",text))
    return content, matches[0]

def get_patient_info_rtf(content, patient_info, check_date_time):
    barcode_num_flag = content.find("床号")
    bmode_img_flag = content.find("图像所见")
    name_start = content.find("姓名") + len("姓名")
    name_end = content.find("性别")
    barcode_num_start = content.find("住院号") + len("住院号")
    barcode_num_end = content.find("送检科室") if barcode_num_flag == -1 else content.find("床号")
    check_position_start = content.find("检查部位") + len("检查部位")
    check_position_end = content.find("超声所见") if bmode_img_flag == -1 else content.find("图像所见")

    # 姓名
    name = content[name_start:name_end].strip()
    # 体检编号
    barcode_num = content[barcode_num_start:barcode_num_end].strip()
    # 检查部位
    check_position = content[check_position_start:check_position_end].strip()
    # 检查日期
    check_date = check_date_time

    info_check_date = datetime.strptime(check_date, "%Y/%m/%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

    patient_info["name"] = name
    patient_info["barcodeNum"] = barcode_num
    patient_info["checkDate"] = info_check_date
    patient_info["testPart"] = check_position

    return patient_info

def get_bmode_result_html(html_file, patient_info):
    html = etree.parse(html_file, etree.HTMLParser(encoding='GBK'))

    font_list = html.xpath('//font')
    
    html_text = ''

    for font in font_list:
        if font.text:
            html_text += font.text

    check_result_start = html_text.find("超声所见：") + len("超声所见：")
    check_result_end = html_text.find("超声提示")
    check_tips_start = html_text.find("超声提示：") + len("超声提示：")
    check_tips_end = html_text.find("检查日期")

    # 检查所见
    check_result = html_text[check_result_start:check_result_end].strip()
    # 检查提示
    check_tips = html_text[check_tips_start:check_tips_end].strip()

    patient_info["testResult"] = check_result
    patient_info["prompt"] = check_tips

    return patient_info

def get_img_list_html(base_path, directory_path, html_file, patient_info):
    html = etree.parse(html_file, etree.HTMLParser(encoding='GBK'))

    file_name_date = datetime.strptime(patient_info["checkDate"], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")

    img_list = html.xpath('//img')[1:]

    img_path_list = [img.get("src") for img in img_list if img.get("src")]
    img_full_path_list = [f"{directory_path}/{patient_info['name']}({file_name_date})/{img_path}" for img_path in img_path_list]

    base64_list = get_base64_list_v2(base_path, img_full_path_list)

    patient_info['bmodeImgList'] = base64_list

    return patient_info