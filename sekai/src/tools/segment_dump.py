# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/14 11:25:52$"

import sys
import codecs
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

import os
import struct

def int_to_hex(i):
    return ("0" + hex(i)[2:].upper())[-2:]

def str_to_byte(s):
    b = struct.unpack("B", s)
    if 1 != len(b):
        raise "1 != len(b)"
    return b[0]

def is_text(arr):
    if 2 <= len(arr):
        if 0x0E == str_to_byte(arr[0]) and str_to_byte(arr[1]) == len(arr) - 1:
            return True
    return False

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

def segment_label(buf, arr, hash):
    if 0 == len(buf):
        return "NULL"
    if is_text(buf):
        return "text"
#    labels = {
#        "08080204" : u"sinku ID",
#        "0808023203" : u"mio ID",
#        "0808080808023D13" : u"yuuma ID",
#        "0808022401": u"kana ID",
#        "0808020505": u"kagami ID",
#        "080802C30D": u"sigure ID",
#        "08080802786303" : u"?click after 1",
#        "02597203" : u"?click after 2",
#        
#    }
#    if hash in labels:
#        return labels[hash]
#    
#    if 20 <= len(hash):
#        if "08080808080808080802" == hash[:20]:
#            return "?chara pic"
#    
#    if 1 <= len(arr) and "0A" == arr[0]:
#        return "voice"
    return ""

def dump(filename):
    filesize = os.path.getsize(filename)
    
    print "filename: %s" % filename
    print "size: %s(%s)" % (filesize, hex(filesize))
    
    segment = []
    segment_index = []
    segment_end = None
    buf = []
    pos = -1
    for line in open(filename, "rb"):
        for s in line:
            pos += 1
            b = str_to_byte(s)
            if 0 != b:
                buf.append(s)
                continue
                
            segment.append(buf)
            if segment_end:
                segment_index.append(segment_end + 1)
            else:
                segment_index.append(0)
            segment_end = pos    
            buf = []
    
    print "segments: %s" % len(segment)
    print 
    
    unique = {}
    unique_order = 0
    for i, buf in enumerate(segment):
        index = segment_index[i]
        arr = [int_to_hex(str_to_byte(s)) for s in buf]
        hash = "".join(arr)
        if hash not in unique:
            unique[hash] = unique_order
            unique_order += 1
        label = segment_label(buf, arr, hash)
        print "%10d: %8s: %6d: %15s: %s | %s" % (
            index, hex(index)[2:].upper(), unique[hash], label.encode("utf-8"),
            " ".join(arr), bin_decode(buf)
            )
    
if __name__ == "__main__":    
    filename = "/tmp/sekai/World.hcb"
    filename = "/tmp/sekai/World.1.1.hcb"
    #filename = /tmp/sekai/"World_preview.hcb"
    dump(filename)
    
    
    