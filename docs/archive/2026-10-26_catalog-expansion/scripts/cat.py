import sys; sys.stdout.reconfigure(encoding='utf-8')
import json,sys,glob
c=r"C:\Users\Administrator\Documents\EmberClove-Hub\data\catalog"
for h in sys.argv[1:]:
    d=json.load(open(f"{c}\\{h}.json",encoding="utf-8"))
    print("=====",h)
    print("SPECS:",json.dumps(d.get("specs"),ensure_ascii=False)[:900])
    print("DESC:",json.dumps(d.get("description_text"),ensure_ascii=False)[:900])
    print("SIZE_TABLES:",json.dumps(d.get("size_tables"),ensure_ascii=False)[:1200])
    print("DESC_IMGS:",len(d.get("description_images") or []))


