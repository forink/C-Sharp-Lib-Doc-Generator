"""
C# Lib Doc Generator
"""
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Author: Yifong Jiang
# C# Lib Doc Generator (use Python 3.9, Apache 2.0 License)
import datetime
import json
import logging
import os.path
import pathlib
import re
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path

## SETTINGS ################################
with open('settings.json', 'r', encoding="UTF-8") as json_settings:
    setting_dict = json.load(json_settings)

    datetime_format = setting_dict['datetime_format']
    log_file_name = setting_dict['log']['file_name']
    log_format = setting_dict['log']['format']
    log_maxsize_bytes = setting_dict['log']['maxsize_megabytes']*1048576 #(MB->Bytes)
    log_backup_count = setting_dict['log']['backup_count']  # logs qty to keep
    parser_output_file_name = setting_dict['parser']['output_file_name']
    parser_output_file_ext = setting_dict['parser']['output_file_ext']
    parser_output_file_encode = setting_dict['parser']['output_file_encode']
    parser_scan_file_ext = setting_dict['parser']['scan_file_ext']
    parser_scan_file_decode = setting_dict['parser']['scan_file_decode']
    parser_sheet_column_name = setting_dict['parser']['sheet_column_name']

# C# Class Regex
REGEX_CLASS_NAME_PTN = (r'<summary>\W+(.*?)\W+</summary>.*?'
                            r'(public|internal|protected|private)\s*'
                            r'(static|)\s*class\s+(.\w*)(.*)$')

# C# Function Regex
REGEX_FUNC_NAME_PTN = (r'<summary>\s*///\s*(.*?)\s*///\s*</summary>.*?'
                           r'(public|internal|protected|private)\s*(static|)\s*'
                           r'(virtual|)\s*(\w+)\s*([a-zA-Z0-9\<\>]*)\s*(.*?)\s*\{')
LOG_LEVEL = logging.INFO  # LOG Level

walk_dir = pathlib.Path().absolute()
log_file_path = f"{walk_dir}\\{log_file_name}"
output_file_path = f"{walk_dir}\\{parser_output_file_name}.{parser_output_file_ext}"
now = datetime.datetime.now().strftime(datetime_format)

## MAIN PROGRAM ################################
try:
    if __name__ == "__main__":

        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        log_handler = RotatingFileHandler(log_file_path, mode='a', maxBytes=log_maxsize_bytes,
                                          backupCount=log_backup_count, encoding="UTF-8", delay=0)

        log_handler.setFormatter(logging.Formatter(log_format))
        log_handler.setLevel(LOG_LEVEL)

        logger = logging.getLogger()
        logger.setLevel(LOG_LEVEL)
        logger.addHandler(log_handler)

    print(f"{now} {walk_dir}")

    regex_class_name = re.compile(REGEX_CLASS_NAME_PTN, re.M | re.I)
    regex_func_name = re.compile(REGEX_FUNC_NAME_PTN, re.M | re.I)

    with open(output_file_path, 'w', newline='', encoding=parser_output_file_encode) as result_file:
        result_file.write(f"{parser_sheet_column_name}\r\n")

        # Recursively read the file in the specified folder.
        for root, subdirs, files in os.walk(walk_dir):

            for subdir in subdirs:
                print(f"\t- subdirectory {subdir}")

            for filename in files:
                file_path = os.path.join(root, filename)

                print("\t- file %s (full path: %s)" % (filename, file_path))

                if pathlib.Path(file_path).suffix == f".{parser_scan_file_ext}":

                    relative_path = Path(file_path).relative_to(walk_dir.resolve())

                    with open(file_path, 'rb') as f:
                        f_content = f.read().decode(parser_scan_file_decode)
                        f_content = f_content.replace('\r\n', '')
                        match_class_list = regex_class_name.findall(f_content)

                        f_func_content = match_class_list[0][len(
                            match_class_list[0])-1]
                        match_func_list = regex_func_name.findall(
                            f_func_content)

                        class_summary = match_class_list[0][0]
                        class_public = match_class_list[0][1]
                        class_static = match_class_list[0][2]
                        class_name = match_class_list[0][3]

                        for func_sign in match_func_list:
                            try:
                                func_summary = func_sign[0]
                                func_public = func_sign[1]
                                func_static = func_sign[2]
                                func_virtual = func_sign[3]
                                func_return_type = func_sign[4]
                                func_name = func_sign[5]
                                func_paras = func_sign[6]

                                if func_name != '' and func_paras != '':
                                    result_file.write(
                                        f'"{relative_path}",{class_name},{class_summary},'
                                        f'"{func_return_type} {func_name} {func_paras}",'
                                        f'"{func_summary}"\r\n')

                            except KeyboardInterrupt as ex:
                                logger.error(ex)
                                print(ex)

    ALERT_MSG = "CSharp Lib Doc Generating Complete."
    logger.info(ALERT_MSG)
    print(f"{now}  {ALERT_MSG}")

except (ValueError, Exception) as ex: # pylint: disable=broad-except
    traceback.print_exc()
    now = datetime.datetime.now().strftime(datetime_format)
    ALERT_MSG = "CSharpLibDocGenerator was startup failure:"
    logger.error(f"{ALERT_MSG} {ex}")
    print(f"{now}  {ALERT_MSG} {ex}")
