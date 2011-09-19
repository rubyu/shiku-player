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
    return struct.unpack("B", s)[0]

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
    
def decode(arr):
    if not is_text(arr):
        raise "invalid text"
    buf = []
    s1 = None
    for i in xrange(2, len(arr)):
        s2 = arr[i]
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

def head_parse(head):
    def to_bin_array(str_arr):
        return [str_to_byte(s) for s in str_arr]
    def match(bin_arr, pat):
        bl = len(bin_arr)
        pl = len(pat)
        if bl < pl:
            return False
        for i in xrange(pl):
            if not bin_arr[i] == pat[i]:
                return False
        return True
    p = 0
    while p < len(head):
        str_arr = head[p:]
        bin_arr = to_bin_array(str_arr)
        
        if None:
            pass

        elif match(bin_arr, [0x22, 0x20, 07]):
            # 22 20 07 XX XX XX XX
            print buf_format(str_arr[:7])
            p += 7

        elif match(bin_arr, [0x0C, 0x01, 0x15]):
            # 0C 01 15 XX XX
            print buf_format(str_arr[:5])
            p += 5
        elif match(bin_arr, [0x0C, 0x01, 0x19]):
            # 0C 01 19
            print buf_format(str_arr[:3])
            p += 3
            
        elif match(bin_arr, [0x0C, 0x04]):
            # 0C 02
            print buf_format(str_arr[:2])
            p += 2    
        elif match(bin_arr, [0x0C, 0x07]):
            # 0C 02
            print buf_format(str_arr[:2])
            p += 2    
        elif match(bin_arr, [0x0C, 0x02]):
            # 0C 02
            print buf_format(str_arr[:2])
            p += 2
        elif match(bin_arr, [0x0C, 0x01]):
            # 0C 01
            print buf_format(str_arr[:2])
            p += 2
        elif match(bin_arr, [0x0C, 0x00]):
            # 0C 00
            print buf_format(str_arr[:2])
            p += 2
            
        elif match(bin_arr, [0x01]):
            # 01 00 00
            print buf_format(str_arr[:3])
            p += 3
        elif match(bin_arr, [0x02]):
            # 02 XX XX XX
            print buf_format(str_arr[:4])
            p += 4
        
        elif match(bin_arr, [0x09]):
            # 09 XX
            print buf_format(str_arr[:2])
            p += 2
        
        elif match(bin_arr, [0x0B]):
            # 0B XX XX
            print buf_format(str_arr[:3])
            p += 3
        
        elif match(bin_arr, [0x0F]):
            # 0F XX
            print buf_format(str_arr[:2])
            p += 2
        
        elif match(bin_arr, [0x08]):
            # 08
            print "(%s)" % buf_format(str_arr[:1])
            p += 1
        
        elif match(bin_arr, [0x00]):
            # 00
            print "(%s)" % buf_format(str_arr[:1])
            p += 1
        
        else:
            # XX
            print buf_format(str_arr[:1])
            p += 1
#        
#        s0 = head[p0]
#        b0 = str_to_byte(s0)
#        if b0 == 0x01:
#            buf = copy(head, p0, p0+3)
#            print buf_format(buf)
#            p0 = p0+3
#        elif b0 == 0x02:
#            buf = copy(head, p0, p0+4)
#            print buf_format(buf)
#            p0 = p0+4
#        elif b0 == 0x0C:
#            buf = copy(head, p0, p0+2)
#            print buf_format(buf)
#            p0 = p0+2
#        elif b0 == 0x0F:
#            buf = copy(head, p0, p0+2)
#            print buf_format(buf)
#            p0 = p0+2
#        elif b0 == 0x08:
#            buf = copy(head, p0, p0+1)
#            print buf_format(buf)
#            p0 = p0+1
#        else:
#            buf = copy(head, p0, p0+1)
#            print buf_format(buf)
#            p0 = p0+1
    
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
        
        head = copy(file, p, text_s+1)
        print "head: %s-%s:" % (p, text_s-1),
        print "%s" % buf_format(head)
        head_parse(head)
        
        chara_e = text_s-1
        chara_s = chara_e-3
        chara = copy(file, chara_s, chara_e)
        
        print "chara: %s-%s:" % (chara_s, chara_e),
        print "%s" % buf_format(chara)
        
        text = copy(file, text_s+1, text_e)
        print "text: %s-%s:" % (text_s, text_e),
        print "%s" % buf_format(text)
        print "[%s]" % decode(text)
        p = text_e + 1
    print "-> end"

