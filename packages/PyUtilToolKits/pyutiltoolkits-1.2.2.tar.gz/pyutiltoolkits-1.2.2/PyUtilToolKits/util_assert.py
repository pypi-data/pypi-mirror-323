# -*- coding:utf-8 -*-
"""
@Time        : 2023/3/2
@File        : util_assert.py
@Author      : MysteriousMan
@version     : python 3
@Description : 断言
"""

from hamcrest import *


def assert_db(actual):
    """
    断言匹配对象不为()
    :param actual:
    :return:
    """
    assert_that(actual, is_not(()), reason="reason was 'Expected value is not none!'")


def assert_not_none(actual, url=None):
    """
    断言匹配对象不为空
    :param actual: 真实值
    :param url: 地址
    :return:
    """
    assert_that(actual, is_not(None), reason=f"url was '{url}'\nreason was 'Expected value is not none!'")


def assert_equals(actual, expect=None, url=None, info=None):
    """
    断言匹配相等对象
    :param actual: 真实值
    :param expect: 期望值
    :param url: 地址
    :param info: 断言结果日志记录对象(obj)
    :return:相等则不抛出异常，不相等则抛出异常
    """
    if expect:
        assert_that(
            actual, equal_to(expect),
            reason=f"url was '{url}'\nreason was 'Expected value is not equal to the actual value!'"
        )
        mes = "接口断言成功, 符合预期结果"
        mes = f"{mes} {url}\n" if url else f"{mes}\n"
        info.log(mes) if info else print(mes)
    else:
        pass


def assert_containString(actual, expect=None, url=None, info=None):
    """
    断言匹配字符串的一部分
    :param actual: 真实值
    :param expect: 期望值
    :param url: 地址
    :param info: 断言结果日志记录对象(obj)
    :return: 返回状态 True None
    :url
    """
    if expect:
        assert_that(
            actual, contains_string(str(expect)),
            reason=f"断言失败原因: '实际结果与期望结果不同!' \nurl was {url}"
        )
        mes = "接口断言成功, 符合预期结果"
        mes = f"{mes} {url}\n" if url else f"{mes}\n"
        info.log(mes) if info else print(mes)
        return True
    else:
        info.log(f"未进行接口返回断言!") if info else None
        return None


def assert_less(actual, expect=None, url=None, info=None):
    """
    断言数字小于预期
    :param actual: 真实值
    :param expect: 期望值
    :param url: 地址
    :param info: 断言结果日志记录对象(obj)
    :return:
    """
    if expect:
        assert_that(
            actual, less_than(expect),
            reason=f"url was '{url}'\nreason was 'Actual value is greater than or equal to the expected value!'"
        )
        mes = "接口断言成功, 符合预期结果"
        mes = f"{mes} {url}\n" if url else f"{mes}\n"
        info.log(mes) if info else print(mes)
    else:
        pass


if __name__ == '__main__':
    print(assert_containString(actual='123', expect='3'))

