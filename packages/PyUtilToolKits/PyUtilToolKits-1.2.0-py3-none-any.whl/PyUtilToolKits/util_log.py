# -*- coding:utf-8 -*-
"""
@Time        : 2023/3/2
@File        : util_log.py
@Author      : MysteriousMan
@version     : python 3
@Description : 日志
"""

import logging
import time
from colorlog import ColoredFormatter


class AutoLog:
    """
    通用日志
    """

    def __init__(self, filename, level_param):
        """
        初始化
        :param filename: 文件路径
        :param level_param: 打印级别 INFO WARNING ERROR CRITICAL
        """
        self.filename = f"{filename}-{time.strftime('%Y-%m-%d', time.localtime())}.log"  # 文件路径+日期
        self.level_param = level_param

    def log(self, message=""):
        logger = logging.getLogger(__name__)
        try:
            formatter = ColoredFormatter(  # 设置颜色&格式
                "%(log_color)s[%(levelname)s][%(asctime)s] %(message)s", datefmt=None, reset=True,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'black,bg_white'
                }
            )
            ch = logging.StreamHandler()  # 创建控制台
            ch.setFormatter(formatter)  # 对文件格式
            logger.addHandler(ch)  # 控制台句柄加入logger

            fh = logging.FileHandler(filename=self.filename, encoding="utf-8")  # 创建文件
            fh.setFormatter(logging.Formatter('[%(levelname)s][%(asctime)s]\t%(message)s'))  # 对文件格式
            logger.addHandler(fh)  # 文件句柄加入logger

            logger.setLevel(level=logging.INFO)  # 设置打印级别

            if self.level_param == 'DEBUG':
                logger.debug(message)
            elif self.level_param == 'INFO':
                logger.info(message)
            elif self.level_param == 'ERROR':
                logger.error(message)
            elif self.level_param == 'WARNING':
                logger.warning(message)
            elif self.level_param == 'CRITICAL':
                logger.critical(message)

            logger.removeHandler(fh)  # 删除文件句柄
            logger.removeHandler(ch)  # 移除控制台对象
            logging.shutdown()

        except:
            print('file exception')
        # finally:
        # fh.close()
        # kill_process_using_file(file_path)


if __name__ == '__main__':
    pass
    # Info = AutoLog(f"\\message_log\\info", level_param='INFO')
    # Warn = AutoLog(f"\\message_log\\warn", level_param='WARNING')
    # Error = AutoLog(f"\\message_log\\error", level_param='ERROR')
    # Critical = AutoLog(f"\\message_log\\critical", level_param='CRITICAL')
