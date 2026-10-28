import sys,glob,os
from PIL import Image
root=sys.argv[1]; specs=sys.argv[3:]; out=sys.argv[2]
tiles=[]
for sp in specs:
    pid,pre,box=sp.split(":"); x0,y0,x1,y1=map(float,box.split(","))
    f=glob.glob(os.path.join(root,pid,pre+"*.img"))[0]
    im=Image.open(f).convert("RGB"); W,H=im.size
    c=im.crop((int(x0*W),int(y0*H),int(x1*W),int(y1*H))); c.thumbnail((500,500)); tiles.append(c)
W=sum(t.width for t in tiles); H=max(t.height for t in tiles)
s=Image.new("RGB",(W,H),"white"); x=0
for t in tiles: s.paste(t,(x,0)); x+=t.width
s.save(out)
