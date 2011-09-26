# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/26 15:42:24$"

import unittest
import logging
import types
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
        ・_restore_after
            関数。
            restore後に呼ばれる。
        ・_save_before
            関数。
            save前に呼ばれる。
        ・__setstate__
            関数。
            pickleが使う。
        ・__getstate__
            関数。
            pickleが使う。
    を実装して動作をカスタマイズできる。
    """
    
    def __init__(self):
        logging.debug("Create")
        self._ins_rest_id = self._cls_rest_id()
        self._ins_rest_ver = self._cls_rest_ver()
        logging.debug("Created %s(ver=%s)", self._ins_rest_id, self._ins_rest_ver)
    
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
        logging.debug("Restore")
        ins = _pickle.load(open(path, "rb"))
        if hasattr(ins, "_restore_after") and \
           type(ins._restore_after) is types.MethodType:
            logging.debug("Call _restore_after of %s", ins)
            ins._restore_after()
        logging.debug("Restored %s(ver=%s) from %s", ins._ins_rest_id, ins._ins_rest_ver, path)
        return ins
    
    def save(self, path):
        logging.debug("Save")
        if hasattr(self, "_save_before") and \
           type(self._save_before) is types.MethodType:
            logging.debug("Call _save_before of %s", self)
            self._save_before()
        _pickle.dump(self, open(path, "wb"))
        logging.debug("Saved %s(ver=%s) to %s", self._ins_rest_id, self._ins_rest_ver, path)
    

class Suc1(Restorable):

    def __init__(self):
        Restorable.__init__(self)


class Suc2(Restorable):

    _rest_id = "hoge"
    _rest_ver = 1

    def __init__(self):
        Restorable.__init__(self)
        

class Suc3(Restorable):

    def __init__(self):
        Restorable.__init__(self)

    def _restore_after(self):
        self._restore_after_called = True


class Suc4(Restorable):

    def __init__(self):
        Restorable.__init__(self)

    def _save_before(self):
        self._save_before_called = True
        
        
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
            
    def test_restore_after(self):
        u"""
        Restorableの子クラスが、restoreされるとき、
        _restore_afterを持っていれば、restore後に、それがコールされる。
        """        
        suc = Suc3()
        self.assert_(not hasattr(suc, "_restore_after_called"))
        suc.save(os.path.join(self.temp_store, "test"))
        suc = Suc3.restore(os.path.join(self.temp_store, "test"))
        self.assert_(suc._restore_after_called)

    def test_save_before(self):
        u"""
        Restorableの子クラスが、saveされるとき、
        _save_beforeを持っていれば、save前に、それがコールされる。
        """        
        suc = Suc4()
        self.assert_(not hasattr(suc, "_save_before_called"))
        suc.save(os.path.join(self.temp_store, "test"))
        self.assert_(suc._save_before_called)
        suc = Suc3.restore(os.path.join(self.temp_store, "test"))
        self.assert_(suc._save_before_called)


if __name__ == "__main__":
    import os
    import shutil
    
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)-8s %(module)-16s %(funcName)-16s@%(lineno)d - %(message)s"
    )
    
    unittest.main()