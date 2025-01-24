#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
@Time        : 2023/3/2
@File        : util_requirements.py
@Author      : MysteriousMan
@version     : python 3
@Description : 依赖库
               判断程序是否每次会更新依赖库，如有更新，则自动安装
"""
import json
import os
import chardet


class InstallRequirements:
    """ 自动识别安装最新依赖库 """

    def __init__(self, version_path, requirements_path, exclude_path):
        """
        初始化
        Args:
            version_path: 版本控制文件路径
            requirements_path: 原始文件路径
            exclude_path: 排除库的配置文件路径 json文件
        """
        self.version_library_comparisons_path = version_path
        self.requirements_path = requirements_path
        self.exclude_path = exclude_path
        # 初始化时，获取最新的版本库
        self.get_latest_requirements()

    def get_latest_requirements(self):
        """ 获取最新的依赖库信息并保存到 requirements.txt """
        try:
            os.system("pip freeze > {}".format(self.requirements_path))
        except Exception as e:
            print(f"获取最新依赖库时出错: {e}")

    def read_version_library_comparisons_txt(self):
        """
        获取版本比对默认的文件
        @return: 文件内容
        """
        try:
            with open(self.version_library_comparisons_path, 'r', encoding="utf-8") as file:
                return file.read().strip(' ')
        except Exception as e:
            print(f"读取版本比对文件时出错: {e}")

    @classmethod
    def check_charset(cls, file_path):
        """获取文件的字符集"""
        try:
            with open(file_path, "rb") as file:
                data = file.read(4)
                charset = chardet.detect(data)['encoding']
            return charset
        except Exception as e:
            print(f"检测文件编码时出错: {e}")

    def read_requirements(self):
        """获取安装文件"""
        file_data = ""
        try:
            with open(
                    self.requirements_path,
                    'r',
                    encoding=self.check_charset(self.requirements_path)
            ) as file:
                for line in file:
                    if "[0m" in line:
                        line = line.replace("[0m", "")
                    file_data += line

            with open(
                    self.requirements_path,
                    "w",
                    encoding=self.check_charset(self.requirements_path)
            ) as file:
                file.write(file_data)
        except Exception as e:
            print(f"读取或写入 requirements 文件时出错: {e}")

        return file_data

    def exclude_libraries(self):
        """
        读取排除库的配置文件
        @return: 排除库的列表
        """
        try:
            with open(self.exclude_path, 'r') as file:
                exclude_data = json.load(file)
                return exclude_data.get('libraries', [])
        except Exception as e:
            print(f"读取排除库配置文件时出错: {e}")
            return []

    def text_comparison(self):
        """
        版本库比对
        @return:
        """
        read_version_library_comparisons_txt = self.read_version_library_comparisons_txt()
        read_requirements = self.read_requirements()
        exclude_libraries = self.exclude_libraries()

        # 过滤掉排除库的信息
        requirements_lines = read_requirements.split('\n')
        filtered_requirements = [line for line in requirements_lines if not any(line.startswith(exclude_lib) for exclude_lib in exclude_libraries)]
        filtered_version = [line for line in read_version_library_comparisons_txt.split('\n') if not any(line.startswith(exclude_lib) for exclude_lib in exclude_libraries)]

        if filtered_version == filtered_requirements:
            print("程序中未检查到更新版本库（排除指定库后），已为您跳过自动安装库")
        # 程序中如出现不同的文件，则安装
        else:
            print("程序中检测到您更新了依赖库（排除指定库后），已为您自动安装")
            try:
                os.system(f"pip install -r {self.requirements_path}")
                with open(self.version_library_comparisons_path, "w",
                          encoding=self.check_charset(self.requirements_path)) as file:
                    file.write('\n'.join(filtered_requirements))
            except Exception as e:
                print(f"安装依赖库或更新版本比对文件时出错: {e}")


if __name__ == '__main__':
    install_requirements = InstallRequirements(
        "/install_tool/version_library_comparisons.txt",
        "/requirements.txt",
        "/exclude_config.json",
    )
    install_requirements.text_comparison()

    # json
    # {
    #   "libraries": [
    #     "library1",
    #     "library2"
    #   ]
    # }
