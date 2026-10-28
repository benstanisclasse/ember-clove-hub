from PIL import Image
Q = r"C:\Users\Administrator\AppData\Local\Temp\ec_q"
names = ["i046","i047","i048","i051","i054","i511","i513","i001"]
S = Image.new("RGB", (4*300, 2*300), "white")
for k, n in enumerate(names):
    im = Image.open(f"{Q}\\all\\{n}.jpg").convert("RGB"); im.thumbnail((295, 295))
    S.paste(im, ((k%4)*300, (k//4)*300))
S.save(Q + r"\sh\thumbs.png")
