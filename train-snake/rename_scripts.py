# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 14:38:52 2020

@author: Logan Rowe
"""

import os
import glob

files=glob.glob('./drafts/*')
new_files=[file.replace('-','_') for file in files]

print(new_files)
for name,new_name in zip(files,new_files):
    os.rename(name,new_name)