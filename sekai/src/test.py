# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/21 14:07:07$"

import unittest
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s %(module)-16s %(funcName)-16s@%(lineno)d - %(message)s"
)
from voice_parser import Voice
from script_parser import Script
from defs \
    import VOICE_FILE, SCRIPT_FILE

voice = Voice(VOICE_FILE)
script = Script(SCRIPT_FILE)


class ScriptTestCase(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_talk_has_valid_vid(self):
        u"""
        テキストにvoice idが付加されている場合、そのvoice idは必ず
        正しい（voiceにインデックスが存在する）ものでなければならない。
        """
        vids = set(voice.dict.keys())
        missed = set()
        for title in script.titles:
            for text in script.texts[title]:
                str, cname, vid = text
                if not vid:
                    continue
                if vid not in vids:
                    missed.add(vid)
        self.assertEqual(0, len(missed)) 
    
    def test_talk_has_vid(self):
        u"""
        テキストに発言者（悠馬以外）が付加されている場合、そのテキストには
        voice idが付加されていなければならない。
        """
        missed = set()
        for title in script.titles:
            for text in script.texts[title]:
                str, cname, vid = text
                if cname and \
                   cname != u"悠馬" and \
                   not vid:
                    missed.add(text)
        self.assertEqual(0, len(missed))
    
    
class VoiceTestCase(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_vid_has_talk(self):
        u"""
        voiceにインデックスが存在する全てのvoice idが、いずれかのテキストに
        結び付けられていなければならない　…　これは正しくない。
        
        ・使用されていない（ボツ？）voice id
        が存在するため。
        """
        self.assert_(True)
    
    
if __name__ == "__main__":
    unittest.main()
