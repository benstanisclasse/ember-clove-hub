import cv2, sys, numpy as np, os
base=r"C:\Users\Administrator\Documents\EmberClove-Hub\research\tiktok\ads"
out=os.path.join(base,"analysis","_tmp_02")
def frame(vid,t):
    cap=cv2.VideoCapture(os.path.join(base,"videos",vid+".mp4"))
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000); ok,f=cap.read(); cap.release()
    return f if ok else None
def montage(vid,times,name,h=480):
    ims=[]
    for t in times:
        f=frame(vid,t)
        if f is None: continue
        s=h/f.shape[0]; f=cv2.resize(f,(int(f.shape[1]*s),h))
        cv2.putText(f,f"{t}s",(5,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        ims.append(f)
    rows=[np.hstack(ims[i:i+6]+[np.zeros_like(ims[0])]*(6-len(ims[i:i+6]))) for i in range(0,len(ims),6)]
    cv2.imwrite(os.path.join(out,name+".jpg"),np.vstack(rows))
def crop(vid,t,y0,y1,name):
    f=frame(vid,t); H=f.shape[0]
    c=f[int(H*y0):int(H*y1)]
    cv2.imwrite(os.path.join(out,name+".jpg"),c)
    print(name,f.shape)
mode=sys.argv[1]
if mode=="m":
    montage(sys.argv[2],[float(x) for x in sys.argv[3].split(",")],sys.argv[4])
else:
    crop(sys.argv[2],float(sys.argv[3]),float(sys.argv[4]),float(sys.argv[5]),sys.argv[6])
