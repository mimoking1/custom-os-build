import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops, ImageFont
ACC=(79,178,247); S=3
MOON=Image.open("/downloads/os-build/theme/crescent-moon.png").convert("RGBA")
bb=MOON.split()[-1].point(lambda a:255 if a>10 else 0).getbbox(); MOON=MOON.crop(bb)
def mix(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def grid(D):
    y,x=np.mgrid[0:D,0:D].astype(np.float32); c=(D-1)/2; return (x-c)/c,(y-c)/c
def arr2img(a): return Image.fromarray(np.clip(a,0,255).astype(np.uint8),"RGBA")
def glass_orb(size, tint_top, tint_bot, alpha_body=255, pad=0.05):
    D=size*S; X,Y=grid(D); sc=1/(1-2*pad); X*=sc; Y*=sc
    rr=np.sqrt(X*X+Y*Y); inside=(rr<=1).astype(np.float32)
    edge=np.clip((1-rr)*D/ (2*S),0,1)  # antialias
    cov=np.clip((1-rr)*D/2,0,1)
    t=(Y+1)/2
    col=np.zeros((D,D,4),np.float32)
    for i in range(3): col[...,i]=tint_top[i]+(tint_bot[i]-tint_top[i])*t
    # fresnel rim: brighter, bluish-white toward edge
    fr=np.clip((rr-0.62)/0.38,0,1)**2.2
    for i in range(3): col[...,i]=col[...,i]*(1-0.55*fr)+255*0.55*fr*np.array([0.85,0.95,1.0])[i]
    # bottom caustic: bright lens glow at lower inside edge
    cau=np.exp(-(((X-0.0)/0.55)**2+((Y-0.62)/0.22)**2))*np.clip((rr<0.92),0,1)
    for i in range(3): col[...,i]+=cau*90
    col[...,3]=255*cov
    img=arr2img(col)
    # top specular reflection
    sp=Image.new("L",(D,D),0); dr=ImageDraw.Draw(sp)
    dr.ellipse([D*.17,D*.07,D*.83,D*.46],fill=150)
    sp=sp.filter(ImageFilter.GaussianBlur(D*.012))
    grad=np.linspace(1,0.05,D)[:,None]*np.ones((1,D)); sp=ImageChops.multiply(sp,Image.fromarray((grad*255).astype(np.uint8)))
    sp=ImageChops.multiply(sp,Image.fromarray((cov*255).astype(np.uint8)))
    w=Image.new("RGBA",(D,D),(255,255,255,255)); w.putalpha(sp); img=Image.alpha_composite(img,w)
    # crisp rim line
    rim=np.clip(1-np.abs(rr-0.985)/0.012,0,1)*(0.35+0.65*np.clip(-Y*0.8+0.5,0,1))
    rl=np.zeros((D,D,4),np.float32); rl[...,:3]=255; rl[...,3]=rim*210
    img=Image.alpha_composite(img,arr2img(rl))
    return img, Image.fromarray((cov*255).astype(np.uint8))
def sphere(rad,color,S_=1):
    d=int(rad*2+4); X,Y=grid(d); r=np.sqrt(X*X+Y*Y)
    z=np.sqrt(np.clip(1-r*r,0,1)); L=np.array([-0.45,-0.6,0.66]); L/=np.linalg.norm(L)
    nd=np.clip(X*L[0]+Y*L[1]+z*L[2],0,1)
    rf=2*(X*L[0]+Y*L[1]+z*L[2])*z-L[2]; spec=np.clip(rf,0,1)**28
    a=np.zeros((d,d,4),np.float32)
    for i in range(3): a[...,i]=color[i]*(0.28+0.85*nd)+255*spec*0.95
    a[...,3]=255*np.clip((1-r)*d/2,0,1)
    return arr2img(a)
def metal_line(layer_size,p,q,width,col):
    D=layer_size; l=Image.new("RGBA",(D,D),(0,0,0,0)); dr=ImageDraw.Draw(l)
    dr.line([p,q],fill=mix(col,(0,0,0),0.55)+(255,),width=int(width))
    dr.line([p,q],fill=mix(col,(255,255,255),0.1)+(255,),width=max(1,int(width*0.66)))
    # offset highlight toward upper-left
    off=(-width*0.18,-width*0.22)
    dr.line([(p[0]+off[0],p[1]+off[1]),(q[0]+off[0],q[1]+off[1])],fill=(255,255,255,235),width=max(1,int(width*0.22)))
    return l
def shadow(base_alpha,size,dy=0.03,blur=0.025,k=0.5):
    D=size*S; a=base_alpha.filter(ImageFilter.GaussianBlur(D*blur))
    sh=Image.new("RGBA",(D,D),(0,0,10,255)); sh.putalpha(a.point(lambda v:int(v*k)))
    return ImageChops.offset(sh,0,int(D*dy))
def moon_scaled(h):
    m=MOON.resize((int(MOON.width*h/MOON.height),int(h)),Image.LANCZOS); return m
def place(img,layer,cx,cy):
    img.alpha_composite(layer,(int(cx-layer.width/2),int(cy-layer.height/2)))
def moon_light(m):
    # add subtle rim light on lit edge for depth
    a=m.split()[-1]; e=ImageChops.subtract(a,a.filter(ImageFilter.MinFilter(5)))
    l=Image.new("RGBA",m.size,(235,245,255,255)); l.putalpha(e.point(lambda v:int(v*0.6)))
    return Image.alpha_composite(m,l)
# crescent outline points from alpha (for nodes)
def edge_nodes(m,n):
    a=np.array(m.split()[-1])>128
    ys,xs=np.nonzero(a); cx,cy=xs.mean(),ys.mean()
    # boundary pixels
    from itertools import product
    pad=np.pad(a,1); b=a&~(pad[:-2,1:-1]&pad[2:,1:-1]&pad[1:-1,:-2]&pad[1:-1,2:])
    by,bx=np.nonzero(b)
    ang=np.arctan2(by-cy,bx-cx); order=np.argsort(ang)
    return np.stack([bx[order],by[order]],1)
# ---- concept 1: orb, real moon, metal mesh nodes along crescent edge
def c1(size=512):
    D=size*S; orb,cov=glass_orb(size,mix(ACC,(255,255,255),0.38),mix(ACC,(0,0,0),0.72))
    out=Image.new("RGBA",(D,D),(0,0,0,0)); out.alpha_composite(shadow(cov,size))
    out.alpha_composite(orb)
    m=moon_light(moon_scaled(D*0.58)); place(out,m,D*0.5,D*0.52)
    a=np.array(m.split()[-1])>128; ys,xs=np.nonzero(a)
    ox=D*0.5-m.width/2; oy=D*0.52-m.height/2
    c0=((xs.min()+xs.max())/2+ (xs.max()-xs.min())*0.12, (ys.min()+ys.max())/2)
    ang=np.arctan2(ys-c0[1],xs-c0[0]); rad=np.hypot(xs-c0[0],ys-c0[1])
    lo,hi=np.percentile(ang,6),np.percentile(ang,94)
    nb=9; O=[];I=[]
    for k in range(nb):
        t=lo+(hi-lo)*k/(nb-1); sel=np.abs(ang-t)<0.05
        if sel.sum()<5: continue
        r_o=rad[sel].max(); r_i=rad[sel].min()
        wd_=r_o-r_i
        ro=r_o-wd_*0.14; O.append((ox+c0[0]+ro*math.cos(t),oy+c0[1]+ro*math.sin(t)))
        ri=r_i+wd_*0.30; I.append((ox+c0[0]+ri*math.cos(t),oy+c0[1]+ri*math.sin(t)))
    lay=Image.new("RGBA",(D,D),(0,0,0,0)); w=D*0.0075
    E=[]
    for i in range(len(O)-1): E+=[(O[i],O[i+1]),(I[i],I[i+1]),(O[i],I[i+1]),(I[i],O[i+1])]
    for i in range(1,len(O)-1): E.append((O[i],I[i]))
    for p,q in E: lay.alpha_composite(metal_line(D,p,q,w,(170,215,250)))
    out.alpha_composite(shadow(lay.split()[-1],size,0.008,0.006,0.5)); out.alpha_composite(lay)
    P=O+I
    for p in P:
        r=D*0.019; sp=sphere(r,(200,230,255)); gl=Image.new("RGBA",sp.size,(0,0,0,0))
        out.alpha_composite(sp,(int(p[0]-sp.width/2),int(p[1]-sp.height/2)))
    return out.resize((size,size),Image.LANCZOS)
# ---- concept 2: transparent glass sphere with chrome armillary rings around real moon
def c2(size=512):
    D=size*S; orb,cov=glass_orb(size,mix(ACC,(255,255,255),0.5),mix(ACC,(0,10,40),0.62))
    out=Image.new("RGBA",(D,D),(0,0,0,0)); out.alpha_composite(shadow(cov,size)); out.alpha_composite(orb)
    m=moon_light(moon_scaled(D*0.56)); place(out,m,D*0.5,D*0.52)
    ring=Image.new("RGBA",(D,D),(0,0,0,0)); dr=ImageDraw.Draw(ring)
    cx=cy=D/2; R=D*0.40
    def band(box,w):
        l=Image.new("RGBA",(D,D),(0,0,0,0)); d_=ImageDraw.Draw(l)
        d_.ellipse(box,outline=(40,90,130,255),width=int(w))
        d_.ellipse([box[0]+w*.25,box[1]+w*.25,box[2]-w*.25,box[3]-w*.25],outline=(190,225,250,255),width=int(w*.55))
        # highlight arc upper-left
        d_.arc([box[0]+w*.2,box[1]+w*.2,box[2]-w*.2,box[3]-w*.2],200,300,fill=(255,255,255,255),width=max(1,int(w*.2)))
        return l
    w=D*0.012
    for k in (0.35,0.7):      # meridians
        ring.alpha_composite(band([cx-R*k,cy-R,cx+R*k,cy+R],w))
    # equator tilt: ellipse
    ring.alpha_composite(band([cx-R,cy-R*0.28,cx+R,cy+R*0.28],w))
    out.alpha_composite(shadow(ring.split()[-1],size,0.01,0.007,0.5)); out.alpha_composite(ring)
    # nodes at ring crossings
    for (x,y) in [(cx,cy-R),(cx,cy+R),(cx-R,cy),(cx+R,cy),(cx-R*.7,cy-R*.28*.7),(cx+R*.7,cy+R*.28*.7)]:
        sp=sphere(D*0.017,(215,238,255)); out.alpha_composite(sp,(int(x-sp.width/2),int(y-sp.height/2)))
    return out.resize((size,size),Image.LANCZOS)
# ---- concept 3: deep glass, glowing real moon, orbiting light-node network
def c3(size=512):
    D=size*S; orb,cov=glass_orb(size,mix(ACC,(0,0,0),0.45),mix(ACC,(0,0,0),0.86))
    out=Image.new("RGBA",(D,D),(0,0,0,0)); out.alpha_composite(shadow(cov,size)); out.alpha_composite(orb)
    m=moon_light(moon_scaled(D*0.58)); cx,cy=D*0.5,D*0.52
    # moon glow
    pad_=int(D*0.15); mp=Image.new('RGBA',(m.width+2*pad_,m.height+2*pad_),(0,0,0,0)); mp.alpha_composite(m,(pad_,pad_))
    a=mp.split()[-1].filter(ImageFilter.GaussianBlur(D*0.04)).point(lambda v:int(v*0.9))
    gl=Image.new('RGBA',(D,D),(0,0,0,0)); tmp=Image.new('RGBA',mp.size,mix(ACC,(255,255,255),0.5)+(255,)); tmp.putalpha(a)
    place(gl,tmp,cx,cy); out.alpha_composite(gl); place(out,m,cx,cy)
    # orbit network: nodes on two tilted ellipses with light-trail strands
    lay=Image.new("RGBA",(D,D),(0,0,0,0)); dr=ImageDraw.Draw(lay)
    nodes=[]
    for (rx,ry,tilt,ts) in [(0.43,0.17,-0.5,[0.3,2.0,3.9,5.4]),(0.36,0.33,0.7,[1.0,2.9,4.8])]:
        pts=[]
        for t in np.linspace(0,2*math.pi,200):
            x=rx*math.cos(t); y=ry*math.sin(t)
            xr=x*math.cos(tilt)-y*math.sin(tilt); yr=x*math.sin(tilt)+y*math.cos(tilt)
            pts.append((cx+xr*D*0.98,cy+yr*D*0.98))
        dr.line(pts+[pts[0]],fill=(200,230,255,120),width=max(1,int(D*0.0035)))
        for t in ts:
            x=rx*math.cos(t); y=ry*math.sin(t)
            nodes.append((cx+(x*math.cos(tilt)-y*math.sin(tilt))*D*0.98,cy+(x*math.sin(tilt)+y*math.cos(tilt))*D*0.98))
    for i in range(len(nodes)):
        for j in range(i+1,len(nodes)):
            if math.dist(nodes[i],nodes[j])<D*0.38: dr.line([nodes[i],nodes[j]],fill=(220,240,255,150),width=max(1,int(D*0.0028)))
    out.alpha_composite(lay.filter(ImageFilter.GaussianBlur(D*0.004))); out.alpha_composite(lay)
    for p in nodes:
        gg=Image.new("RGBA",(D,D),(0,0,0,0)); ImageDraw.Draw(gg).ellipse([p[0]-D*.03,p[1]-D*.03,p[0]+D*.03,p[1]+D*.03],fill=(150,210,255,170))
        out.alpha_composite(gg.filter(ImageFilter.GaussianBlur(D*0.012)))
        sp=sphere(D*0.017,(235,247,255)); out.alpha_composite(sp,(int(p[0]-sp.width/2),int(p[1]-sp.height/2)))
    return out.resize((size,size),Image.LANCZOS)
ic=[c1(),c2(),c3()]
W,H=1500,860
col=np.zeros((H,W,3),np.uint8); t=np.linspace(0,1,H)[:,None]
for i,(a,b) in enumerate(zip((26,62,98),(10,20,36))): col[:,:,i]=(a+(b-a)*t).astype(np.uint8)
img=Image.fromarray(col,"RGB"); d=ImageDraw.Draw(img)
f2=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
names=["1  real moon + metal network on glass","2  real moon in glass globe, chrome rings","3  glowing moon, orbiting light network"]
for i,x in enumerate(ic):
    X=40+i*490; d.text((X,20),names[i],font=f2,fill=(235,240,245))
    big=x.resize((440,440),Image.LANCZOS); img.paste(big,(X,70),big)
    for j,s in enumerate((96,48,32)):
        sm=x.resize((s,s),Image.LANCZOS); img.paste(sm,(X+20+j*140,560),sm)
    d.text((X+20,680),"96 / 48 / 32 px",font=f2,fill=(160,175,190))
img.save("/downloads/browser_icon_proof2.png")
for i,x in enumerate(ic): x.save(f"/tmp/bicon_c{i+1}.png")
