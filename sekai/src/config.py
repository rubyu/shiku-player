# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/26 18:21:43$"

from sekai.restorable \
    import Restorable
    
    
class Config(Restorable):
    
    _rest_ver = 0
    
    def __init__(self):
        Restorable.__init__(self)
    
    def _restore_after(self):
        if self._ins_rest_id != self._cls_rest_id():
            raise ValueError("Restorable ID mismatch! %s != %s", 
                self._ins_rest_id, self._cls_rest_id())
        
        if self._ins_rest_ver != self._cls_rest_ver():
            raise ValueError("Restorable Version mismatch! %s != %s", 
                self._ins_rest_ver, self._cls_rest_ver())
        