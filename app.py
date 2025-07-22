import os, hashlib, time, xml.etree.ElementTree as ET, requests
from flask import Flask, request

app = Flask(__name__)
TOKEN = os.getenv("WECHAT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET", "POST"])
def wechat():
    if request.method == "GET":
        args = request.args
        s = [TOKEN, args["timestamp"], args["nonce"]]
        s.sort()
        if hashlib.sha1("".join(s).encode()).hexdigest() == args["signature"]:
            return args["echostr"]
        return ""
    xml_data = request.data
    root = ET.fromstring(xml_data)
    to_user = root.find("FromUserName").text
    from_user = root.find("ToUserName").text
    content = root.find("Content").text.strip()

    resp = requests.post("https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={"model":"gpt-3.5-turbo","messages":[{"role":"system","content":"你是专业简历顾问。"},{"role":"user","content":content}],"temperature":0.7}
    )
    reply = resp.json()["choices"][0]["message"]["content"]

    response = f"""
    <xml>
      <ToUserName><![CDATA[{to_user}]]></ToUserName>
      <FromUserName><![CDATA[{from_user}]]></FromUserName>
      <CreateTime>{int(time.time())}</CreateTime>
      <MsgType><![CDATA[text]]></MsgType>
      <Content><![CDATA[{reply}]]></Content>
    </xml>"""
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
