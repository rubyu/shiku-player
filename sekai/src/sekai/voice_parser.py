# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/20 17:41:44$"

import unittest
import logging
import os
import sys

from restorable \
    import Restorable
from file_utils \
    import from_little_endian
    
    
class Voice(Restorable):
    u"""
    ボイスデータのパーサ。
    データは普通のoggファイル。
    
    フォーマットは以下。
    
    4  byte [エントリ数]
    4  byte [ファイル名辞書長]
    12 byte [ [ファイル名オフセット][データアドレス][データ長] ]
        x エントリ数
    (8 + 12 * エントリ数)
    〜ファイル名辞書〜 
    (8 + 12 * エントリ数 + ファイル名辞書長)
    〜データ〜
    EOF
    """
    
    _rest_ver = 0
    
    def __init__(self, path):
        Restorable.__init__(self)
        self.path = path
        logging.debug("Voice: path=%s", self.path)
        if not os.path.isfile(path):
            raise IOError()
        self.file = open(self.path, "rb")
        self._parse()
    
    def __getstate__(self):
        dict = self.__dict__.copy()
        del dict["file"]
        return dict
    
    def __setstate__(self, dict):
        self.__dict__.update(dict)
    
    def _restore_after(self):
        self.file = open(self.path, "rb")
    
    def _read_int(self):
        return from_little_endian(self.file.read(4))
    
    def _read_str(self, n):
        return self.file.read(n)
    
    def _parse(self):
        self.file.seek(0)
        number_of_entries = self._read_int()
        dict_length = self._read_int()
        logging.debug("number of entries: %s", number_of_entries)
        logging.debug("dict length: %s", dict_length)
        
        entries = []
        for i in xrange(number_of_entries):
            dict_offset = self._read_int()
            adress = self._read_int()
            length = self._read_int()
            entries.append((dict_offset, adress, length))
        
        dict_adress = 8 + number_of_entries * 12
        data_adress = dict_adress + dict_length
        logging.debug("dict adress: %s", dict_adress)
        logging.debug("data adress: %s", data_adress)
        
        dict = {}
        for i in xrange(number_of_entries):
            self.file.seek(dict_adress + entries[i][0])
            if i == number_of_entries - 1:
                length = data_adress - dict_adress - entries[i][0] - 1
            else:
                length = entries[i+1][0] - entries[i][0] - 1
            name = self._read_str(length)
            dict[name] = (entries[i][1], entries[i][2])
        self.dict = dict
        
    def get(self, id):
        if id in self.dict:
            entry = self.dict[id]
            adress, length = entry
            self.file.seek(adress)
            logging.info("get: %s adress=%s length=%s", id, adress, length)
            return self._read_str(length)
        raise KeyError()


class ProcWrapper(object):
    
    def print_list(self, voice_file):
        voice = Voice(voice_file)
        for key in sorted(voice.dict.keys()):
            print key
            
    def output_voice(self, voice_file, extract_dir, voice_id):
        voice = Voice(voice_file)
        if voice_id in voice.dict:
            temp_path = os.path.join(extract_dir, "%s.ogg" % voice_id)
            temp = open(temp_path, "wb")
            temp.write(voice.get(options.id))
        else:
            print "%s is invalid Voice ID!" % voice_id
        
        
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
        cls._path = "/tmp/sekai/voice.bin"
        cls._extract = "/tmp/sekai/voice_test"
        cls._id = "00000350"
        cls._argv = sys.argv
    
    @classmethod
    def terDownClass(cls):
        sys.argv = cls._argv
    
    def setUp(self):
        self._wrapper = self.DummyProcWrapper()
        sys.argv = [self._argv[0]]
        
    def test_list(self):
        sys.argv.append("--list")
        parse(self._wrapper)
        self.assertEqual([], self._wrapper._log)
        
    def test_path_list(self):
        sys.argv.append("--path=%s" % self._path)
        sys.argv.append("--list")
        parse(self._wrapper)
        self.assertEqual(["print_list"], self._wrapper._log)
        
    def test_extract(self):
        sys.argv.append("--extract=%s" % self._extract)
        parse(self._wrapper)
        self.assertEqual([], self._wrapper._log)
        
    def test_path_extract(self):
        sys.argv.append("--path=%s" % self._path)
        sys.argv.append("--extract=%s" % self._extract)
        parse(self._wrapper)
        self.assertEqual([], self._wrapper._log)
        
    def test_path_extract_id(self):
        sys.argv.append("--path=%s" % self._path)
        sys.argv.append("--extract=%s" % self._extract)
        sys.argv.append("--id=%s" % self._id)
        parse(self._wrapper)
        self.assertEqual(["output_voice"], self._wrapper._log)

def parser():
    from optparse import OptionParser
    p = OptionParser(
        "usage: script_parser.py --path=to_voice.bin --list --extract=output_directory --id=voice_id")
    p.add_option(
        "-p", 
        "--path",
        type="string",
        help="file path to voice.bin"
    )
    p.add_option(
        "-e", 
        "--extract",
        type="string",
        help="directory path to extract voice file"
    )
    p.add_option(
        "-i", 
        "--id",
        type="string",
        help="voice ID to extract"
    )
    p.add_option(
        "-l", 
        "--list",
        action="store_true",
        default=False,
        help="print list of Voice ID"
    )
    return p

def parse(wrapper):
    p = parser()
    options, args = p.parse_args()
    if options.path:
        if options.extract:
            if options.id:
                wrapper.output_voice(options.path, options.extract, options.id)
        elif options.list:
            wrapper.print_list(options.path)
        return
    if not debug:
        p.print_help()
    
if __name__ == "__main__":
    debug = False
#    debug = True
    
    if debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)-8s %(module)-16s %(funcName)-16s@%(lineno)d - %(message)s"
        )
        unittest.main()
    else:
        parse(ProcWrapper())