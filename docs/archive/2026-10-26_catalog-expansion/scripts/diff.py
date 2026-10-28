import sys
from PIL import Image, ImageChops
a=Image.open(sys.argv[1]).convert('L').resize((200,200)); b=Image.open(sys.argv[2]).convert('L').resize((200,200))
d=ImageChops.difference(a,b); print(sum(d.getdata())/40000)
