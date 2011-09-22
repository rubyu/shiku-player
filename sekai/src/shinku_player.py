# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/14 11:25:52$"

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s %(module)-16s %(funcName)-16s@%(lineno)d - %(message)s"
)

import os
import sys
from optparse import OptionParser
import cPickle as _pickle
import re
import json

from flask \
    import Flask, make_response, render_template
app = Flask(__name__)

from sekai.voice_parser import Voice
from sekai.script_parser import Script

voice = None
script = None

def save(obj, dump):
    try:
        _pickle.dump(obj, open(dump, "wb"))
    except:
        pass
def restore(dump):
    try:
        return _pickle.load(open(dump, "rb"))
    except:
        pass
    
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
    for title in script.titles:
        for text in script.texts[title]:
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
    return ruby_pat.sub(r"<ruby>\2<rt>\1</rt></ruby>", str)

def main():
    parser = OptionParser("usage: shinku_player.py --path=game_installed")
    parser.add_option(
        "-p", 
        "--path",
        type="string",
        help="Directory that the game installed."
    )
    options = parser.parse_args()[0]
    
    if options.path:
        save({"path": options.path}, "gconfig.p")
        logging.debug("path(%s) saved to gconfig.p" % options.path)
    
    gconfig = restore("gconfig.p")
    if not gconfig:
        parser.error("path is not given!")
        sys.exit()
    path = gconfig["path"]
    voice_path = os.path.join(path, "voice.bin")
    script_path = os.path.join(path, "World.hcb")
    if not os.path.isdir(path) or \
       not os.path.isfile(voice_path) or \
       not os.path.isfile(script_path):
        parser.error("'voice.bin' and 'World.hcb' is needed!")
        sys.exit()
    
    logging.info("path restored from gconfig.p: %s" % path)
    global voice
    global script
    voice = Voice.restore_or_create(voice_path, "voice.p")
    script = Script.restore_or_create(script_path, "script.p")
    
    app.debug = True
    app.run()

if __name__ == "__main__":
    main()
