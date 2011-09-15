# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/14 11:25:52$"

import os
import struct

def print_hr():
    print "-- " * 16

def print_header():
    print_hr()
    for i in xrange(16):
        print int_to_hex(i),
    print
    print_hr()


def int_to_hex(i):
    return ("0" + hex(i)[2:].upper())[-2:]

def str_to_byte(s):
    b = struct.unpack("B", s)
    if 1 != len(b):
        raise "1 != len(b)"
    return b[0]

def dump(filename, page_lines):
    filesize = os.path.getsize(filename)
    
    print "filename: %s" % filename
    print "size: %s(%s)" % (filesize, hex(filesize))
    
    print_header()
    
    last = None
    buf = []
    pos = -1
    vl = -1
    for line in open(filename, "rb"):
        for s in line:
            pos += 1
            buf.append(s)
            print int_to_hex(str_to_byte(s)),
            if ( 0 != pos and 0 == (pos+1) % 16 ) or pos == filesize - 1:
                print "|",
                for s in buf:
                    if last:
                        lb = str_to_byte(last)
                        b = str_to_byte(s)
                        #制御文字は潰す
                        if 0 <= lb and lb <= 31:
                            print "□",
                            last = s
                            continue
                        #2バイト目ならばまとめる
                        if 81 <= lb:
                            if (64 <= b and b <= 126) or (128 <= b and b <= 252):
                                print unicode(last+s, "cp932", "ignore").encode("utf-8"),
                                last = None
                                continue
                        print unicode(last, "cp932", "ignore").encode("utf-8"),
                    last = s
                print "|"
                buf = []
                vl += 1
                if 0 != vl and 0 == (vl+1) % page_lines:
                    page = (vl+1) / page_lines
                    vl_e = 16 * page_lines * page - 1
                    vl_s = 16 * page_lines * (page - 1)
                    print "%s(%s)" % (vl_s, hex(vl_s)),
                    print "-",
                    print "%s(%s)" % (vl_e, hex(vl_e)),
                    print
    
if __name__ == "__main__":    
    filename = "World.hcb"
    #filename = "Hoshimemo_EH.hcb"
    #filename = "_HOSHIMEM.HCB"
    dump(filename, 10)
    