# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/21 11:57:12$"

import struct

def hex_str(i):
    u"""
    数値を16進数の文字列に変換して返す。
    """
    return ("0" + hex(i)[2:].upper())[-2:]

def byte_int(s):
    u"""
    文字列を数値に変換して返す。
    """
    b = struct.unpack("B", s)
    if 1 != len(b):
        raise ValueError()
    return b[0]

def from_little_endian(str):
    u"""
    16進数の文字列の配列をリトルエンディアンと解釈し、数値にして返す。
    """
    arr = [hex_str(byte_int(s)) for s in str]
    arr.reverse()
    return int("".join(arr), 16)


def byte_array(str):
    u"""
    文字列を1バイトづつ解釈し、数値の配列として返す。
    """
    return [byte_int(s) for s in str]


def is_cp932_2byte_char(s1, s2):
    u"""
    連続するビットが、cp932の2バイト表現を満たしていればTrueを返す。
    """
    b1 = byte_int(s1)
    b2 = byte_int(s2)
    #2バイト処理
    #http://www.kanzaki.com/docs/jcode.html
    if (129 <= b1 and b1 <= 159) or (224 <= b1 and b1 <= 239):
        if (64 <= b2 and b2 <= 126) or (128 <= b2 and b2 <= 252):
            return True
    return False
                    
def is_ctrl_char(s):
    u"""
    コントロールキャラクタであればTrueを返す。
    """
    b = byte_int(s)
    if 0 <= b and b <= 31:
        return True
    return False

def from_cp932(str):
    u"""
    文字列をcp932から、unicodeに変換する。
    """
    return unicode(str, "cp932", "ignore")

def pretty(s, replace):
    u"""
    コントロールキャラクタを殺す。
    """
    if is_ctrl_char(s):
        return replace
    else:
        return s
    
def hex_format(str):
    u"""
    文字列を1バイトづつ、16進数に変換し、空白を挟んだフォーマットで返す。
    """
    return " ".join([hex_str(byte_int(s)) for s in str])

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
        b = byte_int(s)
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
    