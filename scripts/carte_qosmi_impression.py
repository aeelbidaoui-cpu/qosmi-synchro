from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import CMYKColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image
import qrcode
for n in ("Regular","Medium","Light"): pdfmetrics.registerFont(TTFont("Jost-"+n,"Jost-%s.ttf"%n))
K=CMYKColor(0,0,0,1)
B=3*mm; W,H=85*mm+2*B,55*mm+2*B
def gris(src,dst):
    im=Image.open(src).convert("RGBA"); bg=Image.new("RGBA",im.size,"white"); bg.alpha_composite(im); bg.convert("L").point(lambda p:255 if p>235 else p).save(dst)
def cmyk(src_l,dst):
    L=Image.open(src_l).convert("L"); k=Image.eval(L,lambda p:255-p); z=Image.new("L",L.size,0)
    Image.merge("CMYK",(z,z,z,k)).save(dst,"TIFF")
gris("assets/qosmi-logo.png","logo_L.png")
logo=Image.open("logo_L.png")
# icône Mimi seule (partie gauche du logo)
ico=logo.crop((0,0,int(logo.size[0]*0.115),logo.size[1])); bb=Image.eval(ico,lambda p:255-p).getbbox(); ico=ico.crop(bb); ico.save("mimi_L.png")
def tracke(c,txt,x,y,font,size,track,centre=False):
    w=sum(pdfmetrics.stringWidth(ch,font,size) for ch in txt)+track*(len(txt)-1)
    if centre: x-=w/2
    t=c.beginText(x,y); t.setFont(font,size); t.setCharSpace(track); t.setFillColor(K); t.textOut(txt); c.drawText(t)
import potrace, numpy as np
def trace(src):
    L=np.array(Image.open(src).convert("L")); bm=potrace.Bitmap(L>=128)
    return bm.trace(turdsize=2,alphamax=1.0,opticurve=True,opttolerance=0.2), L.shape
def dessine(src,x,y,w):
    plist,(h_px,w_px)=trace(src); s=w/w_px; h=h_px*s
    p=c.beginPath()
    for curve in plist:
        X=lambda pt:x+pt.x*s; Y=lambda pt:y+h-pt.y*s
        p.moveTo(X(curve.start_point),Y(curve.start_point))
        for seg in curve.segments:
            if seg.is_corner: p.lineTo(X(seg.c),Y(seg.c)); p.lineTo(X(seg.end_point),Y(seg.end_point))
            else: p.curveTo(X(seg.c1),Y(seg.c1),X(seg.c2),Y(seg.c2),X(seg.end_point),Y(seg.end_point))
        p.close()
    c.setFillColor(K); c.drawPath(p,stroke=0,fill=1,fillMode=0)
    return h
c=canvas.Canvas("Qosmi-carte-85x55-recto-verso.pdf",pagesize=(W,H),initialFontName="Jost-Regular",initialFontSize=7)
c.setTitle("Qosmi - carte 85x55 recto verso"); c.setAuthor("Qosmi")
def boites():
    c.setTrimBox((B,B,W-B,H-B)); c.setBleedBox((0,0,W,H))
# RECTO
boites()
lw=52*mm; lh=lw*logo.size[1]/logo.size[0]
dessine("logo_L.png",(W-lw)/2,H/2-lh/2+3*mm,lw)
tracke(c,"FRAGRANCE & BEAUTY",W/2,H/2-lh/2-4*mm,"Jost-Regular",6.5,1.6,centre=True)
c.showPage()
# VERSO
boites()
x0=B+6*mm; top=H-B-8*mm
c.setFillColor(K)
c.setFont("Jost-Medium",17); c.drawString(x0,top-4*mm,"Merci !")
c.setFont("Jost-Light",11); c.drawString(x0,top-10*mm,"Bedankt!")
c.setFont("Jost-Regular",7)
c.drawString(x0,top-18*mm,"Ta commande a été préparée avec soin.")
c.setFont("Jost-Light",7)
c.drawString(x0,top-21.5*mm,"Je bestelling werd met zorg ingepakt.")
c.setFont("Jost-Regular",7)
c.drawString(x0,B+7.5*mm,"qosmi.be")
c.setFont("Jost-Light",7)
c.drawString(x0,B+4.5*mm,"contact@qosmi.be")
# QR vectoriel -> Instagram
q=qrcode.QRCode(border=0,error_correction=qrcode.constants.ERROR_CORRECT_M); q.add_data("https://www.instagram.com/qosmi.be"); q.make(fit=True)
mtx=q.get_matrix(); n=len(mtx); size=17*mm; cell=size/n
qx=W-B-6*mm-size; qy=B+9*mm
for r,row in enumerate(mtx):
    for col,v in enumerate(row):
        if v: c.rect(qx+col*cell,qy+(n-1-r)*cell,cell+0.01,cell+0.01,stroke=0,fill=1)
tracke(c,"@qosmi.be",qx+size/2,B+4.5*mm,"Jost-Regular",6.5,0.3,centre=True)
tracke(c,"INSTAGRAM",qx+size/2,qy+size+2.2*mm,"Jost-Regular",5.5,1.2,centre=True)
# petite Mimi en haut à droite
iw=6*mm; ih=iw*ico.size[1]/ico.size[0]
dessine("mimi_L.png",W-B-6*mm-iw,H-B-6*mm-ih,iw)
c.showPage(); c.save()
print("ok",W/mm,H/mm)
