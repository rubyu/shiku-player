# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/20 17:41:44$"

import logging
import os
import sys
from optparse import OptionParser
import cPickle as _pickle

from file_utils \
    import from_little_endian
    
    
class Voice:
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
    
    _cls_ver = 0
    
    def __init__(self, path):
        self._ins_ver = self._cls_ver
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
        if self._ins_ver != self._cls_ver:
            raise ValueError() 
        self.file = open(self.path, "rb")
    
    @classmethod
    def restore_or_create(cls, path, dump):
        try:
            ins = _pickle.load(open(dump, "rb"))
            logging.debug("Voice restored from %s", dump)
        except:
            ins = cls(path)
            _pickle.dump(ins, open(dump, "wb"))
            logging.debug("Voice dumped to %s", dump)
        return ins
    
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
        
        
def main():
    #sys.argv.append("--path=/tmp/sekai/voice.bin")
    #sys.argv.append("--list")
    #sys.argv.append("--id=00000350")
    parser = OptionParser(
        "usage: script_parser.py --path=to_voice.bin --extract=voice_id --list")
    parser.add_option(
        "-p", 
        "--path",
        type="string",
        help="file path to voice.bin."
    )
    parser.add_option(
        "-i", 
        "--id",
        type="string",
        help="voice ID to extract."
    )
    parser.add_option(
        "-l", 
        "--list",
        action="store_true",
        default=False,
        help="print list of Voice ID."
    )    
    options = parser.parse_args()[0]
    
    if not options.path:
        parser.print_help()
        sys.exit(-1)
    
    voice = Voice(options.path)
    if options.list:
        for key in sorted(voice.dict.keys()):
            print key
        sys.exit()
    if options.id:
        if options.id in voice.dict:
            temp_path = os.path.join(os.path.split(options.path)[0], "%s.ogg" % options.id)
            temp = open(temp_path, "wb")
            temp.write(voice.get(options.id))
        else:
            print "Invalid Voice ID!"
        sys.exit()
        
if __name__ == "__main__":
    main()
