#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 18:14:54 2024

@author: enriquem
"""

import os
from striprtf.striprtf import rtf_to_text


folder_path = '/Users/enriquem/Documents/HumanityLab/Wooby/GitHub3/Wooby/Python/datasets/WoobyQuadHX711ForBeetleNew3DPieces'

files_list = [f for f in os.listdir(folder_path) if f.endswith('.txt') and f.startswith('25_06_2024') ]


# Mapping for the wwights
mappingWeights = {
    "2500": "2590",
    "5000": "5020",
    "8110": "8110",
}
# Mapping for the last characters
mapping = {
    "C": "1",
    "C2": "4",
    "D": "2",
    "D2": "5",
    "G": "3",
    "G2": "6"
}

# Process each file
for wooby_file in files_list:
    # Split the filename
    parts = wooby_file.split('_')
    
    # Replace the date part
    new_name_parts = ["WoobyQuadHX711ForBeetleNew3DPieces"]
    
    # Replace the number part
    number_part = mappingWeights.get(parts[3])  + "gr"
    new_name_parts.append( number_part )
    
    # Map the last part
    last_part = parts[4][:-4]
    new_last_part = mapping.get(last_part, last_part)
    new_name_parts.append(new_last_part)
    
    # Construct the new filename
    new_file_name = '_'.join(new_name_parts) + '.txt'
    
    # Create the full old and new file paths
    old_file_path = os.path.join(folder_path, wooby_file)
    new_file_path = os.path.join(folder_path, new_file_name)
    
    # Create the full old and new file paths
    old_file_path = os.path.join(folder_path, wooby_file)
    new_file_path = os.path.join(folder_path, new_file_name)
    
    
    # Read the content of the old file
    with open(old_file_path, 'r', encoding='utf-8') as old_file:
        content = old_file.read()
    
    # Write the content to the new file
    with open(new_file_path, 'w', encoding='utf-8') as new_file:
        new_file.write(content)
    
    print(f'Created {new_file_name} from {wooby_file}')
