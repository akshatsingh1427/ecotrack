import math,datetime
FUEL={'petrol':2.31,'diesel':2.68,'cng':2.0,'ev':0}  # kg CO2 per litre / kg
GRID=0.82  # kg CO2/kWh (India grid avg)
# mode: (kgCO2/km/passenger, km/h, Rs/km)
MODES={'walk':(0,5,0),'bicycle':(0,15,0),'metro':(0.03,35,1.5),'train':(0.04,45,1.0),'bus':(0.08,20,1.2),'motorcycle':(0.1,30,3),'car':(None,30,8)}
LIMIT={'walk':3,'bicycle':10}  # max sensible km
def haversine(a,b,c,d):
    r=6371;p=math.radians;dl=p(c-a);dn=p(d-b)
    h=math.sin(dl/2)**2+math.cos(p(a))*math.cos(p(c))*math.sin(dn/2)**2
    return 2*r*math.asin(math.sqrt(h))*1.3  # 1.3 road factor
def car_rate(pr):
    if pr.fuel=='ev':return 0.12*GRID
    if pr.fuel not in FUEL:return 0.192
    age=max(0,datetime.date.today().year-pr.vehicle_year-5)
    eff=pr.kmpl*(1-min(0.2,age*0.01))  # older engines lose efficiency
    return FUEL[pr.fuel]/eff
def rate(pr,m):return car_rate(pr) if m=='car' else MODES[m][0]
def best_alt(pr,mode,km):
    t0=km/MODES[mode][1];c0=km*MODES[mode][2];r0=rate(pr,mode);best=None
    for m in MODES:
        if m==mode or km>LIMIT.get(m,1e9):continue
        r=rate(pr,m);t=km/MODES[m][1];c=km*MODES[m][2]
        if r<r0 and t<=t0*1.3 and c<=c0:
            if not best or r<best[1]:best=(m,r,t,c)
    return best
FOODS={'Chicken curry':(2.9,'meal','Try chickpea/soy curry with same spices'),'Mutton curry':(9.5,'meal','Try rajma or paneer curry'),
'Paneer dish':(1.8,'meal','Tofu or dal makhani is lower impact'),'Dal rice':(0.9,'meal','Already low; use seasonal vegetables'),
'Rajma chawal':(0.8,'meal','Already low impact'),'Veg biryani':(1.0,'meal','Use local veggies, less ghee'),
'Chicken burger':(6.0,'fast','Veggie burger/aloo tikki saves most'),'Cheese pizza':(1.7,'fast','Veg-topped thin crust'),'Veg burger':(0.7,'fast','Great choice'),
'Packaged chips':(0.5,'snack','Roasted chana / fruit'),'Chocolate bar':(1.2,'snack','Local jaggery/peanut chikki'),'Fruit':(0.3,'snack','Great choice'),'Roasted chana':(0.2,'snack','Great choice')}
APPL={'AC':1.5,'Ceiling fan':0.07,'Room heater':2.0,'Refrigerator':0.15,'Washing machine':0.5,'TV':0.1,'LED light':0.01,'Geyser':2.0}
BUY={'Smartphone':70,'Laptop':300,'Clothing item':15,'Furniture piece':90,'Book':2.5,'Shoes':14}
import re
APPL={'AC':(1.5,'Set 24-26°C, clean filters monthly, use a fan alongside.'),'Ceiling fan':(0.07,'BLDC fans use about half the power.'),'Room heater':(2.0,'Insulate windows; use only in the room you occupy.'),
'Refrigerator':(0.15,'Keep it 3/4 full, door seals tight, away from heat.'),'Washing machine':(0.5,'Full loads, cold wash, air dry.'),'TV':(0.1,'Turn off standby; lower brightness.'),
'LED light':(0.01,'Already efficient; switch off when leaving.'),'Geyser':(2.0,'Use a timer; 50°C is enough; solar heater is better.'),'Computer/Laptop':(0.08,'Enable sleep; laptops use far less than desktops.'),
'Water pump':(0.75,'Fill tanks in one go; fix leaks.'),'Microwave/Induction':(1.2,'Cover pots and use right-sized vessels.'),'Air cooler':(0.2,'Cuts about 80% power versus AC for dry climates.')}
LB={'Chocolate':5,'Biscuits':1.6,'Chips/Namkeen':2.5,'Instant noodles':1.8,'Packaged juice':1.0,'Milk drink':1.4,'Breakfast cereal':1.2,'Ice cream':3.5,'Other packaged food':2.0}
ALTS={'Chocolate':['Dark chocolate 70%+ with few ingredients and no palm oil','Dates with nuts or jaggery-peanut chikki (local, plant-based)'],
'Biscuits':['Whole-wheat/ragi biscuits with no palm oil','Roasted makhana or homemade oats cookies'],'Chips/Namkeen':['Roasted chana or air-popped makhana','Baked multigrain snacks (low salt)'],
'Instant noodles':['Whole-grain noodles with vegetables','Poha or vegetable upma (local and quick)'],'Packaged juice':['Whole seasonal fruit (fibre, no added sugar)','Nimbu pani or coconut water'],
'Milk drink':['Unsweetened milk, lassi or buttermilk','Soy/oat drink with no added sugar'],'Breakfast cereal':['Plain oats or muesli with no added sugar','Idli, dalia or poha'],
'Ice cream':['Fruit popsicle or frozen curd','Kulfi made at home with less sugar'],'Other packaged food':['Fresh local seasonal alternatives','Look for fewer ingredients and short shelf-life products']}
FLAGS=[('palm','Palm oil (deforestation)',8,0.10),('hydrogenated','Hydrogenated fat',12,0.0),('high fructose','High-fructose syrup',10,0.0),('maida','Refined flour (maida)',5,0.0),
('refined wheat','Refined flour',5,0.0),('colour','Artificial colour',6,0.0),('e1','Colour additive (E1xx)',4,0.0),('flavour','Added flavouring',3,0.0),('preservative','Preservative',4,0.0),
('milk','Dairy (higher footprint)',0,0.15),('butter','Dairy (higher footprint)',0,0.15),('cheese','Dairy (higher footprint)',0,0.20),('cocoa','Cocoa',0,0.05)]
def num(t,pats):
    for p in pats:
        m=re.search(p+r'[^0-9\n]{0,20}(\d+(?:\.\d+)?)',t)
        if m:return float(m.group(1))
