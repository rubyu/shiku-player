# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/14 11:25:52$"

import sys
import codecs
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

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

def decode(arr):
    if not is_text(arr):
        raise "invalid text"        
    buf = []
    last = None
    for i in xrange(2, len(arr)):
        s = arr[i]
        if last:
            lb = str_to_byte(last)
            b = str_to_byte(s)
            #制御文字は潰す
            if 0 <= lb and lb <= 31:
                buf.append("□")
                last = s
                continue
            #2バイト処理
            #http://www.kanzaki.com/docs/jcode.html
            if (129 <= lb and lb <= 159) or (224 <= lb and lb <= 239):
                if (64 <= b and b <= 126) or (128 <= b and b <= 252):
                    buf.append(unicode(last+s, "cp932", "ignore"))
                    last = None
                    continue
            buf.append(unicode(last, "cp932", "ignore"))
        last = s
    if last:
        buf.append(unicode(last, "cp932", "ignore"))
    return "".join(buf)

def little_endian(arr):
    arr = [int_to_hex(str_to_byte(s)) for s in arr]
    arr.reverse()
    return int("".join(arr), 16)

def copy(arr, fr, to):
    buf = []
    for i in xrange(fr, to):
        buf.append(arr[i])
    return buf

def search(file, pat, fr):
    pl = len(pat)
    al = len(file)
    flag = [False] * pl
    def f_clear():
        for i in xrange(pl):
            flag[i] = False
    def f_ok():
        for f in flag:
            if not f:
                return False
        return True
    for i in xrange(fr, al):
        s = file[i]
        b = str_to_byte(s)
        #print "search-> %s %s %s" % (i, flag, int_to_hex(b))
        for j in xrange(pl):
            if flag[j] == True:
                continue
            if pat[j] == b:
                flag[j] = True
            else:
                f_clear()
                if pat[0] == b:
                    flag[0] = True
            break
        if f_ok():
            return i - pl + 1
    return -1
    
def character(buf):
#    define = {
#        []
#    }
    pass

def parse_script(file, start, end):

    p = start
    while p <= end:
        #print "p -> %s" % p
        text_s = search(file, [0x00, 0x0E], p)
        if -1 == end:
            break
        if end <= text_s:
            break
        text_e = search(file, [0x00], text_s+1)
        if -1 == text_e:
            raise "segment error"
        if end <= text_s:
            raise "segment error"
        
        chara_e = text_s-1
        chara_s = chara_e-3
        chara = copy(file, chara_s, chara_e)
        
        
        text = copy(file, text_s+1, text_e)
        print "text: %8s: %8s:" % (text_s, text_e),
        print "%s" % buf_format(text)
        print "%s" % buf_format(chara)
        print "[%s]" % decode(text)
        p = text_e + 1
    print "-> end"

def end_adress(file):
    p = search(file, [0x00], 0)
    if -1 != p:
        buf = copy(file, 0, p)
        return little_endian(buf)
    raise "error"

def buf_format(buf):
    return " ".join([int_to_hex(str_to_byte(s)) for s in buf])

if __name__ == "__main__":    
    filename = "World.hcb"

    file = open(filename, "rb").read()
    filesize = len(file)    
    print "filename: %s" % filename
    print "filesize: %s" % filesize

    script_end = end_adress(file)
    print "script_end: %s" % script_end
    
#    buf, p = find(file, 0x00, p+1)
#    print_buf(buf)
#    
#    buf, p = copy(file, p+1, 12)
#    print_buf(buf)
#    
#    p += 1
#    
#    buf, p = find(file, 0x00, p+1)
#    print_buf(buf)
#    
    
    routes = [
        [ u"共通ルート１章",       "FC 31 07", ],
        [ u"共通ルート２章",       "41 1C 09", ],
        [ u"共通ルート３章",       "B4 A8 0A", ],
        [ u"共通ルート４章",       "8E 04 0C", ],
        [ u"共通ルート５章",       "89 81 0E", ],
        [ u"共通ルート６章",       "45 56 10", ],
        [ u"共通ルート７章",       "0C 39 11", ],
        [ u"共通ルート８章",       "77 69 12", ],
        [ u"共通ルート９章",       "B3 8C 13", ],
        [ u"共通ルート１０章",     "B5 50 15", ],
        [ u"共通ルート１１章",     "9E D2 16", ],
        [ u"共通ルート１２章",     "23 84 18", ],
        [ u"ヒロインルート真紅",   "A8 AC 19", ],
        [ u"ヒロインルート加奈",   "DF A3 23", ],
        [ u"ヒロインルート澪",     "5E 84 2E", ],
        [ u"ヒロインルート鏡",     "8A DD 35", ],
        [ u"ヒロインルートつかさ", "F6 95 39", ],
    ]
    
    for route in routes:
        arr = route[1].split(" ")
        arr.reverse()
        route[1] = int("".join(arr), 16)
        print "%s %s" % (route[0], route[1])
    
    title = routes[0][0]
    start = routes[0][1]
    end = routes[1][1]
    
    print
    print "%s (%s - %s)" % (title, start, end - 1)
    
    parse_script(file, start, end-1)
    
    #print file[end_adress:]
    
    
    
    