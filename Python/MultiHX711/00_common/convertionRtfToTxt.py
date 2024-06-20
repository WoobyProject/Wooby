#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 23:07:30 2024

@author: enriquem
"""

import os
from striprtf.striprtf import rtf_to_text


folder_path = '/Users/enriquem/Downloads/babydata'

rtf_files_list = [f for f in os.listdir(folder_path) if f.endswith('.rtf')]

for rtf_file in rtf_files_list:
    rtf_file_path = os.path.join(folder_path, rtf_file)
    txt_file_path = os.path.join(folder_path, os.path.splitext(rtf_file)[0] + '.txt')


    with open(rtf_file_path, 'r', encoding='utf-8', errors='ignore') as rtf_file:
        rtf_content = rtf_file.read()

    cleaned_content = rtf_to_text(rtf_content)
    # print(cleaned_content)

    with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(cleaned_content)

    print(f"Converted: {rtf_file_path} -> {txt_file_path}")
    