def analyze(text,cat,grams):
    t=text.lower();v={'sugar':num(t,['sugars?']),'satfat':num(t,['saturated fat','saturates','sat\\.? fat']),'protein':num(t,['protein']),'fibre':num(t,['fibre','fiber'])}
    sod=num(t,['sodium']);salt=num(t,['salt']);v['salt']=salt if salt is not None else (sod*2.5/1000 if sod is not None else None)
    sc=70;why=[]
    s=v['sugar']
    if s is not None:
        if s>22.5:sc-=30;why.append(f'Very high sugar ({s:g} g/100g)')
        elif s>10:sc-=15;why.append(f'High sugar ({s:g} g/100g)')
    if v['satfat'] and v['satfat']>5:sc-=15;why.append(f'High saturated fat ({v["satfat"]:g} g)')
    if v['salt'] and v['salt']>1.5:sc-=10;why.append('High salt')
    if v['protein'] and v['protein']>=10:sc+=10;why.append('Good protein')
    if v['fibre'] and v['fibre']>=5:sc+=10;why.append('Good fibre')
    mult=1.0;seen=set()
    for k,l,pen,m in FLAGS:
        if k in t and l not in seen:seen.add(l);sc-=pen;mult+=m;why.append(l) if pen or m else 0
    sc=max(0,min(100,sc));co=LB.get(cat,2.0)*mult*grams/1000
    verdict='Better choice' if sc>=65 else ('Okay in moderation' if sc>=40 else 'Choose something else')
    return dict(score=sc,verdict=verdict,why=why,vals={k:x for k,x in v.items() if x is not None},co2=co,alts=ALTS.get(cat,[]),missing=[k for k,x in v.items() if x is None])

