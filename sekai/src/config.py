# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/26 18:21:43$"

from sekai.restorable \
    import Restorable
    
    
class Config(Restorable):
    
    _rest_ver = 0
    
    def __init__(self):
        Restorable.__init__(self)
    
        