# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/20 17:41:44$"

import os
import logging

from file_utils import from_little_endian


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
    def __init__(self, path):
        self.path = path
        logging.info("Voice: path=%s", self.path)
        if not os.path.isfile(path):
            raise IOError()
        self.file = open(self.path, "rb")
        self._parse()
        
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
    voice = Voice("/home/rubyu/Documents/voice.bin")
    file = open("/home/rubyu/Documents/voice.bin.temp.ogg", "wb")
    file.write(voice.get("00000050"))

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)-8s %(module)-16s %(funcName)-16s@%(lineno)d - %(message)s"
    )    
    main()
