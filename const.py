# -*- coding: utf-8 -*-

class _const:
    class ConstError(TypeError) : pass

def __setattr__(self, key, value):
        # self.__dict__
        if self.__dict__.has_key(key):
            raise self.ConstError,"constant reassignment error!"
        self.__dict__[key] = value

import sys

sys.modules[__name__] = _const()