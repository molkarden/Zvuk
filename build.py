#!/usr/bin/env python3
"""Генератор статического сайта «Живой звук» (афиша концертов).

Запуск:  python3 build.py        -> готовый сайт в папке dist/
Данные:  data/events.json         -> список концертов (правится вручную)
Переменные окружения (все необязательные):
  SITE_URL       полный адрес сайта, например https://user.github.io/repo
                 (путь /repo определяется из него автоматически)
  BUILD_DATE     дата сборки YYYY-MM-DD (по умолчанию сегодня);
                 концерты с более ранней датой в сайт не попадают
  YM_ID          номер счётчика Яндекс Метрики (если пусто, счётчика нет)
  YANDEX_VERIFY  код подтверждения Яндекс Вебмастера
"""
import os,re,json,html,random,shutil,hashlib,datetime as dt
from urllib.parse import urlparse
H=html.escape
SITE=os.environ.get("SITE_URL","https://example.github.io/zhivoy-zvuk").rstrip("/")
BP=urlparse(SITE).path.rstrip("/")
YM=os.environ.get("YM_ID",""); VERIFY=os.environ.get("YANDEX_VERIFY","")
BRAND="Живой звук"
BASE=dt.date.fromisoformat(os.environ["BUILD_DATE"]) if os.environ.get("BUILD_DATE") else dt.date.today()


HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(HERE,"dist")
MON=["января","февраля","марта","апреля","мая","июня","июля","августа","сентября","октября","ноября","декабря"]
MS=["янв","фев","мар","апр","мая","июн","июл","авг","сен","окт","ноя","дек"]; WD=["пн","вт","ср","чт","пт","сб","вс"]
fd=lambda d:f"{d.day} {MON[d.month-1]}"; fdw=lambda d:f"{d.day} {MS[d.month-1]}, {WD[d.weekday()]}"
rub=lambda n:f"{n:,}".replace(","," ")+" ₽"
_t=dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",["a","b","v","g","d","e","e","zh","z","i","y","k","l","m","n","o","p","r","s","t","u","f","h","c","ch","sh","sch","","y","","e","yu","ya"]))
tr=lambda s:re.sub(r"[^a-z0-9]+","-","".join(_t.get(c,c) for c in s.lower())).strip("-")
CN={"moskva":"Москва","sankt-peterburg":"Санкт-Петербург","tula":"Тула","kaluga":"Калуга","voronezh":"Воронеж","ekaterinburg":"Екатеринбург"}
CI={"moskva":"в Москве","sankt-peterburg":"в Санкт-Петербурге","tula":"в Туле","kaluga":"в Калуге","voronezh":"в Воронеже","ekaterinburg":"в Екатеринбурге"}
GN={"rok":"Рок","hip-hop":"Хип-хоп","klassika":"Классическая музыка","dzhaz":"Джаз и блюз","pop":"Поп","elektronika":"Электронная музыка","indi":"Инди"}
GB={"rok":"Гитарные риффы, мощные барабаны и зал, который поёт хором.","hip-hop":"Тексты, бит и энергия живого выступления.","klassika":"Оркестры, камерные составы и вечера при свечах.","dzhaz":"Импровизация, живые инструменты и камерные клубы.","pop":"Хиты, большие шоу и сольные программы.","elektronika":"Клубные live-сеты, свет и звук на полную мощность.","indi":"Новые имена, альбомные программы и уютные клубы."}
GC={"rok":("#ff6b81","#5b1252"),"hip-hop":("#ffb347","#7a1f1f"),"klassika":("#7cc4ff","#1b2a7a"),"dzhaz":("#4fd1c5","#0f3a6b"),"pop":("#ff8fd0","#4a1a8f"),"elektronika":("#a78bfa","#10226b"),"indi":("#c6f068","#0f4a3c")}
VN={"kluby":"Клубы","kontsertnye-zaly":"Концертные залы","stadiony":"Стадионы","open-air":"Open-air"}
DT={"segodnya":("today","Концерты сегодня"),"zavtra":("tomorrow","Концерты завтра"),"vyhodnye":("weekend","Концерты на выходных"),"etot-mesyac":("month","Концерты в этом месяце")}

DATA=json.load(open(os.path.join(HERE,"data","events.json"),encoding="utf-8"))
CHECKED=dt.date.fromisoformat(DATA["checked"])
EV=[]
for x in DATA["events"]:
    d=dt.date.fromisoformat(x["date"])
    if d<BASE: continue
    EV.append(dict(artist=x["artist"],tour=x.get("tour",""),g=x["genre"],c=x["city"],v=x["venue"],vt=x["vt"],d=d,tm=x.get("time"),pr=x.get("price"),age=x.get("age",""),url=x["url"],slug=tr(f"{x['artist']}-{x['city']}-{x['date']}")))
EV.sort(key=lambda e:(e["d"],e["tm"] or ""))
if not EV: raise SystemExit("В data/events.json нет предстоящих концертов: добавьте новые даты.")
CN={k:v for k,v in CN.items() if any(e["c"]==k for e in EV)}
GN={k:v for k,v in GN.items() if any(e["g"]==k for e in EV)}
VN={k:v for k,v in VN.items() if any(e["vt"]==k for e in EV)}
ttl=lambda e:f"{e['artist']} — {e['tour']}" if e["tour"] else e["artist"]
ARTISTS=sorted({e["artist"] for e in EV})
PAGES={}


