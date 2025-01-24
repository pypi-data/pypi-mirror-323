# -*- coding: utf-8 -*-
# @Author: maoyongfan
# @email: maoyongfan@163.com
# @Date: 2025/1/6 17:32

class GetErr(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class BadValue(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
