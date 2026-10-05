import datetime,io
from django.shortcuts import render,redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum,Count
from django.utils import timezone
from .models import *
from . import engine as e
def register(r):
    if r.method=='POST':
        d=r.POST
        if User.objects.filter(username=d['username']).exists():return render(r,'core/register.html',{'err':'Username taken'})
        u=User.objects.create_user(d['username'],password=d['password'],first_name=d['name'])
        org=None
        if d.get('org'):org,_=Organisation.objects.get_or_create(name=d['org'].strip())
        Profile.objects.create(user=u,org=org,is_admin=bool(d.get('admin')),age=d['age'],weight=d['weight'],fuel=d['fuel'],kmpl=d.get('kmpl') or 15,vehicle_year=d.get('year') or 2018)
        login(r,u);return redirect('dash')
    return render(r,'core/register.html')
def ocr(f):
    data=f.read()
    try:
        from rapidocr_onnxruntime import RapidOCR
        res,_=RapidOCR()(data)
        if res:
            res=sorted(res,key=lambda x:x[0][0][1]);rows=[]
            for b,t,s in res:
                y=b[0][1]
                if rows and abs(rows[-1][0]-y)<14:rows[-1][1].append((b[0][0],t))
                else:rows.append([y,[(b[0][0],t)]])
            return '\n'.join(' '.join(t for _,t in sorted(x[1])) for x in rows),'RapidOCR'
    except Exception:pass
    try:
        import pytesseract;from PIL import Image
        return pytesseract.image_to_string(Image.open(io.BytesIO(data))),'Tesseract'
    except Exception:pass
    return '',None
def streak(u):
    ds=set(Activity.objects.filter(user=u).values_list('created__date',flat=True));d=timezone.localdate();n=0
    if d not in ds:d-=datetime.timedelta(days=1)
    while d in ds:n+=1;d-=datetime.timedelta(days=1)
    return n
def dashboard(r):
    if not r.user.is_authenticated:
        A=Activity.objects.aggregate(t=Sum('co2'),v=Sum('avoided'),n=Count('id'))
        return render(r,'core/landing.html',{'st':{'u':User.objects.count(),'n':A['n'],'v':round(A['v'] or 0,1),'t':round(A['t'] or 0,1)},'modes':[(k,e.MODES[k][0] if k!='car' else 0.192) for k in e.MODES]})
    today=timezone.localdate()
    try:day=datetime.date.fromisoformat(r.GET.get('date',''))
    except ValueError:day=today
    a=Activity.objects.filter(user=r.user,created__date=day).order_by('created')
    parts=[('🌅 Morning',0),('☀️ Afternoon',1),('🌇 Evening',2),('🌙 Night',3)];tl=[]
    idx=lambda h:0 if 5<=h<12 else 1 if 12<=h<17 else 2 if 17<=h<21 else 3
    rows=[(timezone.localtime(x.created),x) for x in a]
    for n,i in parts:
        it=[(t.strftime('%I:%M %p'),x) for t,x in rows if idx(t.hour)==i];tl.append((n,it,sum(x.co2 for _,x in it)))
    tot=a.aggregate(t=Sum('co2'),v=Sum('avoided'));T=tot['t'] or 0
    cats=list(a.values('category').annotate(t=Sum('co2'),v=Sum('avoided')))
    wl,wc,wa=[],[],[]
    for i in range(6,-1,-1):
        d=today-datetime.timedelta(days=i);q=Activity.objects.filter(user=r.user,created__date=d).aggregate(t=Sum('co2'),v=Sum('avoided'))
        wl.append(d.strftime('%a %d'));wc.append(round(q['t'] or 0,2));wa.append(round(q['v'] or 0,2))
    allt=Activity.objects.filter(user=r.user).aggregate(v=Sum('avoided'),n=Count('id'));av=allt['v'] or 0;cnt=allt['n'];st=streak(r.user);pts=int(av*10+cnt*5)
    lvl='🌱 Seedling' if pts<100 else '🌿 Sapling' if pts<500 else '🌳 Tree' if pts<1500 else '🌲 Forest'
    badges=[('🌱','First log',cnt>=1),('♻️','1 kg avoided',av>=1),('🔥','3-day streak',st>=3),('🚴','10 activities',cnt>=10),('🌳','10 kg avoided',av>=10),('🏆','7-day streak',st>=7)]
    ch={'cat':{'l':[c['category'].title() for c in cats],'d':[round(c['t'],2) for c in cats]},'wk':{'l':wl,'c':wc,'a':wa}}
    return render(r,'core/dash.html',{'day':day,'is_today':day==today,'tl':tl,'tot':tot,'charts':ch,'pts':pts,'lvl':lvl,'streak':st,'badges':badges,'prev':day-datetime.timedelta(days=1),'next':day+datetime.timedelta(days=1)})
