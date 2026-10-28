import json,sys
sys_=__import__("sys"); sys_.stdout.reconfigure(encoding="utf-8")
HUB=r'C:/Users/Administrator/Documents/EmberClove-Hub'
mine=['9756889153775','9756889252079','9756889612527','9756889874671','9756890005743','9756901933295','9756905537775','9756949676271']
d=json.load(open(HUB+'/data/inbox/shopify_products_full_2026-10-26_new.json',encoding='utf-8'))['data']['products']['nodes']
out={}
for pid in mine:
    p=[n for n in d if n['id'].endswith(pid)][0]
    c=json.load(open(HUB+'/data/catalog/'+p['handle']+'.json',encoding='utf-8'))
    print('=====',pid,p['handle']); print('title:',p['title'])
    print('options:',[(o['name'],o['values']) for o in p['options']])
    media=[m['id'] for m in p['media']['nodes']]
    vm={}
    for v in p['variants']['nodes']:
        col=[o['value'] for o in v['selectedOptions'] if o['name'].lower()!='size']
        for m in v['media']['nodes']:
            vm.setdefault(m['id'],set()).add('/'.join(col))
    for i,m in enumerate(media): print(f'  [{i}] {m.split("/")[-1]} variant:{sorted(vm.get(m,[]))}')
    print('specs:',c['specs']); print('desc_text:',c['description_text']); print('size_tables:',c['size_tables'])
    print('n desc imgs:',len(c['description_images']))
    out[pid]={'handle':p['handle'],'gallery':[(m['id'],m['image']['url']) for m in p['media']['nodes']],'desc':c['description_images']}
json.dump(out,open(sys.argv[1],'w'),indent=1)
