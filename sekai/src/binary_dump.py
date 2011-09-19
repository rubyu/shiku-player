# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/14 11:25:52$"

import sys
import codecs
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

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


def is_2byte_character(s1, s2):
    b1 = str_to_byte(s1)
    b2 = str_to_byte(s2)
    #2バイト処理
    #http://www.kanzaki.com/docs/jcode.html
    if (129 <= b1 and b1 <= 159) or (224 <= b1 and b1 <= 239):
        if (64 <= b2 and b2 <= 126) or (128 <= b2 and b2 <= 252):
            return True
    return False
                    
def is_control_character(s):
    b = str_to_byte(s)
    if 0 <= b and b <= 31:
        return True
    return False

def to_unicode(s):
    return unicode(s, "cp932", "ignore")

def pretty(s):
    if is_control_character(s):
        return u"□"
    else:
        return to_unicode(s)

def bin_decode(arr):
    if is_text(arr):
        arr = arr[2:]
    buf = []
    s1 = None
    for s2 in arr:
        if s1:
            if is_2byte_character(s1, s2):
                buf.append(to_unicode(s1+s2))
                s1 = None
                continue
            buf.append(pretty(s1))
        s1 = s2
    if s1:
        buf.append(pretty(s1))
    return "".join(buf)

def dump(filename, page_lines):
    filesize = os.path.getsize(filename)
    
    print "filename: %s" % filename
    print "size: %s(%s)" % (filesize, hex(filesize))
    
    print_header()
    
    s1 = None
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
                for s2 in buf:
                    if s1:
                        if is_2byte_character(s1, s2):
                            print to_unicode(s1+s2),
                            s1 = None
                            continue
                        print pretty(s1),
                    s1 = s2
                if s1:
                    print pretty(s1),
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
    filename = "World_preview.hcb"
    #filename = "Hoshimemo_EH.hcb"
    #filename = "_HOSHIMEM.HCB"
    dump(filename, 10)
    