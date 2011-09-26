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
            from_cp932, pretty, byte_array, search

            
class Script(Restorable):
    u"""
    「いろとりどりのセカイ」のスクリプトをパースするクラス。
    ver1.0のみ対応。ver1.1以降は修正ファイルに含まれているため。
    """
    _rest_ver = 0
    
    def __init__(self, path):
        Restorable.__init__(self)
        self.path = path
        logging.debug("Script: path=%s", self.path)
        if not os.path.isfile(path):
            raise IOError()
        
        str_arr = open(self.path, "rb").read()
        byte_arr = byte_array(str_arr)
        
        script_size = len(str_arr)
        script_end = self._end_adress(str_arr)
        if script_size < script_end:
            raise ValueError("invalid header")
        
        script_id = self._script_id(str_arr, script_end)
        self.id = script_id
        
        logging.debug("script_size: %s", script_size)
        logging.debug("script_end: %s", script_end)
        logging.debug("script_id: %s", script_id)
        
        if script_id == u"いろとりどりのセカイ":
            index = [
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
            self.chapters = []
            self.texts = []
            for i, chapter in enumerate(index):
                title = chapter[0]
                start = chapter[1]
                if i == len(index) - 1:
                    end = script_end
                else:
                    end = index[i+1][1]
                logging.debug("parsing '%s' %s - %s", title, start, end-1)
                segments = self._script_parse(str_arr, byte_arr, start, end-1)
                texts = self._segment_parse(str_arr, byte_arr, segments)
                self.texts.extend(texts)
                chapter_start = len(self.texts) - len(texts)
                chapter_end = len(self.texts) - 1
                self.chapters.append((title, chapter_start, chapter_end))
            logging.debug("done.")
            self.supported = True
        else:
            self.supported = False
    
    def __getstate__(self):
        return self.__dict__.copy()
    
    def __setstate__(self, dict):
        self.__dict__.update(dict)
            
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

    def _script_parse(self, str_arr, byte_arr, start, end):
        u"""
        シナリオファイルをかなり適当にパースし、
        命令単位？に分解する。
        アーカイブ的な構造は理解できなかったので無視してる。
        """
        segments = []
        p0 = start
        p1 = None
        while p0 <= end:
            if byte_arr[p0] == 0x01:
                # 01 XX XX
                p1 = p0 + 3
            elif byte_arr[p0] == 0x02:
                # 02 XX XX XX XX
                p1 = p0 + 5
            elif byte_arr[p0] == 0x06:
                # 06 XX XX XX XX
                p1 = p0 + 5
            elif byte_arr[p0] == 0x07:
                # 07 XX XX XX XX
                p1 = p0 + 5
            elif byte_arr[p0] == 0x0A:
                # 0A XX XX XX XX
                p1 = p0 + 5
            elif byte_arr[p0] == 0x0B:
                # 0B ... (0B|0C|02|07|08)
                # 0B .. 19
                p1 = p0
                p1 += 2 #長さ2以下の場合は無い、はず
                while p1 <= min(p0+4, end):
                    p1 += 1
                    if byte_arr[p1] == 0x0B or\
                       byte_arr[p1] == 0x0C or\
                       byte_arr[p1] == 0x02 or\
                       byte_arr[p1] == 0x07 or\
                       byte_arr[p1] == 0x08:
                        break
                    if byte_arr[p1] == 0x19:
                        p1 += 1
                        break
            elif byte_arr[p0] == 0x0C:
                # 0C ... (0B|0C|02|07|08)
                # 0C .. 19
                p1 = p0
                p1 += 1 #長さ1以下の場合は無い、はず
                while p1 <= min(p0+4, end):
                    p1 += 1
                    if byte_arr[p1] == 0x0B or\
                       byte_arr[p1] == 0x0C or\
                       byte_arr[p1] == 0x02 or\
                       byte_arr[p1] == 0x07 or\
                       byte_arr[p1] == 0x08:
                        break
                    if byte_arr[p1] == 0x19:
                        p1 += 1
                        break
            elif byte_arr[p0] == 0x0E:
                # 0E 長さ ... 00
                p1 = p0
                while p1 <= end:
                    p1 += 1
                    if byte_arr[p1] == 0x00:
                        break
                p1 += 1
            elif byte_arr[p0] == 0x0F:
                # 0F XX 00
                p1 = p0 + 3
            else:
                # *
                p1 = p0 + 1
            segments.append((p0, p1))
            p0 = p1
        return segments
    
    def _segment_parse(self, str_arr, byte_arr, segments):
        u"""
        分解した命令？から、ボイスID、キャラクタ名、テキストを抽出する。
        """
        texts = []
        for i, segment in enumerate(segments):
            p0, p1 = segment
            #print "%7s: %7s: " % (hex(p0)[2:].upper(), hex(p1-1)[2:].upper()),
            #print buf_format(str_arr[p0:p1])
            if byte_arr[p0] == 0x0E:
                text = [None] * 3
                text[0] = self._decode(str_arr[p0:p1-1])
                cid_p = segments[i-1]
                cid = byte_arr[cid_p[0]:cid_p[1]]
                cname = self._cid_to_cname(cid)
                if cname:
                    text[1] = cname
                if cname and cname != u"悠馬":
                    j = i - 1
                    while i - 5 < j:
                        j += -1
                        vid_p = segments[j]
                        tmp = byte_arr[vid_p[0]:vid_p[1]]
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
    
    def _script_id(self, file, script_end):
        u"""
        スクリプトのIDを返す。
        """
        pos = search(file, [0x00], script_end)
        s = search(file, [0x00], pos+1)
        e = search(file, [0x00], s+1)
        l = from_little_endian(file[s+1])
        id_str = file[s+2:e]
        if l != len(id_str) + 1: #長さチェック自体も含む
            logging.debug("script id length check error")
        return from_cp932(id_str)


class ScriptParserTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls._v1_0_path = "/tmp/sekai/World.hcb"
        cls._v1_0 = Script(cls._v1_0_path)
#        cls._v1_1_path = "/tmp/sekai/World.1.1.hcb"
#        cls._v1_1 = Script(cls._v1_1_path)
    def setUp(self):
        pass
    
    def test_parse(self):
        data = [
            [
                u"",
                u"……失くしたものを取り戻すそのために。",
                0, 1759,
            ],
            [
                u"目が、覚めたか？",
                u"空からたくさんの羽根が降る、いつもの夢を。",
                1760, 3129,
            ],
            [
                u"暑い……",
                u"きっと俺たちの何もかもが始まったのであろう、遠い幼きあの日のことを……。",
                3130, 4183,
            ],
            [
                u"恋をしようか",
                u"それは少し昔の夢だった。",
                4184, 6278,
            ],
            [
                u"ねえ、本当に覚えてないの、私のこと",
                u"少し昔の、俺がぼくとして生起した、あの日の夢を。",
                6279, 7867,
            ],
            [
                u"この町にはね、魔女が住んでいるんだよ",
                u"空から絶え間ない白が降り注ぐ、あの夢を。",
                7868, 8666,
            ],
            [
                u"…………",
                u"お前の明日が幸せに満ち足りているようにと、祈っている",
                8667, 9752,
            ],
            [
                u"…………",
                u"青い空から真っ白な羽根が降ってくる、いつもの夢を。",
                9753, 10651,
            ],
            [
                u"今週末は海へ遊びに行くそうです",
                u"つかさはピュアすぎる笑顔を見せた。",
                10652, 12201,
            ],
            [
                u"きっと、幸せってこう言うことを言うんですね！",
                u"……夢の中で誰かに呼ばれたような気がした。",
                12202, 13647,
            ],
            [
                u"昼休み。",
                u"かみさま、聞いてください。私の名前は……",
                13648, 15197,
            ],
            [
                u"“約束”",
                u"明日から始まる、俺たちの願いを叶える日々を、想いながら。",
                15198, 16300,
            ],
            [
                u"夢を見ている。",
                u"それは何よりも何よりも、幸せなものであればいいと、俺は願った。",
                16301, 25120,
            ],
            [
                u"……ごめんなさい。",
                u"……それはまるで、“え、ええっと……うん、ごめんね。僕もいま、思い出したんだ”と言うような、照れくさそうな声だった。",
                25121, 34492,
            ],
            [
                u"――どうして",
                u"ずっとずっと、わたしたち、ふたり一緒だよね",
                34493, 41106,
            ],
            [
                u"お兄ちゃん……",
                u"差し出されたその手を、そっと握った。",
                41107, 44492,
            ],
            [
                u"……私には。",
                u"俺たちは唇を合わせ、もう一度、身体を重ねるようと、強く抱き合った。",
                44493, 51078,
            ],
        ]
        for i, datum in enumerate(data):
            (str1, str2, chapter_start, chapter_end) = datum
            chapter = self._v1_0.chapters[i]
            self.assertEqual(chapter_start, chapter[1])
            self.assertEqual(chapter_end, chapter[2])
            self.assertEqual(str1, self._v1_0.texts[chapter_start][0])
            self.assertEqual(str2, self._v1_0.texts[chapter_end][0])


class ProcWrapper(object):
    
    def print_script(self, script_file):
        script = Script(script_file)
        if not script.id:
            print "'%s' is not hcb file." % script_file
            return
        if not script.supported:
            print "'%s' is not supported." % script.id
            return
        print script.id
        print
        for text in script.texts:
            str, name, vid = text
            if name:
                print u"%s　「%s」" % (name, str)
            else:
                print u"　%s" % str
            

from StringIO import StringIO
class ProcWrapperTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls._v1_0_path = "/tmp/sekai/World.hcb"
        cls._v1_1_path = "/tmp/sekai/World.1.1.hcb"
        cls._other_path = "/tmp/sekai/dummy.hcb"
        cls._stdout = sys.stdout
    
    @classmethod
    def terDownClass(cls):
        sys.stdout = cls._stdout
        
    def setUp(self):
        self._dummy_out = StringIO()
        sys.stdout = self._dummy_out
        self.wrapper = ProcWrapper()

    def test_print_script(self):
        self.wrapper.print_script(self._v1_0_path)
        self.assertEqual(
            u"""いろとりどりのセカイ\n"""
            u"""\n"""
            u"""　\n"""
            u"""　\n"""
            u"""　……。\n"""
            u"""　……羽根だ。\n"""
            u"""　空から羽根が降っている。\n"""
            u"""　……。\n"""
            u"""　雪""",
            self._dummy_out.getvalue()[:50]
        )

    def test_print_script_not_script_id(self):
        self.wrapper.print_script(self._v1_1_path)
        self.assertEqual(
            u"""'いろとりどりのセカイ　ver1.1' is not supported.\n""",
            self._dummy_out.getvalue()
        )
        
    def test_print_script_not_hcb(self):
        try:
            self.wrapper.print_script(self._other_path)
            self.assert_(False)
        except:
            self.assert_(True)
        

class OptionParserTestCase(unittest.TestCase):
    
    
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
        help="file path to World.hcb(ver=1.0)"
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