def poster(e):
    a,b=GC[e["g"]]; r=random.Random(e["slug"]); out,cur=[],""
    for w in e["artist"].split():
        if cur and len(cur+" "+w)>13: out.append(cur); cur=w
        else: cur=(cur+" "+w).strip()
    L=(out+[cur])[:3]; y0=410-44*(len(L)-1)
    sh="".join(f'<circle cx="{r.randint(0,400)}" cy="{r.randint(0,300)}" r="{r.randint(30,130)}" fill="#fff" opacity="{r.uniform(.08,.26):.2f}"/>' for _ in range(5))
    bars="".join(f'<rect x="{14+i*20}" y="{320-h}" width="12" height="{h}" rx="6" fill="#fff" opacity=".85"/>' for i,h in enumerate(r.randint(30,150) for _ in range(19)))
    ts="".join(f'<tspan x="24" dy="{0 if i==0 else 44}">{H(l)}</tspan>' for i,l in enumerate(L))
    f='font-family="Arial,Helvetica,sans-serif" fill="#fff"'
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500"><defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/><stop offset=".6" stop-color="{b}"/><stop offset="1" stop-color="#0b0830"/></linearGradient></defs><rect width="400" height="500" fill="url(#g)"/>{sh}{bars}<text x="24" y="{y0}" {f} font-weight="900" font-size="40">{ts}</text><text x="24" y="450" {f} font-size="19" opacity=".9">{H(e["tour"])}</text><text x="24" y="478" {f} font-size="17" font-weight="700">{fd(e["d"])}, {CN[e["c"]]}</text></svg>'
LOGO='<svg viewBox="0 0 36 36" aria-hidden="true"><rect width="36" height="36" rx="10" fill="#ff4d6d"/><path d="M9 22v-8M14 26V10M19 20v-4M24 24V12M29 21v-6" stroke="#120e38" stroke-width="3" stroke-linecap="round" fill="none"/></svg>'

def ptxt(e): return "от "+rub(e["pr"]) if e["pr"] else "цена у продавца"
def card(e):
    u=f"/koncert/{e['slug']}/"; t=ttl(e)
    k=H(f"{t} {e['v']} {CN[e['c']]} {GN[e['g']]}".lower()); dp=e["pr"] if e["pr"] else 999999
    sub=(H(e["tour"])+"<br>" if e["tour"] else "")+H(e["v"])+(", "+e["tm"] if e["tm"] else "")
    return (f'<article class="card" data-t="{k}" data-c="{e["c"]}" data-g="{e["g"]}" data-v="{e["vt"]}" data-p="{dp}" data-d="{e["d"].isoformat()}">'
    f'<a class="po" href="{u}" tabindex="-1"><img src="/img/p/{e["slug"]}.svg" width="400" height="500" alt="Афиша: {H(t)}" loading="lazy" decoding="async"><span class="chip">{fdw(e["d"])}</span></a>'
    f'<div class="cb"><div class="tg"><span>{GN[e["g"]]}</span><i>{CN[e["c"]]}</i></div><h3><a href="{u}">{H(e["artist"])}</a></h3><p class="mu sm">{sub}</p>'
    f'<div class="row"><b class="pr">{ptxt(e)}</b></div><a class="btn" href="{u}" data-goal="to_event">Подробнее</a></div></article>')
def nav():
    L=lambda items:"".join(f'<li><a href="{h}">{n}</a></li>' for n,h in items)
    col=lambda t,items:f'<div><h3>{t}</h3><ul>{L(items)}</ul></div>'
    mega='<div class="dd mg">'+col("Города",[(CN[s],f"/afisha/{s}/") for s in CN]+[("Все города","/afisha/")])+col("Даты",[(v[1].replace("Концерты ",""),f"/afisha/{k}/") for k,v in DT.items()]+[("Выбрать дату","/raspisanie/")])+col("Жанры",[(GN[g],f"/afisha/{g}/") for g in GN])+col("Площадки",[(n,f"/afisha/{s}/") for s,n in VN.items()])+'</div>'
    sb='<button class="sub" aria-label="Открыть подменю" aria-expanded="false">▾</button>'
    items=[("Афиша","/afisha/",mega),("Как купить","/bilety/",""),("Артисты","/artisty/",""),("Подборки","/podborki/",""),("О проекте","/o-nas/",""),("Помощь","/pomoshch/","")]
    return '<ul class="nv">'+"".join(f'<li><a href="{h}">{n}</a>{sb if d else ""}{d}</li>' for n,h,d in items)+'</ul>'
def footer():
    return f'''<footer class="ft"><div class="w"><div class="cols"><div><a class="lg" href="/">{LOGO}{BRAND}</a><p class="mu" style="margin:14px 0 6px">Учебный проект: афиша концертов. Билеты здесь не продаются, кнопки «Купить» ведут на сайт продавца.</p></div>
<div><h3>Афиша</h3><ul><li><a href="/afisha/">Все концерты</a></li><li><a href="/raspisanie/">Расписание концертов</a></li><li><a href="/podborki/">Подборки</a></li><li><a href="/artisty/">Артисты</a></li></ul></div>
<div><h3>Проект</h3><ul><li><a href="/bilety/">Как купить билет</a></li><li><a href="/pomoshch/">Помощь</a></li><li><a href="/o-nas/">О проекте</a></li><li><a href="/politika-konfidencialnosti/">Конфиденциальность</a></li></ul></div></div>
<div class="bot"><span>© {BASE.year} {BRAND}. Данные о концертах взяты с Афиша.ру, сверены {fd(CHECKED)} {CHECKED.year}. Названия артистов и площадок принадлежат их владельцам.</span></div></div></footer>'''


V={}

