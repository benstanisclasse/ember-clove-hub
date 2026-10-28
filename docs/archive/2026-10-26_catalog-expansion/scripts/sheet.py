import sys,os,glob
from PIL import Image,ImageDraw,ImageFont
root=sys.argv[1]; T=int(sys.argv[2]) if len(sys.argv)>2 else 380
try: font=ImageFont.truetype("arial.ttf",22)
except: font=ImageFont.load_default()
for pid in sorted(os.listdir(root)):
    pd=os.path.join(root,pid)
    if not os.path.isdir(pd): continue
    for kind in "gd":
        fs=sorted(glob.glob(os.path.join(pd,kind+"*.img")))
        if not fs: continue
        cols=4; rows=(len(fs)+cols-1)//cols
        sheet=Image.new("RGB",(cols*T,rows*(T+30)),"white"); dr=ImageDraw.Draw(sheet)
        for i,f in enumerate(fs):
            try:
                im=Image.open(f); im.load(); im=im.convert("RGB"); w,h=im.size
                im.thumbnail((T,T))
            except Exception as e:
                im=Image.new("RGB",(T,T),"gray"); w=h=0
            x=(i%cols)*T; y=(i//cols)*(T+30)
            sheet.paste(im,(x,y+30))
            lab=os.path.basename(f).replace(".img","")
            dr.text((x+4,y+4),f"{lab} {w}x{h}",fill="red",font=font)
        sheet.save(os.path.join(root,f"sheet_{pid}_{kind}.jpg"),quality=85)
        print(pid,kind,len(fs))
