# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/20 21:01:15$"

import unittest
import logging
import os
import sys

from restorable \
    import Restorable
from file_utils \
    import from_little_endian, byte_int, is_cp932_2byte_char, \
            from_cp932, pretty, byte_array

            
class Script(Restorable):
    
    _rest_ver = 0
    
    def __init__(self, path):
        Restorable.__init__(self)
        self.path = path
        logging.debug("Script: path=%s", self.path)
        if not os.path.isfile(path):
            raise IOError()
        str_arr = open(self.path, "rb").read()
        byte_arr = byte_array(str_arr)
        script_end = self._end_adress(str_arr)
        logging.debug("filesize: %s", len(str_arr))
        logging.debug("script_end: %s", script_end)
        chapters = [
            [ u"共通ルート１章",       0x0731FC, ],
            [ u"共通ルート２章",       0x091C41, ],
            [ u"共通ルート３章",       0x0AA8B4, ],
            [ u"共通ルート４章",       0x0C048E, ],
            [ u"共通ルート５章",       0x0E8189, ],
            [ u"共通ルート６章",       0x105645, ],
            [ u"共通ルート７章",       0x11390C, ],
            [ u"共通ルート８章",       0x126977, ],
            [ u"共通ルート９章",       0x138CB3, ],
            [ u"共通ルート１０章",     0x1559B5, ],
            [ u"共通ルート１１章",     0x16D29E, ],
            [ u"共通ルート１２章",     0x188423, ],
            [ u"ヒロインルート真紅",   0x19ACA8, ],
            [ u"ヒロインルート加奈",   0x23A3DF, ],
            [ u"ヒロインルート澪",     0x2E845E, ],
            [ u"ヒロインルート鏡",     0x35DD8A, ],
            [ u"ヒロインルートつかさ", 0x3995F6, ],
        ]
        self.titles = []
        self.texts = {}
        for i, chapter in enumerate(chapters):
            title = chapter[0]
            start = chapter[1]
            if i == len(chapters) - 1:
                end = script_end
            else:
                end = chapters[i+1][1]
            logging.debug("parsing '%s' %s - %s", title, start, end-1)
            self.titles.append(title)
            self.texts[title] = self._parse(str_arr, byte_arr, start, end-1)
        logging.debug("done.")
    
    def __getstate__(self):
        return self.__dict__.copy()
    
    def __setstate__(self, dict):
        self.__dict__.update(dict)
            
    def _restore_after(self):
        if self._ins_rest_id != self._cls_rest_id():
            raise ValueError("Restorable ID mismatch! %s != %s", 
                self._ins_rest_id, self._cls_rest_id())
        
        if self._ins_rest_ver != self._cls_rest_ver():
            raise ValueError("Restorable Version mismatch! %s != %s", 
                self._ins_rest_ver, self._cls_rest_ver())
                
    def _is_text(self, arr):
        u"""
        シナリオファイル内の、正しい文字列パターンであればTrueを返す。
        ・先頭バイト
        ・2バイト目が文字列パターンの長さを表しているか
        をチェックする。
        """
        if 2 <= len(arr):
            if 0x0E == byte_int(arr[0]) and byte_int(arr[1]) == len(arr) - 1:
                return True
        return False

    def _decode(self, arr):
        u"""
        シナリオファイル内に出現する 0x0E 長さ ~ 0x00 の文字列パターンをデコードする。
        文字コードはcp932と解釈。
        """
        if not self._is_text(arr):
            raise ValueError("invalid text")
        buf = []
        s1 = None
        for i in xrange(2, len(arr)):
            s2 = arr[i]
            if s1:
                if is_cp932_2byte_char(s1, s2):
                    buf.append(from_cp932(s1+s2))
                    s1 = None
                    continue
                buf.append(from_cp932(pretty(s1, u"□")))
            s1 = s2
        if s1:
            buf.append(from_cp932(pretty(s1, u"□")))
        return "".join(buf)

    def _parse(self, str_arr, bin_arr, start, end):
        u"""
        シナリオファイルをかなり適当にパースし、
        ボイスID、キャラクタ名、テキストを抽出する。
        アーカイブ的な構造は理解できなかったので無視してる。
        """
        texts = []
        segments = []
        p0 = start
        p1 = None
        while p0 <= end:
            if bin_arr[p0] == 0x01:
                # 01 XX XX
                p1 = p0 + 3
            elif bin_arr[p0] == 0x02:
                # 02 XX XX XX XX
                p1 = p0 + 5
            elif bin_arr[p0] == 0x06:
                # 06 XX XX XX XX
                p1 = p0 + 5
            elif bin_arr[p0] == 0x07:
                # 07 XX XX XX XX
                p1 = p0 + 5
            elif bin_arr[p0] == 0x0A:
                # 0A XX XX XX XX
                p1 = p0 + 5
            elif bin_arr[p0] == 0x0B:
                # 0B ... (0B|0C|02|07|08)
                # 0B .. 19
                p1 = p0
                p1 += 2 #長さ2以下の場合は無い、はず
                while p1 <= min(p0+4, end):
                    p1 += 1
                    if bin_arr[p1] == 0x0B or\
                       bin_arr[p1] == 0x0C or\
                       bin_arr[p1] == 0x02 or\
                       bin_arr[p1] == 0x07 or\
                       bin_arr[p1] == 0x08:
                        break
                    if bin_arr[p1] == 0x19:
                        p1 += 1
                        break
            elif bin_arr[p0] == 0x0C:
                # 0C ... (0B|0C|02|07|08)
                # 0C .. 19
                p1 = p0
                p1 += 1 #長さ1以下の場合は無い、はず
                while p1 <= min(p0+4, end):
                    p1 += 1
                    if bin_arr[p1] == 0x0B or\
                       bin_arr[p1] == 0x0C or\
                       bin_arr[p1] == 0x02 or\
                       bin_arr[p1] == 0x07 or\
                       bin_arr[p1] == 0x08:
                        break
                    if bin_arr[p1] == 0x19:
                        p1 += 1
                        break
            elif bin_arr[p0] == 0x0E:
                # 0E 長さ ... 00
                p1 = p0
                while p1 <= end:
                    p1 += 1
                    if bin_arr[p1] == 0x00:
                        break
                p1 += 1
            elif bin_arr[p0] == 0x0F:
                # 0F XX 00
                p1 = p0 + 3
            else:
                # *
                p1 = p0 + 1
            segments.append((p0, p1))
            p0 = p1

        for i, segment in enumerate(segments):
            p0, p1 = segment
            #print "%7s: %7s: " % (hex(p0)[2:].upper(), hex(p1-1)[2:].upper()),
            #print buf_format(str_arr[p0:p1])
            if bin_arr[p0] == 0x0E:
                text = [None] * 3
                text[0] = self._decode(str_arr[p0:p1-1])
                cid_p = segments[i-1]
                cid = bin_arr[cid_p[0]:cid_p[1]]
                cname = self._cid_to_cname(cid)
                if cname:
                    text[1] = cname
                if cname and cname != u"悠馬":
                    j = i - 1
                    while i - 5 < j:
                        j += -1
                        vid_p = segments[j]
                        tmp = bin_arr[vid_p[0]:vid_p[1]]
                        if tmp == [0x08] or \
                           (0x0C == tmp[0] and tmp[1] < 0x0A):
                            continue
                        #vidは整数をゼロでパディングした長さ8の文字列
                        vid = str_arr[vid_p[0]:vid_p[1]]
                        vid = from_little_endian(vid[1:])
                        vid = ("00000000%s" % vid)[-8:]
                        text[2] = vid
                        break
                    if not text[2]:
                        logging.warning(
                            "voice id related to '%s' was not found", text[0])
                texts.append(text)
        return texts

    def _cid_to_cname(self, cid):
        u"""
        キャラクターの識別子に合致していれば、対応するキャラクター名を返す。
        対応するものがなければ""を返す。
        """
        if cid == [0x02, 0x04, 0x00, 0x00, 0x00]:
            return u"真紅"
        if cid == [0x02, 0x3D, 0x13, 0x00, 0x00]:
            return u"悠馬"
        if cid == [0x02, 0xC3, 0x0D, 0x00, 0x00]:
            return u"時雨"
        if cid == [0x02, 0x24, 0x01, 0x00, 0x00]:
            return u"加奈"
        if cid == [0x02, 0xDB, 0x07, 0x00, 0x00]:
            return u"蓮"
        if cid == [0x02, 0x00, 0x0C, 0x00, 0x00]:
            return u"あゆむ"
        if cid == [0x02, 0x32, 0x03, 0x00, 0x00]:
            return u"澪"
        if cid == [0x02, 0x05, 0x05, 0x00, 0x00]:
            return u"鏡"
        if cid == [0x02, 0x01, 0x0A, 0x00, 0x00]:
            return u"鈴"
        if cid == [0x02, 0x45, 0x06, 0x00, 0x00]:
            return u"つかさ"
        if cid == [0x02, 0x25, 0x11, 0x00, 0x00]:
            return u"お母さん"
        if cid == [0x02, 0xEE, 0x08, 0x00, 0x00]:
            return u"白"
        if cid == [0x02, 0xF5, 0x04, 0x00, 0x00]:
            return u"澪　&　悠馬"
        if cid == [0x02, 0xE1, 0x0E, 0x00, 0x00]:
            return u"担任教師"
        if cid == [0x02, 0x17, 0x12, 0x00, 0x00]:
            return u"祟り"
        if cid == [0x02, 0x37, 0x0F, 0x00, 0x00]:
            return u"女の子"
        if cid == [0x02, 0x9E, 0x11, 0x00, 0x00]:
            return u"藍"
        if cid == [0x02, 0xB0, 0x0F, 0x00, 0x00]:
            return u"祖母"
        if cid == [0x02, 0xC4, 0x12, 0x00, 0x00]:
            return u"蓮也"
        if cid == [0x02, 0x29, 0x10, 0x00, 0x00]:
            return u"とおる"

        if 5 == len(cid) and \
           0x02 == cid[0] and \
           cid[2] < 0x20 and \
           0x00 == cid[3] and \
           0x00 == cid[4]:
            logging.warning(
                "Maybe '%s' is a valid character id, but not defined in cid table", cid)
            
        return ""

    def _end_adress(self, file):
        u"""
        ファイルの先頭をチェックして、終了位置を返す。
        """
        return from_little_endian(file[:3])


