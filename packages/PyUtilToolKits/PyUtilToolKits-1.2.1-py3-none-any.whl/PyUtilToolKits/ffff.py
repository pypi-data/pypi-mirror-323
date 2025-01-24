# -*- coding:utf-8 -*-
"""
@Time        : 2025/1/24 17:41
@File        : ffff.py
@Author      : lyz
@Version     : python 3.11
@Description : 
"""
def write_list_to_txt(lst, file_path):
    with open(file_path, 'w') as file:
        for item in lst:
            file.write(str(item) + '\n')

# 示例用法
my_list = [1, 2, 3, "hello", "world"]
write_list_to_txt(my_list, "output.txt")