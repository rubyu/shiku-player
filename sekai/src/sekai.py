# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/14 11:25:52$"

import logging
from voice_parser import Voice
from script_parser import Script

def main():
    pass

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)-8s %(module)-16s %(funcName)-16s@%(lineno)d - %(message)s"
    )
    import sys
    import codecs
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
    main()