class ProcWrapper(object):
    
    def print_script(self, script_file):
        script = Script(script_file)
        for title in script.titles:
            for text in script.texts[title]:
                str, name, vid = text
                if name:
                    print u"%s「%s」" % (name, str)
                else:
                    print str
            

class ParserTestCase(unittest.TestCase):
    
    
    class DummyProcWrapper(object):

        def __init__(self):
            self._log = []

        def __getattr__(self, name):
            def _dummy(self, *args, **kwargs):
                pass
            self._log.append(name)
            return _dummy    
        
        
    @classmethod
    def setUpClass(cls):
        cls._path = "/tmp/sekai/World.hcb"
        cls._argv = sys.argv
    
    @classmethod
    def terDownClass(cls):
        sys.argv = cls._argv
        
    def setUp(self):
        self._wrapper = self.DummyProcWrapper()
        sys.argv = [self._argv[0]]
        
    def test_path(self):
        sys.argv.append("--path=%s" % self._path)
        parse(self._wrapper)
        self.assertEqual(["print_script"], self._wrapper._log)
        

def parser():
    from optparse import OptionParser
    p = OptionParser("usage: script_parser.py --path=to_World.hcb")
    p.add_option(
        "-p", 
        "--path",
        type="string",
        help="file path to World.hcb"
    )
    return p

def parse(wrapper):
    p = parser()
    options, args = p.parse_args()
    if options.path:
        wrapper.print_script(options.path)
        return
    if not debug:
        p.print_help()
    
if __name__ == "__main__":
    debug = False
#    debug = True
    
    import sys
    import codecs
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
    
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)-8s %(module)-16s %(funcName)-16s@%(lineno)d - %(message)s"
        )
        unittest.main()
    else:
        parse(ProcWrapper())