@login_required
def log(r,cat):
    p=r.user.profile;res=None;d=r.POST;lab=None;err=None
    if r.method=='POST':
      try:
        if cat=='transport':
            km=float(d['km']) if d.get('km') else e.haversine(*[float(d[k]) for k in('alat','alon','blat','blon')])
            m=d['mode'];co=e.rate(p,m)*km;av=max(0,e.car_rate(p)*km-co) if m!='car' else 0
            alt=e.best_alt(p,m,km);cal=0
            if m in('walk','bicycle'):cal=(3.5 if m=='walk' else 6.8)*p.weight*km/e.MODES[m][1]
            res={'title':f'{km:.1f} km by {m}','co2':co,'av':av,'cal':cal,'tip':(f'Better: {alt[0]} - {alt[1]*km:.2f} kg, {alt[2]*60:.0f} min, Rs {alt[3]:.0f} (no slower/costlier than yours)' if alt else 'No cleaner option that is also as fast and cheap - good choice.')}
            Activity.objects.create(user=r.user,category=cat,label=res['title'],co2=co,avoided=av)
        elif cat=='food':
            n=d['item'];kg,g,tip=e.FOODS[n];por=float(d['portion']);co=kg*por
            alts=sorted([(k,v[0]*por) for k,v in e.FOODS.items() if v[1]==g and v[0]<kg],key=lambda x:x[1])[:3]
            res={'title':f'{n} x{por}','co2':co,'av':0,'tip':'Recipe tip: '+tip+('. Swap options: '+', '.join(f'{k} ({c:.2f} kg)' for k,c in alts) if alts else '')}
            Activity.objects.create(user=r.user,category=cat,label=res['title'],co2=co)
        elif cat=='label':
            txt=d.get('text','');eng=None
            if r.FILES.get('photo'):
                t2,eng=ocr(r.FILES['photo']);txt=(txt+'\n'+t2).strip()
                if not t2:err='Could not read the photo. Install OCR (py -m pip install rapidocr-onnxruntime) or paste the label text instead.'
            if not err:
                lab=e.analyze(txt,d['cat'],float(d.get('grams') or 100))
                if lab is None:err='No nutrition values or ingredients found. Paste text like "Ingredients: ... Sugars 12 g, Fat 20 g" or upload a clearer photo.'
                else:
                    lab['name']=d.get('pname') or d['cat'];lab['engine']=eng;lab['text']=txt[:400]
                    Activity.objects.create(user=r.user,category='label',label=f'{lab["name"]} ({d.get("grams") or 100} g): {lab["verdict"]}',co2=lab['co2'])
        elif cat=='energy':
            n=d['item'];kw,tip=e.APPL[n];h=float(d['hours']);q=int(d['qty']);st=int(d['star']);base=kw*h*q
            f=1.3-0.1*st;k=base*f;tips=[tip]
            if n=='AC':
                t=float(d['temp']);k0=k;k*=max(0,1+0.06*(24-t))
                if t<24:tips.append(f'Raising from {t:g}°C to 24°C saves about {k-k0:.2f} kWh today.')
                elif t<26:tips.append('Going to 26°C would save roughly another 12%.')
                else:tips.append('Great setpoint.')
            if st<5:tips.append(f'A 5-star model would save about {(f-0.8)*base:.2f} kWh per day of this use.')
            co=k*e.GRID;res={'title':f'{q} x {n}, {h:g} h ({k:.1f} kWh)','co2':co,'av':0,'tip':' '.join(tips)}
            Activity.objects.create(user=r.user,category=cat,label=res['title'],co2=co)
        else:
            n=d['item'];q=int(d['qty']);new=d['cond']=='new';base=e.BUY[n]*q;co=base if new else base*0.2
            res={'title':f'{q} x {n} ({d["cond"]})','co2':co,'av':base-co,'tip':'Second-hand/refurbished cuts ~80% of embodied carbon.' if new else 'Great: reuse avoided new manufacturing.'}
            Activity.objects.create(user=r.user,category=cat,label=res['title'],co2=co,avoided=base-co)
      except (ValueError,KeyError,TypeError,ZeroDivisionError):
        err=err or 'Please fill all fields correctly (for transport: a distance, or all four coordinates).'
    return render(r,'core/log.html',{'cat':cat,'res':res,'lab':lab,'err':err,'modes':e.MODES,'foods':e.FOODS,'appl':e.APPL,'buy':e.BUY,'lbcats':e.LB})
def board(org=None):
    q=Activity.objects.all()
    if org:q=q.filter(user__profile__org=org)
    return q.values('user__first_name').annotate(v=Sum('avoided'),t=Sum('co2'),n=Count('id')).order_by('-v')[:10]
@login_required
def leaderboard(r):
    o=r.user.profile.org
    return render(r,'core/lb.html',{'g':board(),'o':board(o) if o else None})
@login_required
def company(r):
    org=r.user.profile.org
    if not org or not r.user.profile.is_admin:return render(r,'core/lb.html',{'denied':True})
    a=Activity.objects.filter(user__profile__org=org);emp=Profile.objects.filter(org=org).count();act=a.values('user').distinct().count()
    tot=a.aggregate(t=Sum('co2'),v=Sum('avoided'));cats=list(a.values('category').annotate(t=Sum('co2'),v=Sum('avoided')));top=list(board(org))
    today=timezone.localdate();tl,tc,ta=[],[],[]
    for i in range(13,-1,-1):
        d=today-datetime.timedelta(days=i);q=a.filter(created__date=d).aggregate(t=Sum('co2'),v=Sum('avoided'));tl.append(d.strftime('%d %b'));tc.append(round(q['t'] or 0,2));ta.append(round(q['v'] or 0,2))
    ch={'cat':{'l':[c['category'].title() for c in cats],'t':[round(c['t'],2) for c in cats],'v':[round(c['v'],2) for c in cats]},'top':{'l':[x['user__first_name'] for x in top],'d':[round(x['v'],2) for x in top]},'tr':{'l':tl,'c':tc,'a':ta}}
    return render(r,'core/company.html',{'org':org,'emp':emp,'active':act,'part':round(100*act/emp) if emp else 0,'per':round((tot['v'] or 0)/act,2) if act else 0,'tot':tot,'top':top,'charts':ch})