V={}
def layout(path,title,desc,body,bc=None,kw="",ld=None,noindex=False,sb="",pri=.5,cf="weekly",og="/img/og.png",lastmod=None):
    assert path not in PAGES,path
    crumbs=[("Главная","/")]+(bc or [])
    items=[{"@type":"ListItem","position":i+1,"name":n,"item":SITE+(h or path)} for i,(n,h) in enumerate(crumbs)]
    lds=[{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":items}]+(ld or [])
    bch=""
    if bc: bch='<nav aria-label="Хлебные крошки" class="w"><ol class="bc">'+"".join(f'<li><a href="{h}">{n}</a></li>' if h else f'<li aria-current="page">{n}</li>' for n,h in crumbs)+'</ol></nav>'
    ym=""
    if YM: ym=f'<script>window.YM_ID={YM};(function(m,e,t,r,i,k,a){{m[i]=m[i]||function(){{(m[i].a=m[i].a||[]).push(arguments)}};m[i].l=1*new Date();k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)}})(window,document,"script","https://mc.yandex.ru/metrika/tag.js","ym");ym({YM},"init",{{clickmap:true,trackLinks:true,accurateTrackBounce:true,webvisor:true}});</script><noscript><div><img src="https://mc.yandex.ru/watch/{YM}" style="position:absolute;left:-9999px" alt=""></div></noscript>'
    head=f'''<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{H(title)}</title><meta name="description" content="{H(desc)}">{f'<meta name="keywords" content="{H(kw)}">' if kw else ''}<meta name="robots" content="{'noindex,nofollow' if noindex else 'index,follow,max-image-preview:large'}"><link rel="canonical" href="{SITE}{path}"><meta name="theme-color" content="#0f0c3d">{f'<meta name="yandex-verification" content="{VERIFY}">' if VERIFY else ''}<meta property="og:type" content="website"><meta property="og:site_name" content="{BRAND}"><meta property="og:locale" content="ru_RU"><meta property="og:title" content="{H(title)}"><meta property="og:description" content="{H(desc)}"><meta property="og:url" content="{SITE}{path}"><meta property="og:image" content="{SITE}{og}"><meta name="twitter:card" content="summary_large_image"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/img/icon-192.png"><link rel="manifest" href="/manifest.webmanifest"><link rel="stylesheet" href="/css/style.css?v={V['css']}"><script>document.documentElement.className="js"</script><script type="application/ld+json">{json.dumps(lds,ensure_ascii=False)}</script></head>'''
    PAGES[path]=dict(pri=pri,cf=cf,noindex=noindex,lm=lastmod or BASE)
    pg=head+f'<body class="{"has-sb" if sb else ""}"><a class="skip" href="#main">К содержимому</a><header class="hd"><div class="w"><a class="lg" href="/" aria-label="{BRAND}, на главную">{LOGO}{BRAND}</a><button class="bg" aria-label="Меню" aria-expanded="false">☰</button>{nav()}<div class="ha"><a class="btn sm gh" href="/afisha/">Вся афиша</a></div></div></header>{bch}<main id="main">{body}</main>{footer()}{sb}<div id="ck" class="ck2" hidden><p>Сайт использует cookie и Яндекс Метрику, чтобы работать удобнее. <a href="/politika-konfidencialnosti/"><u>Подробнее</u></a></p><button class="btn sm">Понятно</button></div><script src="/js/app.js?v={V["js"]}" defer></script>{ym}</body></html>'
    if not YM: pg=re.sub(r'<div id="ck".*?</div>','',pg,flags=re.S)
    fp=os.path.join(OUT,path.strip("/"),"index.html") if path!="/404.html" else os.path.join(OUT,"404.html")
    os.makedirs(os.path.dirname(fp),exist_ok=True); open(fp,"w",encoding="utf-8").write(pg)

def chips(items): return '<ul class="ch">'+"".join(f'<li><a href="{h}">{n}</a></li>' for n,h in items)+'</ul>'
CHIPS=lambda:chips([(f"Концерты {CI[s]}",f"/afisha/{s}/") for s in CN]+[(GN[g],f"/afisha/{g}/") for g in GN])
def sec(inner,cls="",h=""): return f'<section class="sec {cls}"><div class="w">{h}{inner}</div></section>'

def listing(path,title,desc,h1,lead,evs,bc,drop=(),when="all",seo="",kw="",pri=.7,cf="weekly"):
    def sel(n,lab,opts,cur=""): return "" if n in drop else f'<label><span>{lab}</span><select name="{n}">'+"".join(f'<option value="{v}"{" selected" if v==cur else ""}>{t}</option>' for v,t in opts)+'</select></label>'
    f=('<form id="flt" class="flt" role="search" aria-label="Фильтры афиши"><label class="q"><span>Поиск</span><input type="search" name="q" placeholder="Артист, площадка или тур" autocomplete="off"></label>'
    +sel("city","Город",[("","Все города")]+[(s,CN[s]) for s in CN])+sel("genre","Жанр",[("","Все жанры")]+[(g,GN[g]) for g in GN])+sel("vt","Площадка",[("","Любая")]+list(VN.items()))
    +sel("when","Когда",[("all","Любая дата"),("today","Сегодня"),("tomorrow","Завтра"),("weekend","Выходные"),("month","Этот месяц")],when)+sel("price","Цена",[("","Любая"),("1500","до 1 500 ₽"),("2500","до 2 500 ₽"),("3500","до 3 500 ₽")])
    +'<button type="reset" class="btn gh sm">Сбросить</button><p id="cnt" class="cnt" aria-live="polite"></p></form>')
    emp='<div id="empty" class="empty" hidden><h3>Под эти условия концертов нет</h3><p>Попробуйте другую дату или город. Список составлен вручную и может быть неполным.</p><button id="rst" class="btn" type="button">Сбросить фильтры</button><a class="btn gh" href="/afisha/">Вся афиша</a></div>'
    body=sec(f'<h1>{h1}</h1><p class="lead">{lead}</p>{f}<div id="ld" class="ld" role="status" hidden><span></span>Обновляем афишу…</div><h2 class="vh">Список концертов</h2><div id="grid" class="grid" aria-busy="false">'+"".join(card(e) for e in evs)+f'</div>{emp}',"")
    body+=sec(f'<div class="pr2">{seo}</div><h2 style="margin-top:36px">Смотрите также</h2>{CHIPS()}',"band")
    layout(path,title,desc,body,bc,kw,pri=pri,cf=cf)

def ROCK():
    r=[e for e in EV if e["g"]=="rok"]
    names=", ".join(f"{H(e['artist'])} ({CN[e['c']]}, {fd(e['d'])})" for e in r)
    return f"<p>Рок-концерты в афише: {names}.</p><p>Формат разный: от клубных вечеров до больших арен. Дату, площадку и минимальную цену смотрите на странице концерта, а купить билет можно у продавца по ссылке.</p>"
def build_pages():
    nxt=EV[:8]; top=EV[:3]
    fan="".join(f'<a class="tk" href="/koncert/{e["slug"]}/"><img src="/img/p/{e["slug"]}.svg" width="400" height="500" alt="Афиша: {H(ttl(e))}" {"fetchpriority=\"high\"" if i==1 else ""}><b>{H(e["artist"])}</b><small>{fdw(e["d"])}, {CN[e["c"]]}</small></a>' for i,e in enumerate(top))
    first=H(EV[0]["artist"])
    hero=f'''<section class="hero"><div class="w"><div><h1>Афиша концертов: ближайшие выступления в&nbsp;{len(CN)} городах</h1><p class="lead">Даты, площадки и цены из открытых афиш. Билеты покупаются у официальных продавцов.</p>
<form class="sf" action="/afisha/" role="search"><label><span>Артист или площадка</span><input name="q" placeholder="Например, {first}" autocomplete="off"></label><label><span>Город</span><select name="city"><option value="">Все города</option>{"".join(f'<option value="{s}">{CN[s]}</option>' for s in CN)}</select></label><label><span>Жанр</span><select name="genre"><option value="">Любой</option>{"".join(f'<option value="{g}">{GN[g]}</option>' for g in GN)}</select></label><button class="btn" type="submit" data-goal="hero_search">Найти</button></form></div><div class="fan">{fan}</div></div></section>'''
    tiles='<div class="gtl">'+"".join(f'<a href="/afisha/{g}/" style="--c:{GC[g][0]}">{GN[g]}<small>{sum(e["g"]==g for e in EV)} концертов</small></a>' for g in GN)+'</div>'
    steps='<ol class="st"><li><h3>Найдите концерт</h3><p>Отфильтруйте афишу по городу, дате и жанру или найдите артиста по названию.</p></li><li><h3>Проверьте данные</h3><p>На странице концерта указаны дата, площадка, время начала и минимальная цена.</p></li><li><h3>Купите у продавца</h3><p>Кнопка на странице концерта ведёт на Афиша.ру. Оплата и возврат происходят там.</p></li></ol><p style="margin-top:24px"><a class="btn" href="/bilety/">Как купить билет</a></p>'
    why='<div class="ft3"><div><h3>Реальные события</h3><p class="mu">В афише только концерты, найденные в открытых афишах. Выдуманных событий нет.</p></div><div><h3>Дата проверки</h3><p class="mu">Данные сверены '+fd(CHECKED)+' '+str(CHECKED.year)+'. Переносы и отмены бывают, поэтому перед покупкой смотрите страницу продавца.</p></div><div><h3>Без посредников</h3><p class="mu">Мы не принимаем оплату и не берём комиссию: вы покупаете билет напрямую у продавца.</p></div></div>'
    pods=chips([("Ближайшие концерты","/podborki/#nearest"),("Концерты выходного дня","/podborki/#weekend"),("Недорогие концерты","/podborki/#cheap"),("Концерты не в Москве","/podborki/#regions"),("Концерты 2027 года","/podborki/#later")])
    body=hero+sec('<div class="grid">'+"".join(card(e) for e in nxt)+'</div><p style="margin-top:28px"><a class="btn gh" href="/afisha/">Вся афиша концертов</a></p>',"",'<h2>Ближайшие концерты</h2>')
    body+=sec(tiles,"",'<h2>Выберите по жанру</h2>')+sec(steps,"band",'<h2>Как это работает</h2>')+sec(why,"",'<h2>Как мы работаем</h2>')
    body+=sec(f'<h2>Подборки</h2>{pods}',"band")
    layout("/",f"Афиша концертов {BASE.year}: даты, площадки, цены | {BRAND}",f"Афиша концертов: {', '.join(CN[s] for s in CN)}. Даты, площадки и цены, ссылки на официальных продавцов билетов.",body,kw="афиша концертов, концерты, расписание концертов, билеты на концерт",pri=1.0,cf="daily",
    ld=[{"@context":"https://schema.org","@type":"WebSite","name":BRAND,"url":SITE+"/","potentialAction":{"@type":"SearchAction","target":SITE+"/afisha/?q={q}","query-input":"required name=q"}}])
    A=[("Афиша","/afisha/")]
    listing("/afisha/",f"Афиша концертов {BASE.year}: расписание | {BRAND}","Вся афиша концертов: фильтры по городу, дате, жанру и площадке. Даты, места и цены, ссылки на продавцов билетов.","Афиша концертов","Все ближайшие выступления в одном месте. Отфильтруйте по городу, дате, жанру или цене.",EV,[("Афиша",None)],pri=.9,cf="daily",seo=f"<p>В афише {len(EV)} концертов в {len(CN)} городах: от клубных вечеров до арен. Данные сверены {fd(CHECKED)} {CHECKED.year}.</p>",kw="афиша концертов, концерты, расписание концертов")
    for s in CN:
        ev=[e for e in EV if e["c"]==s]
        listing(f"/afisha/{s}/",f"Концерты {CI[s]} {BASE.year}: афиша | {BRAND}",f"Афиша концертов {CI[s]}: даты, площадки и цены. Ссылки на официальных продавцов билетов.",f"Концерты {CI[s]}",f"Ближайшие выступления {CI[s]}: выберите жанр или дату.",ev,A+[(CN[s],None)],drop=("city",),seo=f"<p>Сейчас в афише {CI[s]}: {len(ev)} концертов. Список пополняется вручную, поэтому часть выступлений может быть ещё не добавлена.</p>",kw=f"концерты {CN[s]}, афиша {CN[s]}, билеты на концерт")
    for g in GN:
        ev=[e for e in EV if e["g"]==g]
        if g=="rok": listing("/afisha/rok/",f"Рок концерты {BASE.year}: афиша | {BRAND}","Рок концерты: даты, города, площадки и цены. Ссылки на официальных продавцов билетов.","Рок концерты",GB[g],ev,A+[("Рок",None)],drop=("genre",),seo=ROCK(),kw="рок концерты, афиша рок концертов, рок группа концерт",pri=.8)
        else: listing(f"/afisha/{g}/",f"{GN[g]}: концерты {BASE.year} | {BRAND}",f"Афиша концертов в жанре «{GN[g].lower()}»: даты, города и цены.",f"{GN[g]}: концерты",GB[g],ev,A+[(GN[g],None)],drop=("genre",),seo=f"<p>{GB[g]} В афише {len(ev)} событий этого жанра.</p>",kw=f"{GN[g].lower()} концерты")
    dd={"today":"Афиша на сегодня: концерты, которые проходят сегодня.","tomorrow":"Концерты на завтра в ваших городах.","weekend":"Что послушать в выходные: концерты на субботу и воскресенье.","month":"Все концерты текущего месяца по датам, с ценами и площадками."}
    for k,(w_,t) in DT.items(): listing(f"/afisha/{k}/",f"{t} — афиша | {BRAND}",dd[w_],t,dd[w_],EV,A+[(t.replace("Концерты ","").capitalize(),None)],when=w_,seo=f'<p>{dd[w_]} Если в выбранный день концертов нет, загляните в <a href="/raspisanie/">расписание</a> или откройте <a href="/afisha/">всю афишу</a>.</p>',kw=t.lower())
    vd={"kluby":"Клубные концерты: камерный звук, близко к сцене.","kontsertnye-zaly":"Концерты в залах: партер, балкон и хорошая акустика.","stadiony":"Большие площадки: арены и стадионы.","open-air":"Open-air и фестивали: музыка под открытым небом."}
    ti={"kluby":"Концерты в клубах","kontsertnye-zaly":"Концерты в концертных залах","stadiony":"Концерты на аренах и стадионах","open-air":"Open-air концерты и фестивали"}
    for s,n in VN.items():
        ev=[e for e in EV if e["vt"]==s]
        listing(f"/afisha/{s}/",f"{ti[s]}: афиша {BASE.year} | {BRAND}",f"{vd[s]} Афиша с датами и ценами.",ti[s],vd[s],ev,A+[(n,None)],drop=("vt",),seo=f"<p>{vd[s]} В афише {len(ev)} событий этого формата.</p>",kw=ti[s].lower())
    for e in EV: event_page(e)
    static_pages()
def event_page(e):
    u=f"/koncert/{e['slug']}/"; t=ttl(e); g=e["g"]; tz="+05:00" if e["c"]=="ekaterinburg" else "+03:00"
    rel=[x for x in EV if x is not e and (x["g"]==g or x["c"]==e["c"])][:3]
    when=f'{fd(e["d"])} {e["d"].year}, {WD[e["d"].weekday()]}'+(f', начало в {e["tm"]}' if e["tm"] else "; время начала уточняйте у продавца")
    price=f'от {rub(e["pr"])}' if e["pr"] else "уточняйте у продавца"
    shr=lambda n,h:f'<a class="btn gh sm" href="{h}" target="_blank" rel="nofollow noopener">{n}</a>'
    q=SITE+u; h1=H(e["artist"])+(f': {H(e["tour"])}' if e["tour"] else "")
    buy=f'<a class="btn" style="width:100%;text-align:center" href="{H(e["url"])}" target="_blank" rel="nofollow noopener" data-goal="buy_click">Смотреть билеты на Афише</a>'
    body=f'''<div class="w"><div class="ev"><div class="po"><img src="/img/p/{e["slug"]}.svg" width="400" height="500" alt="Афиша: {H(t)}" fetchpriority="high"></div><div><div class="tg mu"><span>{GN[g]}</span><i>{CN[e["c"]]}</i></div><h1 style="margin-top:8px;font-size:clamp(2rem,4.5vw,3.4rem)">{h1}</h1>
<dl class="meta"><dt>Дата</dt><dd>{when}</dd><dt>Площадка</dt><dd>{H(e["v"])}, {CN[e["c"]]}</dd>{f'<dt>Возраст</dt><dd>{H(e["age"])}</dd>' if e["age"] else ""}<dt>Цена</dt><dd>{price}</dd></dl>
<div class="act">{shr("ВКонтакте","https://vk.com/share.php?url="+q)}{shr("Telegram","https://t.me/share/url?url="+q)}</div>
<div class="tw" id="buy"><h2 style="font-size:1.4rem;margin-bottom:12px">Билеты</h2><p class="mi" style="margin-bottom:14px">Минимальная цена по данным афиши на {fd(CHECKED)}: <b>{price}</b>.</p>{buy}<p class="sm mi" style="margin-top:12px">Билеты продаёт Афиша.ру. На этом сайте оплата не принимается, а условия возврата указаны у продавца.</p></div></div></div></div>'''
    body+=sec(f'''<div class="pr2"><h2>О концерте</h2><p>{H(e["artist"])} выступит {CI[e["c"]]}: {when}. Площадка: {H(e["v"])}.</p><h3>Что нужно знать</h3><ul><li>Данные сверены {fd(CHECKED)} {CHECKED.year}. Даты и цены могут измениться, актуальную информацию смотрите на странице продавца.</li><li>Как купить билет и что проверить перед оплатой: <a href="/bilety/">инструкция</a>.</li></ul></div>''',"",'')
    body+=sec('<div class="grid">'+"".join(card(x) for x in rel)+f'</div><p style="margin-top:24px">{CHIPS()}</p>',"",'<h2>Другие концерты</h2>')
    sbar=f'<div class="sb"><b>{price}</b><a class="btn sm" href="#buy">Билеты</a></div>'
    off={"@type":"Offer","url":e["url"],"priceCurrency":"RUB"}
    if e["pr"]: off["price"]=e["pr"]
    start=f'{e["d"].isoformat()}T{e["tm"]}:00{tz}' if e["tm"] else e["d"].isoformat()
    ld=[{"@context":"https://schema.org","@type":"Event","name":t,"startDate":start,"eventStatus":"https://schema.org/EventScheduled","eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode","location":{"@type":"Place","name":e["v"],"address":{"@type":"PostalAddress","addressLocality":CN[e["c"]],"addressCountry":"RU"}},"image":[SITE+f"/img/p/{e['slug']}.svg"],"description":f"{e['artist']}: концерт {CI[e['c']]}, {fd(e['d'])}, {e['v']}.","performer":{"@type":"PerformingGroup","name":e["artist"]},"offers":off}]
    layout(u,(f"{e['artist']}"+(f": {e['tour']}" if e["tour"] else "")+f" {CI[e['c']]}, {fd(e['d'])} — билеты | {BRAND}")[:110],f"Концерт {e['artist']} {CI[e['c']]}, {fd(e['d'])}, {e['v']}. Цена {price}. Ссылка на продавца билетов.",body,[("Афиша","/afisha/"),(GN[g],f"/afisha/{g}/"),(e["artist"],None)],ld=ld,sb=sbar,pri=.6)


def prose(path,title,desc,h1,inner,bc,pri=.5,ld=None,kw="",noindex=False,lead="",cf="monthly"):
    layout(path,title,desc,sec(f'<h1>{h1}</h1>'+(f'<p class="lead">{lead}</p>' if lead else '')+f'<div class="pr2">{inner}</div>'),bc,kw,ld,noindex,pri=pri,cf=cf)
def links(items): return '<ul class="ch">'+"".join(f'<li><a href="{h}">{n}</a></li>' for n,h in items)+'</ul>'

def static_pages():
    g4=lambda L:'<div class="grid">'+"".join(card(e) for e in L)+'</div>' if L else '<p class="mu">Сейчас подходящих концертов нет.</p>'
    # как купить
    layout("/bilety/",f"Как купить билет на концерт | {BRAND}","Как купить билет на концерт из афиши: где происходит оплата, что проверить перед покупкой и как вернуть билет.",
    sec('<h1>Как купить билет на концерт</h1><p class="lead">Мы показываем афишу, а билеты продают официальные продавцы. Оплата и возврат происходят на их сайте.</p>'+links([("Афиша концертов","/afisha/"),("Расписание концертов","/raspisanie/"),("Подборки","/podborki/"),("Помощь","/pomoshch/")])
    +'<div class="pr2" style="margin-top:28px"><h2>Шаги</h2><ol><li>Откройте <a href="/afisha/">афишу</a> и выберите концерт по городу, дате или жанру.</li><li>На странице концерта проверьте дату, площадку и время начала.</li><li>Нажмите «Смотреть билеты на Афише»: откроется страница продавца в новой вкладке.</li><li>Выберите места и оплатите заказ на сайте продавца.</li></ol><h2>Что проверить перед оплатой</h2><ul><li>Дату и город: концерты переносят, а у артистов бывает несколько выступлений в одном городе.</li><li>Название площадки и адрес.</li><li>Возрастное ограничение.</li><li>Итоговую цену с учётом сборов продавца и условия возврата.</li></ul><p>Мы не принимаем оплату, не выпускаем билеты и не отвечаем за заказы. По вопросам заказа обращайтесь к продавцу.</p></div>'),
    [("Как купить",None)],kw="как купить билет на концерт",pri=.6)
    # артисты
    by={a:[e for e in EV if e["artist"]==a] for a in ARTISTS}
    def acard(a):
        es=by[a]; g=es[0]["g"]
        return f'<div><div class="av" style="background:{GC[g][0]}">{H(a[0])}</div><h3>{H(a)}</h3><p class="mu sm" style="margin-bottom:10px">{GN[g]}</p><ul class="ch" style="margin-bottom:14px">'+"".join(f'<li><a href="/koncert/{e["slug"]}/">{fd(e["d"])}, {CN[e["c"]]}</a></li>' for e in es)+'</ul></div>'
    tours=[a for a in ARTISTS if len(by[a])>1]
    layout("/artisty/",f"Артисты в афише концертов | {BRAND}","Исполнители, у которых есть ближайшие концерты: даты, города и ссылки на страницы концертов.",
    sec('<h1>Артисты в афише</h1><p class="lead">Исполнители, у которых есть ближайшие концерты. Выберите дату, чтобы открыть страницу концерта.</p>')+sec('<div class="team">'+"".join(acard(a) for a in ARTISTS)+'</div>',"",'<h2 id="artists">Все артисты</h2>')+(sec('<div class="team">'+"".join(acard(a) for a in tours)+'</div>',"band",'<h2 id="tours">Несколько дат</h2>') if tours else ""),[("Артисты",None)],pri=.5)
    # подборки
    wk=[e for e in EV if e["d"].weekday()>=4][:4]; ch=[e for e in EV if e["pr"] and e["pr"]<=2500][:4]; rg=[e for e in EV if e["c"] not in("moskva","sankt-peterburg")][:4]; lt=[e for e in EV if e["d"].year>BASE.year][:4]
    layout("/podborki/",f"Подборки концертов | {BRAND}","Подборки концертов: ближайшие, на выходные, недорогие, в регионах и в следующем году.",
    sec('<h1>Подборки концертов</h1><p class="lead">Автоматические подборки по данным афиши.</p>')+sec(g4(EV[:4]),"",'<h2 id="nearest">Ближайшие концерты</h2>')+sec(g4(wk),"band",'<h2 id="weekend">Концерты выходного дня</h2>')+sec(g4(ch),"",'<h2 id="cheap">Недорогие: от 2 500 ₽ и ниже</h2>')+sec(g4(rg),"band",'<h2 id="regions">Концерты не в Москве и Петербурге</h2>')+sec(g4(lt),"",'<h2 id="later">Концерты следующего года</h2>'),[("Подборки",None)],pri=.6)
    # расписание
    rows="".join(f'<tr><td>{fdw(e["d"])}</td><td>{e["tm"] or "—"}</td><td><a href="/koncert/{e["slug"]}/"><u>{H(e["artist"])}</u></a>'+(f'<br><span class="mu sm">{H(e["tour"])}</span>' if e["tour"] else "")+f'</td><td>{CN[e["c"]]}</td><td>{H(e["v"])}</td><td>{ptxt(e)}</td></tr>' for e in EV)
    layout("/raspisanie/",f"Расписание концертов {BASE.year}: даты, площадки, цены | {BRAND}","Расписание концертов по датам: время начала, город, площадка и минимальная цена билета.",sec(f'<h1>Расписание концертов</h1><p class="lead">Все концерты из афиши по порядку. Время «—» означает, что в источнике оно не указано.</p><div class="tbl"><table><thead><tr><th>Дата</th><th>Время</th><th>Артист</th><th>Город</th><th>Площадка</th><th>Цена</th></tr></thead><tbody>{rows}</tbody></table></div>'),[("Расписание",None)],pri=.7,cf="daily")
    layout("/muzykalnye-koncerty/",f"Музыкальные концерты: жанры и афиша | {BRAND}","Музыкальные концерты по жанрам: выберите направление и посмотрите ближайшие выступления.",
    sec('<h1>Музыкальные концерты</h1><p class="lead">Выберите жанр или посмотрите ближайшие выступления.</p><div class="gtl">'+"".join(f'<a href="/afisha/{g}/" style="--c:{GC[g][0]}">{GN[g]}<small>{GB[g]}</small></a>' for g in GN)+'</div>'),[("Музыкальные концерты",None)],pri=.6)
    prose("/o-nas/",f"О проекте {BRAND}","Что за проект «Живой звук», откуда данные и чего на сайте нет.","О проекте «Живой звук»",f'<p>«Живой звук» — учебный проект: статический сайт с афишей концертов. Он показывает реальные события с датами, площадками и минимальными ценами.</p><h2>Откуда данные</h2><p>Сведения о концертах взяты с Афиша.ру и сверены {fd(CHECKED)} {CHECKED.year}. Список составлен вручную и не претендует на полноту.</p><h2>Чего здесь нет</h2><p>Сайт не продаёт билеты, не принимает оплату и не связан с артистами, площадками и организаторами. Кнопка на странице концерта ведёт на сайт продавца.</p><h2>Нашли ошибку?</h2><p>Создайте issue в репозитории проекта на GitHub: исправить данные можно в файле <code>data/events.json</code>.</p>',[("О проекте",None)],pri=.5)
    faq=[("Вы продаёте билеты?","Нет. Мы показываем афишу, а кнопка «Смотреть билеты на Афише» открывает страницу продавца."),("Откуда данные о концертах?",f"Из открытых афиш Афиша.ру. Данные сверены {fd(CHECKED)} {CHECKED.year}."),("Что делать, если концерт перенесли или отменили?","Обратитесь к продавцу, у которого куплен билет: условия возврата и обмена указаны на его сайте."),("Почему у некоторых концертов нет цены или времени?","Если в источнике этих сведений не было, мы их не придумываем. Уточняйте на странице продавца."),("Почему нужного концерта нет в афише?","Список составлен вручную и охватывает только часть событий.")]
    layout("/pomoshch/",f"Помощь и частые вопросы | {BRAND}","Ответы на частые вопросы: откуда данные, где покупать билеты и что делать при переносе концерта.",sec('<h1>Помощь</h1><div class="pr2" style="margin-top:28px">'+"".join(f'<h2>{H(q_)}</h2><p>{H(a_)}</p>' for q_,a_ in faq)+'<p><a href="/bilety/">Как купить билет</a></p></div>'),[("Помощь",None)],pri=.5,
    ld=[{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":q_,"acceptedAnswer":{"@type":"Answer","text":a_}} for q_,a_ in faq]}])
    prose("/politika-konfidencialnosti/",f"Политика конфиденциальности | {BRAND}","Какие данные собирает сайт.","Политика конфиденциальности",'<p>Сайт статический: на нём нет форм, регистрации и личных кабинетов, и мы не собираем персональные данные.</p><p>Если владелец сайта подключит счётчик Яндекс Метрики, он будет собирать обезличенную статистику посещений. В этом случае на сайте появится уведомление о cookie.</p><p>Ссылки на страницы продавцов ведут на сторонние сайты. Их политика конфиденциальности действует отдельно.</p>',[("Конфиденциальность",None)],pri=.2)
    layout("/404.html",f"Страница не найдена (404) | {BRAND}","Такой страницы нет. Вернитесь на главную или откройте афишу концертов.",'<div class="nf"><div class="w"><h1>404</h1><p class="lead" style="margin-inline:auto">Страница не найдена: возможно, концерт уже прошёл и убран из афиши.</p><p><a class="btn" href="/afisha/">Открыть афишу</a> <a class="btn gh" href="/">На главную</a></p></div></div>',noindex=True,pri=0)


def mincss(s):
    s=re.sub(r"/\*.*?\*/","",s,flags=re.S); s=re.sub(r"\s+"," ",s); s=re.sub(r"\s*([{};,>])\s*",r"\1",s); s=re.sub(r":\s+",":",s); return s.replace(";}","}")
def w(p,c,mode="w"):
    fp=os.path.join(OUT,p); os.makedirs(os.path.dirname(fp),exist_ok=True)
    if isinstance(c,bytes): open(fp,"wb").write(c)
    else: open(fp,mode,encoding="utf-8").write(c)

def assets():
    try:
        from PIL import Image,ImageDraw,ImageFont
        def icon(n):
            im=Image.new("RGB",(n,n),"#ff4d6d"); d=ImageDraw.Draw(im); u=n/36
            for x,a,b in [(9,14,22),(14,10,26),(19,16,20),(24,12,24),(29,15,21)]: d.line([(x*u,a*u),(x*u,b*u)],fill="#120e38",width=int(3*u))
            return im
        for n in (192,512): icon(n).save(os.path.join(OUT,f"img/icon-{n}.png"))
        im=Image.new("RGB",(1200,630),"#0f0c3d"); d=ImageDraw.Draw(im)
        for i,(c,x) in enumerate([("#ff6b81",820),("#ffb347",960),("#a78bfa",1090)]): d.ellipse([x-170,120+i*60,x+170,460+i*60],fill=c)
        d.rectangle([0,0,1200,630],outline="#f4f1fb",width=0)
        try: f1=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",84); f2=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",38)
        except Exception: f1=f2=ImageFont.load_default()
        d.text((70,200),"Живой звук",font=f1,fill="#f4f1fb"); d.text((70,320),"Афиша концертов",font=f2,fill="#b4b0e6",spacing=12)
        im.save(os.path.join(OUT,"img/og.png"),optimize=True)
    except Exception as ex: print("PIL недоступен, иконки пропущены:",ex)

def prefix(s):
    return re.sub(r'(href|src|action)="/(?!/)',lambda m:f'{m.group(1)}="{BP}/',s) if BP else s
def main():
    shutil.rmtree(OUT,ignore_errors=True); os.makedirs(OUT)
    css=mincss(open(os.path.join(HERE,"src/style.css"),encoding="utf-8").read()+".band input,.band select,.band textarea{background:#fff;color:var(--ink);border-color:#cfc9ee}.band label{font-weight:600}.tbl{overflow-x:auto}.tbl table{width:100%;border-collapse:collapse}.tbl th,.tbl td{padding:10px 12px;text-align:left;border-bottom:1px solid #cfc9ee33;vertical-align:top}")
    js=open(os.path.join(HERE,"src/app.js"),encoding="utf-8").read()
    V["css"]=hashlib.md5(css.encode()).hexdigest()[:8]; V["js"]=hashlib.md5(js.encode()).hexdigest()[:8]
    w("css/style.css",css); w("js/app.js",js); w("favicon.svg",LOGO.replace('<svg ','<svg xmlns="http://www.w3.org/2000/svg" '))
    for e in EV: w(f"img/p/{e['slug']}.svg",poster(e))
    assets(); build_pages()
    sm='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f'<url><loc>{SITE}{p}</loc><lastmod>{m["lm"].isoformat()}</lastmod><changefreq>{m["cf"]}</changefreq><priority>{m["pri"]}</priority></url>' for p,m in PAGES.items() if not m["noindex"])+'</urlset>'
    w("sitemap.xml",sm)
    w("robots.txt",f"User-agent: *\nDisallow: /*?q=\nDisallow: /*?city=\nDisallow: /*?genre=\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    w("manifest.webmanifest",json.dumps({"name":BRAND,"short_name":BRAND,"lang":"ru","start_url":BP+"/","display":"standalone","background_color":"#0f0c3d","theme_color":"#0f0c3d","icons":[{"src":BP+"/img/icon-192.png","sizes":"192x192","type":"image/png"},{"src":BP+"/img/icon-512.png","sizes":"512x512","type":"image/png"}]},ensure_ascii=False))
    w(".nojekyll","")
    validate()
    for root,_,files in os.walk(OUT):
        for f in files:
            if f.endswith(".html"):
                fp=os.path.join(root,f); s=open(fp,encoding="utf-8").read(); open(fp,"w",encoding="utf-8").write(prefix(s))


def validate():
    bad=[];T={};D={}
    for p,_ in PAGES.items():
        fp=os.path.join(OUT,p.strip("/"),"index.html") if p!="/404.html" else os.path.join(OUT,"404.html"); s=open(fp,encoding="utf-8").read()
        t=re.search(r"<title>(.*?)</title>",s).group(1); d=re.search(r'name="description" content="(.*?)"',s).group(1)
        if t in T: bad.append(f"дубль title: {p} = {T[t]}")
        if d in D: bad.append(f"дубль description: {p} = {D[d]}")
        T[t]=p;D[d]=p
        if s.count("<h1")!=1: bad.append(f"h1 != 1: {p}")
        if len(t)>110: bad.append(f"длинный title {len(t)}: {p}")
        for m in re.findall(r'(?:href|src)="(/[^"#?]*)',s):
            if m.startswith("//"): continue
            fp2=os.path.join(OUT,m.strip("/"),"index.html") if m.endswith("/") else os.path.join(OUT,m.lstrip("/"))
            if not os.path.exists(fp2): bad.append(f"битая ссылка {m} на {p}")
    n=sum(1 for _ in PAGES)
    print(f"Страниц: {n}, событий: {len(EV)}, замечаний: {len(set(bad))}"); [print(" -",b) for b in sorted(set(bad))[:30]]

if __name__=="__main__": main()

