# -*- coding:utf-8 -*-

__author__="rubyu"
__date__ ="$2011/09/14 11:25:52$"

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)-8s %(module)-16s %(funcName)-16s@%(lineno)d - %(message)s"
)

import re
import json
    
from flask \
    import Flask, make_response, render_template, redirect, url_for
app = Flask(__name__)

from sekai.voice_parser import Voice
from sekai.script_parser import Script
from sekai.defs \
    import VOICE_FILE, SCRIPT_FILE

voice = Voice.restore_or_create(VOICE_FILE, "voice.p")
script = Script.restore_or_create(SCRIPT_FILE, "script.p")

@app.route("/")
def show_root():
    return render_template("index.html")

@app.route("/query/json/")
def query_json_():
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
    app.debug = True
    app.run()

if __name__ == "__main__":
    main()
