"""POST one file to a Shopify staged-upload target. usage: staged_upload.py <params.json> <file>"""
import json
import sys

import requests

t = json.load(open(sys.argv[1]))
fields = [(p["name"], (None, p["value"])) for p in t["parameters"]]
fields.append(("file", (sys.argv[2].split("\\")[-1].split("/")[-1], open(sys.argv[2], "rb"), "image/png")))
r = requests.post(t["url"], files=fields, timeout=120)
print(r.status_code, r.text[:200])