# ---------- v3 label engine ----------
ALT2={'Chocolate':[('Dark chocolate 70%+, short ingredient list, no palm oil',66,4.2),('Dates with roasted nuts',82,1.2),('Jaggery-peanut chikki',68,1.4)],
'Biscuits':[('Whole-wheat/ragi biscuits, no palm oil',62,1.2),('Roasted makhana or homemade oat cookies',78,0.9)],
'Chips/Namkeen':[('Roasted chana or makhana',80,0.9),('Baked multigrain snack, low salt',58,1.6)],
'Instant noodles':[('Whole-grain noodles with vegetables',64,1.2),('Poha or vegetable upma',78,0.8)],
'Packaged juice':[('Whole seasonal fruit',90,0.4),('Nimbu pani or coconut water',80,0.5)],
'Milk drink':[('Plain lassi or buttermilk',74,1.0),('Unsweetened soy/oat drink',70,0.9)],
'Breakfast cereal':[('Plain oats or muesli, no added sugar',80,0.9),('Idli, dalia or poha',78,0.8)],
'Ice cream':[('Frozen fruit popsicle',60,0.6),('Home-made low-sugar kulfi',45,2.5)],
'Other packaged food':[('Fresh local seasonal food',85,0.6),('Product with under 5 ingredients',70,1.2)]}
SUG=['sugar','glucose','fructose','syrup','dextrose','maltodextrin','invert','molasses']
FL=[(r'palm','Palm oil (linked to deforestation)',-8,.10),(r'hydrogenated','Hydrogenated fat',-12,0),(r'high.?fructose|corn syrup','Corn/fructose syrup',-10,0),
(r'maida|refined (wheat )?flour|enriched flour','Refined flour',-5,0),(r'colou?r','Added colour',-5,0),(r'flavou?r','Added flavouring',-3,0),(r'preservative|sorbate|benzoate','Preservatives',-3,0),
(r'monosodium|\bmsg\b|flavou?r enhancer|\be621\b|ins ?621','Flavour enhancer (MSG)',-4,0),(r'aspartame|sucralose|acesulfame|saccharin|\be95\d','Artificial sweetener',-4,0),
(r'milk|butter|ghee|cream|whey|casein|milk solids','Dairy (higher footprint)',0,.15),(r'cheese','Cheese (high footprint)',0,.20),(r'chicken|mutton|beef|gelatin|meat','Animal-based ingredient',0,.30),
(r'vegan|plant.?based','Plant-based',0,-.10)]
WH=[r'whole ?(wheat|grain)',r'\boats?\b',r'millet|ragi|jowar|bajra',r'almond|peanut|cashew|nuts?\b',r'\bdates?\b',r'no added sugar|unsweetened']
def analyze(text,cat,grams):
    t=re.sub(r'(\d),(\d)',r'\1.\2',text.lower())
    if len(re.sub(r'\W','',t))<12:return None
    def n(ps):
        for p in ps:
            m=re.search(p+r'[^0-9\n,;]{0,16}?(\d+(?:\.\d+)?)',t)
            if m:return float(m.group(1))
    v={'sugar':n(['total sugars?','sugars?']),'satfat':n(['saturated fat(?:ty acids)?','saturates','sat\\.? ?fat']),'protein':n(['protein']),'fibre':n(['dietary fib(?:re|er)','fib(?:re|er)'])}
    sod=n(['sodium']);sal=n(['salt']);v['salt']=sal if sal is not None else (None if sod is None else (sod*2.5/1000 if sod>5 else sod*2.5))
    k=re.search(r'(\d+(?:\.\d+)?)\s*kcal',t);kc=float(k.group(1)) if k else n(['energy','calories'])
    if kc and kc>1200:kc=kc/4.184
    v['kcal']=kc
    m=re.search(r'ingredients?\s*[:\-]?\s*(.+?)(?=nutrition|nutritional|allergen|contains|energy|per 100|$)',t,re.S)
    ing=m.group(1) if m else '';items=[x.strip() for x in re.split(r'[,;]',re.sub(r'\([^)]*\)','',ing)) if x.strip()]
    found={k:x for k,x in v.items() if x is not None}
    if not found and not items:return None
    rs=[]
    def R(txt,dl):
        if abs(dl)>=0.5:rs.append((txt,round(dl)))
    s=v['sugar']
    if s is not None:R(f'Sugar {s:g} g per 100 g',-min(35,s*.7))
    if v['satfat'] is not None:R(f'Saturated fat {v["satfat"]:g} g',-min(20,v['satfat']*1.5))
    if v['salt'] is not None:R(f'Salt {v["salt"]:.2f} g',-min(15,v['salt']*6))
    if kc and kc>300:R(f'Energy dense ({kc:.0f} kcal)',-min(10,(kc-300)/40))
    if v['protein']:R(f'Protein {v["protein"]:g} g',min(12,v['protein']))
    if v['fibre']:R(f'Fibre {v["fibre"]:g} g',min(12,v['fibre']*2))
    ni=len(items)
    if ni>8:R(f'Long ingredient list ({ni}) - ultra-processed',-min(12,(ni-8)*1.2))
    elif 0<ni<=5:R(f'Short ingredient list ({ni})',5)
    if items and any(x in items[0] for x in SUG):R('Sugar is the first (main) ingredient',-8)
    sn=sum(any(x in i for x in SUG) for i in items)
    if sn>=3:R(f'Sugar hidden under {sn} names',-6)
    en=len(re.findall(r'\be ?\d{3}[a-z]?\b|\bins ?\d{3}',t))
    if en:R(f'{en} E-number additive(s)',-min(10,2*en))
    mult=1.0
    for p,l,dl,cm in FL:
        if re.search(p,t):R(l,dl);mult+=cm
    wh=sum(bool(re.search(p,t)) for p in WH)
    if wh:R('Wholesome ingredients (grains/nuts/fruit)',min(12,wh*3))
    sc=int(max(0,min(100,75+sum(d for _,d in rs))))
    gr='A' if sc>=75 else 'B' if sc>=60 else 'C' if sc>=45 else 'D' if sc>=30 else 'E'
    base=LB.get(cat,2.0)/10;c100=base*max(.6,mult)
    alts=[dict(name=a,score=s2,co=c/10,dh=s2-sc,dc=round(100*((c/10)-c100)/c100)) for a,s2,c in ALT2.get(cat,[]) if s2>sc or c/10<c100]
    return dict(score=sc,grade=gr,verdict='Better choice' if sc>=65 else 'Okay in moderation' if sc>=40 else 'Choose something else',reasons=rs,found=found,items=items[:12],
      co100=c100,typ=base,pct=round(100*(c100-base)/base),co2=c100*grams/100,alts=alts,conf=min(100,len(found)*18+(28 if items else 0)))
