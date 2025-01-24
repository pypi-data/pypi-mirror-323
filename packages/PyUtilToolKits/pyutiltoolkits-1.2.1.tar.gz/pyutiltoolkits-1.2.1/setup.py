# -*- coding:utf-8 -*-
"""
@Time        : 2025/1/16 15:45
@File        : setup.py
@Author      : lyz
@Version     : python 3.11
@Description : 
"""
from setuptools import setup, find_packages

"""
读取 README.md 文件
"""
with open('PyUtilToolKits/README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()
print(f"Long description:\n{long_description}")

setup(
    name='PyUtilToolKits',  # 包名 别人安装时就是用此名来按照
    version='1.2.1',  # 包的版本号
    description='Python Utils',  # 包的介绍、概述
    author='MysteriousMan',  # 包的作者
    author_email='MysteriousMan@facebook.com',  # 邮箱
    long_description=long_description,  # 项目的描述 读取README.md文件的信息
    long_description_content_type="text/markdown",  # 描述文档README的格式 一般md
    # url='https://github.com/your_username/my_package',  # 项目的 GitLab 地址或其他主页
    packages=find_packages(),  # Python导入包的列表 可以find_packages() 来自动收集
    keywords='kit',
    install_requires=[
        'colorlog==6.8.2',
        'PyHamcrest==2.1.0',
        'chardet==3.0.4'
    ],  # 其他依赖的约束
    license="MIT",  # 许可证
    # 这 需要去官网查，在下边提供了许可证连接 或者 你可以直接把我的粘贴走
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"],
    python_requires='>=3.10',  # Python的版本约束
)
