# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/14 11:25:52$"

import sys
import codecs
sys.stdout = codecs.getwriter('utf_8')(sys.stdout)

import struct

def int_to_hex(i):
    u"""
    数値を16進数の文字列に変換して返す。
    """
    return ("0" + hex(i)[2:].upper())[-2:]

def str_to_byte(s):
    u"""
    文字列を数値に変換して返す。
    """
    return struct.unpack("B", s)[0]

def is_text(arr):
    u"""
    シナリオファイル内の、正しい文字列パターンであればTrueを返す。
    ・先頭バイト
    ・2バイト目が文字列パターンの長さを表しているか
    をチェックする。
    """
    if 2 <= len(arr):
        if 0x0E == str_to_byte(arr[0]) and str_to_byte(arr[1]) == len(arr) - 1:
            return True
    return False

def is_2byte_character(s1, s2):
    u"""
    連続するビットが、cp932の2バイト表現を満たしていればTrueを返す。
    """
    b1 = str_to_byte(s1)
    b2 = str_to_byte(s2)
    #2バイト処理
    #http://www.kanzaki.com/docs/jcode.html
    if (129 <= b1 and b1 <= 159) or (224 <= b1 and b1 <= 239):
        if (64 <= b2 and b2 <= 126) or (128 <= b2 and b2 <= 252):
            return True
    return False
                    
def is_control_character(s):
    u"""
    コントロールキャラクタであればTrueを返す。
    """
    b = str_to_byte(s)
    if 0 <= b and b <= 31:
        return True
    return False

def to_unicode(s):
    u"""
    文字列をcp932だと解釈して、unicodeに変換する。
    """
    return unicode(s, "cp932", "ignore")

def pretty(s):
    u"""
    コントロールキャラクタを殺す。
    """
    if is_control_character(s):
        return u"□"
    else:
        return to_unicode(s)
    
def decode(arr):
    u"""
    シナリオファイル内に出現する 0x0E 長さ ~ 0x00 の文字列パターンをデコードする。
    文字コードはcp932と解釈。
    """
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
    u"""
    16進数の文字列の配列をリトルエンディアンと解釈し、数値にして返す。
    """
    arr = [int_to_hex(str_to_byte(s)) for s in arr]
    arr.reverse()
    return int("".join(arr), 16)

def search(file, pat, fr):
    u"""
    文字列を、指定位置から、バイナリのパターンで検索する。
    """
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
    
def to_bin_array(str_arr):
    u"""
    文字列を1バイトづつ解釈し、数値の配列として返す。
    """
    return [str_to_byte(s) for s in str_arr]

def parse_script(str_arr, bin_arr, start, end):
    u"""
    シナリオファイルを適当にパースし、
    ボイスID、キャラクタ名、テキストを抽出する。
    アーカイブ的な構造は無視してる。
    """
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
            # 0E ... 00
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
            cid_p = segments[i-1]
            cid = bin_arr[cid_p[0]:cid_p[1]]
            cname = cid_to_cname(cid)
            if cname:
                print "[%s]" % cname,
            if cname and \
                cname != u"悠馬":
                j = i - 1
                while i - 5 < j:
                    j += -1
                    vid_p = segments[j]
                    tmp = bin_arr[vid_p[0]:vid_p[1]]
                    if tmp == [0x08] or \
                        (0x0C == tmp[0] and tmp[1] < 0x0A):
                        continue
                    vid = str_arr[vid_p[0]:vid_p[1]]
                    vid_int = little_endian(vid[1:])
                    print "[%s]" % vid_int,
                    break
            print "[%s]" % decode(str_arr[p0:p1-1])
            
def cid_to_cname(cid):
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

#    if 5 == len(cid) and \
#        0x02 == cid[0] and \
#        cid[2] < 0x20 and \
#        0x00 == cid[3] and \
#        0x00 == cid[4]:
#        return u"maybe valid cid, but not defined"

    return ""
    
def end_adress(file):
    u"""
    ファイルの先頭をチェックして、終了位置を返す。
    """
    p = search(file, [0x00], 0)
    if -1 != p:
        return little_endian(file[:p])
    raise "error"

def buf_format(buf):
    u"""
    文字列を1バイトづつ、16進数に変換し、空白を挟んだフォーマットで返す。
    """
    return " ".join([int_to_hex(str_to_byte(s)) for s in buf])

if __name__ == "__main__":    
    filename = "World.hcb"

    str_arr = open(filename, "rb").read()
    bin_arr = to_bin_array(str_arr)
    filesize = len(str_arr)    
    print "filename: %s" % filename
    print "filesize: %s" % filesize
    script_end = end_adress(str_arr)
    print "script_end: %s" % script_end
    print
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
        parse_script(str_arr, bin_arr, start, end-1)
        #break
    
    