def parse_script2(str_arr, start, end):
    def to_bin_array(str_arr):
        return [str_to_byte(s) for s in str_arr]
    bin_arr = to_bin_array(str_arr)
    p0 = start
    while p0 <= end:
        if None:
            pass
        
        elif bin_arr[p0] == 0x01:
            # 01 XX XX
            print buf_format(str_arr[p0:p0+3])
            p0 += 3
        
        elif bin_arr[p0] == 0x02:
            # 02 XX XX XX XX
            print buf_format(str_arr[p0:p0+5])
            p0 += 5
        
        elif bin_arr[p0] == 0x06:
            # 06 XX XX XX XX
            print buf_format(str_arr[p0:p0+5])
            p0 += 5
        
        elif bin_arr[p0] == 0x07:
            # 07 XX XX XX XX
            print buf_format(str_arr[p0:p0+5])
            p0 += 5
        
        elif bin_arr[p0] == 0x0A:
            # 0A XX XX XX XX
            print buf_format(str_arr[p0:p0+5])
            p0 += 5
        
        elif bin_arr[p0] == 0x0B:
            # 0B ... (0B|0C|02|08)
            p1 = p0
            p1 += 1 #長さ0の場合は無い、はず
            while p1 <= end:
                p1 += 1
                if  bin_arr[p1] == 0x0B or\
                    bin_arr[p1] == 0x0C or\
                    bin_arr[p1] == 0x02 or\
                    bin_arr[p1] == 0x08:
                    break
            print buf_format(str_arr[p0:p1])
            p0 = p1 
        
        elif bin_arr[p0] == 0x0C:
            # 0C ... (0B|0C|02|08)
            p1 = p0
            p1 += 1 #長さ0の場合は無い、はず
            while p1 <= end:
                p1 += 1
                if  bin_arr[p1] == 0x0B or\
                    bin_arr[p1] == 0x0C or\
                    bin_arr[p1] == 0x02 or\
                    bin_arr[p1] == 0x08:
                    break
            print buf_format(str_arr[p0:p1])
            p0 = p1 
        
        elif bin_arr[p0] == 0x0E:
            # 0E ... 00
            p1 = p0
            while p1 <= end:
                p1 += 1
                if bin_arr[p1] == 0x00:
                    break
            buf = str_arr[p0:p1]
            #print buf_format(buf),
            print "[%s]" % decode(buf)
            p1 += 1
            p0 = p1

        elif bin_arr[p0] == 0x0F:
            # 0F XX 00
            print buf_format(str_arr[p0:p0+3])
            p0 += 3
        
        else:
            # *
            print buf_format(str_arr[p0:p0+1])
            p0 += 1
        
        

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
    
    for i, route in enumerate(routes):
        title = route[0]
        start = route[1]
        if i == len(routes) - 1:
            end = script_end
        else:
            end = routes[i+1][1]
        
        print
        print "%s (%s - %s)" % (title, start, end - 1)
        
        #parse_script(file, start, end-1)   
        parse_script2(file, start, end-1)

#    title = routes[0][0]
#    start = routes[0][1]
#    end = routes[1][1]
#    
#    print
#    print "%s (%s - %s)" % (title, start, end - 1)
#    
#    #parse_script(file, start, end-1)
#    parse_script2(file, start, end-1)
#    
#    #print file[end_adress:]
    
    
    
    