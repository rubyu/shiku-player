# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/26 15:42:24$"

import unittest
import logging
import cPickle as _pickle
        
        
class Restorable(object):
    u"""
    pickleに依存したsave/restoreを実装するクラス。
    継承クラスは
    
        ・_rest_id
            変数。
            データの正当性の判断などに使う。
            
        ・_rest_ver
            変数。
            データのバージョニングなどに使う。
            
        ・__setstate__
            関数。
            pickleが使う。
            
            ・データのIDが、新しいクラスで変更されている場合
            ・データのバージョンが、新しいクラスで変更されている場合
            は、ここでバージョン移行処理を行う。
            
        ・__getstate__
            関数。
            pickleが使う。
            
    を実装して動作をカスタマイズできる。
    """
    
    def __init__(self):
        self._ins_rest_id = self._cls_rest_id()
        self._ins_rest_ver = self._cls_rest_ver()
        logging.debug("Restorable(id=%s, ver=%s) created", 
            self._ins_rest_id, self._ins_rest_ver)
    
    def _cls_rest_id(self):
        if not hasattr(self, "_rest_id"):
            return self.__class__.__name__
        return self._rest_id
    
    def _cls_rest_ver(self):
        if not hasattr(self, "_rest_ver"):
            return 0
        return self._rest_ver
    
    @classmethod
    def restore(cls, path):
        ins = _pickle.load(open(path, "rb"))
        ins._check_rest_id()
        ins._check_rest_ver()
        logging.debug("Restorable(id=%s, ver=%s) restored from %s", 
            ins._ins_rest_id, ins._ins_rest_ver, path)
        return ins
    
    def _check_rest_id(self):
        if self._ins_rest_id != self._cls_rest_id():
            raise ValueError("Restorable ID mismatch! %s != %s" % 
                (self._ins_rest_id, self._cls_rest_id()))
                
    def _check_rest_ver(self):
        if self._ins_rest_ver != self._cls_rest_ver():
            raise ValueError("Restorable Version mismatch! %s != %s" % 
                (self._ins_rest_ver, self._cls_rest_ver()))
    
    def save(self, path):
        _pickle.dump(self, open(path, "wb"))
        logging.debug("Restorable(id=%s, ver=%s) saved to %s", 
            self._ins_rest_id, self._ins_rest_ver, path)
    

class Suc1(Restorable):

    def __init__(self):
        Restorable.__init__(self)


class Suc2(Restorable):

    _rest_id = "hoge"
    _rest_ver = 1

    def __init__(self):
        Restorable.__init__(self)
        
        
class ScriptTestCase(unittest.TestCase):
    
    temp_store = "/tmp/restorable"
    
    def setUp(self):
        u"""
        temp_storeの中身を削除する。
        """
        if os.path.exists(self.temp_store) and \
           os.path.isdir(self.temp_store):
            shutil.rmtree(self.temp_store)
        os.makedirs(self.temp_store)
        
    def test_default_rest_id_and_rest_ver(self):
        u"""
        Restorableの子クラスが、_rest_id、_rest_verを持たない場合、
        _ins_rest_id、_ins_rest_verはデフォルトが適用される。
        """
        suc = Suc1()
        self.assertEqual(suc.__class__.__name__, suc._ins_rest_id)
        self.assertEqual(0, suc._ins_rest_ver)
        
    def test_overwrite_rest_id_and_rest_ver(self):
        u"""
        Restorableの子クラスが、_rest_id、_rest_verを持つ場合、
        _ins_rest_id、_ins_rest_verは設定値が適用される。
        """
        suc = Suc2()
        self.assertEqual("hoge", suc._ins_rest_id)
        self.assertEqual(1, suc._ins_rest_ver)
            

if __name__ == "__main__":
    import os
    import shutil
    
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)-8s %(module)-16s %(funcName)-16s@%(lineno)d - %(message)s"
    )
    
    unittest.main()
