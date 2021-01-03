#! /usr/bin/env python
# server.py
from flask import Flask, render_template, request, session, redirect, url_for, redirect, make_response
import re, sys, os
import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__, static_folder="./static", template_folder="./templates")
#same url and url with trailing slash
app.url_map.strict_slashes = False
app.secret_key = 'nutanix'

@app.route("/<mystring>")
def string(mystring):
    url = "https://%s:%s/api/nutanix/v3/action_rules/trigger" % (app.config.get("pc_ip"), app.config.get("pc_port"))

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Basic %s" % app.config.get("pc_token"),
        "Cache-Control": "no-cache"
    }

    # change url string to json
    content = re.sub("%7B", "{", mystring)
    content = re.sub("%7D", "}", content)
    content = re.sub("%5B", "[", content)
    content = re.sub("%5D", "]", content)
    content = re.sub("%3A", ":", content)
    content = re.sub("%22", "\"", content)
    content = re.sub("%20", " ", content)
    content = re.sub("%2C", ",", content)
    content = re.sub("%3B", ";", content)
    content = re.sub("%40", "%", content)
    content = re.sub("~"  , "/", content)

    #payload = json.loads(content)
    #print(json.dumps(payload, indent=2))
    r = requests.post(url, headers=headers, verify=False, data=content)
    if r.ok:
        return render_template(
            "single-page.html",
            hostname=os.uname()[1],
            title='Workflow',
            content=r.text
        )
    else:
        return render_template(
            "single-page.html",
            hostname=os.uname()[1],
            title='Workflow',
            content=r.text
        )

if __name__ == "__main__":

    pc_ip = ""
    pc_port = ""
    pc_token = ""
    if pc_ip == "" or pc_port == "" or pc_token == "":
        pc_ip = os.getenv("PC_IP", "")
        pc_port = os.getenv("PC_PORT", "")
        pc_token = os.getenv("PC_TOKEN", "")
        if pc_ip == "" or pc_port == "" or pc_token == "":
            print("No PC Environment Variable")
            sys.exit(9)
    
    app.debug = True
    app.config["pc_ip"] = pc_ip
    app.config["pc_port"] = pc_port
    app.config["pc_token"] = pc_token
    app.run(host='0.0.0.0', port='5000')

