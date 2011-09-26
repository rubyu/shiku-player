# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/14 11:25:52$"

import unittest
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s %(module)-16s %(funcName)-16s@%(lineno)d - %(message)s"
)

import os
import sys
import re
import json

from flask \
    import Flask, make_response, render_template
app = Flask(__name__)

from sekai.voice_parser import Voice
from sekai.script_parser import Script

voice = None
script = None

from config \
    import Config

@app.route("/")
def show_root():
    return render_template("index.html")

@app.route("/query/json/")
def query_json_():
    u"""
    これは綺麗じゃないと思うんだが、解決法がよくわからない。
    """
    return query_json("")

@app.route("/query/json/<keyword>")
def query_json(keyword):
    u"""
    真紅の発言について、キーワードが含まれるものだけを返す。
    
    jsonで、以下の形式で。
    [ [発言, ボイスID], ... ]
    """
    logging.debug("keyword: %s", keyword)
    arr = []
    for text in script.texts:
        str, name, vid = text
        if name == u"真紅" and \
           -1 != str.find(keyword):
            str = html_ruby(str)
            arr.append((str, vid))
    logging.debug("size: %s", len(arr))
    response = make_response()
    response.data = json.dumps(arr)
    response.headers["Content-Type"] = "application/json"
    return response

@app.route("/voice/ogg/<voice_id>")
def output_voice(voice_id):
    u"""
    指定のIDのボイスを切り出して返す。
    形式はもとのoggのまま。
    """
    logging.debug("voice id: %s", voice_id)
    response = make_response()
    response.data = voice.get(voice_id)
    response.headers["Content-Type"] = "audio/ogg"
    response.headers["Content-Disposition"] = "attachment; filename=%s.ogg" % voice_id
    return response

ruby_pat = re.compile("\[(.+?)\|(.+?)\]")
def html_ruby(str):
    u"""
    ...[ルビ|テキスト]...の形式を、HTMLのルビタグに変換する。
    複数個含まれる場合は全て変換する。
    """
    return ruby_pat.sub(r"<ruby>\2<rt>\1</rt></ruby>", str)


class ProcWrapper(object):
    u"""
    コマンドラインから呼び出されるラッパ。
    テスト時はダミーに差し替えられる。
    """
    def app_run(self, voice_path, script_path):
        global voice
        global script
        try:
            voice = Voice.restore("voice.p")
        except Exception, e:
            logging.debug("Excepted: %s", e)
            voice = Voice(voice_path)
            voice.save("voice.p")
        try:
            script = Script.restore("script.p")
        except Exception, e:
            logging.debug("Excepted: %s", e)
            script = Script(script_path)
            script.save("script.p")
        app.run()
            

class OptionParserTestCase(unittest.TestCase):
    u"""
    コマンドラインオプションのテスト。
    """
    class DummyProcWrapper(object):
        u"""
        ダミーのラッパクラス。
        コールされた関数のログを持つ。
        """
        def __init__(self):
            self._log = []

        def __getattr__(self, name):
            def _dummy(self, *args, **kwargs):
                pass
            self._log.append(name)
            return _dummy    
        
        
    @classmethod
    def setUpClass(cls):
        cls._path = "/tmp/sekai"
        cls._argv = sys.argv
    
    @classmethod
    def terDownClass(cls):
        sys.argv = cls._argv
        
    def setUp(self):
        self._wrapper = self.DummyProcWrapper()
        sys.argv = [self._argv[0]]
        
    def test_path(self):
        u"""
        引数pathが与えられた場合。
        """
        sys.argv.append("--path=%s" % self._path)
        parse(self._wrapper)
        self.assertEqual(["app_run"], self._wrapper._log)
        

def parser():
    u"""
    OptionParserのインスタンスを返す。
    """
    from optparse import OptionParser
    p = OptionParser("usage: shinku_player.py --path=game_installed")
    p.add_option(
        "-p", 
        "--path",
        type="string",
        help="directory that the game installed"
    )
    return p

def parse(wrapper):
    u"""
    コマンドラインオプションで分岐し、ラッパをコールする。
    """
    p = parser()
    options, args = p.parse_args()
    
    if options.path:
        config = Config()
        config.path = options.path
        config.save("config.p")
    
    try:
        config = Config.restore("config.p")
    except Exception, e:
        logging.debug("Excepted: %s", e)
        p.error("Program has not enough data. The 'path' parameter never had been given to this program!")
        sys.exit()
        
    voice_path = os.path.join(config.path, "voice.bin")
    script_path = os.path.join(config.path, "World.hcb")
    if not os.path.isdir(config.path) or \
       not os.path.isfile(voice_path) or \
       not os.path.isfile(script_path):
        p.error("File not found. 'voice.bin' and 'World.hcb' must be in the 'path=%s'!" % config.path)
        sys.exit()
    
    app.debug = True
    wrapper.app_run(voice_path, script_path)
    
if __name__ == "__main__":
    debug = False
#    debug = True
    
    if debug:
        unittest.main()
    else:
        parse(ProcWrapper())
