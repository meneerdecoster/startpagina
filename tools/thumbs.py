#!/usr/bin/env python3
"""Zoekt per artikel in data.json de hoofdafbeelding (og:image) op en schrijft thumbs.json."""
import json, re, sys, urllib.request, urllib.parse
from html.parser import HTMLParser

UA = "Mozilla/5.0 (compatible; StartpaginaBot/1.0)"
BAD = re.compile(r"logo|favicon|subscribe|placeholder|avatar|icon|substack\.com/api|twitter_card|\.(png|svg|gif)(\?|$)", re.I)

class Meta(HTMLParser):
    def __init__(self):
        super().__init__(); self.og = None; self.tw = None
    def handle_starttag(self, tag, attrs):
        if tag != "meta": return
        a = dict(attrs); k = (a.get("property") or a.get("name") or "").lower(); c = a.get("content")
        if not c: return
        if k == "og:image" and not self.og: self.og = c
        if k in ("twitter:image", "twitter:image:src") and not self.tw: self.tw = c

def get(url, method="GET", n=600000):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept-Language": "nl,en;q=0.8"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r, (r.read(n) if method == "GET" else b"")

_home={}
def og_of(url):
    try:
        r, body = get(url)
        m = Meta(); m.feed(body.decode(r.headers.get_content_charset() or "utf-8", "ignore"))
        c = m.og or m.tw
        return urllib.parse.urljoin(url, c) if c else None
    except Exception:
        return None

def home_og(u):
    p = urllib.parse.urlparse(u); root = f"{p.scheme}://{p.netloc}/"
    if root not in _home: _home[root] = og_of(root)
    return _home[root]

GENERIC = re.compile(r"opengraph|og[-_]?image|og[-_]?default|default|share[-_]?image|fallback|brand|omslag|logo", re.I)

def yt_thumb(u):
    m = re.search(r"youtube\.com/watch\?v=([\w-]{11})|youtu\.be/([\w-]{11})", u)
    return f"https://i.ytimg.com/vi/{m.group(1) or m.group(2)}/mqdefault.jpg" if m else None

NOPHOTO = ("veb.net",)

def thumb(u):
    if any(h in urllib.parse.urlparse(u).netloc for h in NOPHOTO): return None
    y = yt_thumb(u)
    if y: return y
    if len(urllib.parse.urlparse(u).path) <= 4: return None
    try:
        r, body = get(u)
        m = Meta(); m.feed(body.decode(r.headers.get_content_charset() or "utf-8", "ignore"))
        c = m.og or m.tw
        if not c: return None
        img = urllib.parse.urljoin(u, c)
        if BAD.search(img) or GENERIC.search(img): return None
        h = home_og(u)
        if h and h.split('?')[0] == img.split('?')[0]: return None
        r2, _ = get(img, "HEAD")
        ct = r2.headers.get("Content-Type", ""); ln = int(r2.headers.get("Content-Length") or 0)
        if not ct.startswith("image/") or (ln and ln < 25000): return None
        return img
    except Exception as e:
        print("fout", u, e, file=sys.stderr); return None

def urls(d):
    out = []
    for k in ("markten", "tech", "nieuws", "films", "dieren", "mensen", "duivels", "lifestyle", "voeding", "boeken"):
        out += [x for i in d.get(k, []) if isinstance(i, dict) for x in (i.get("url"), i.get("video"))]
    for p in d.get("podcasts", []):
        out += [e.get("url") for e in p.get("afleveringen", [])]
    for lst in (d.get("sport") or {}).values():
        out += [i.get("url") for i in lst]
    return [u for u in dict.fromkeys(out) if u]

def embeddable(u):
    try:
        get("https://www.youtube.com/oembed?format=json&url=" + urllib.parse.quote(u, safe=""), n=3000); return True
    except urllib.error.HTTPError as e:
        return False if e.code in (401, 403, 404) else None
    except Exception:
        return None

import os
src = {}
for f in ("data.json", "ida.json", "otto.json", "severine.json"):
    if os.path.exists(f):
        try: src[f] = json.load(open(f))
        except Exception as e: print("fout", f, e, file=sys.stderr)
try: old = json.load(open("thumbs.json"))
except Exception: old = {}
res = {}
for d in src.values():
  for u in urls(d):
    res[u] = old[u] if u in old else thumb(u)
json.dump(res, open("thumbs.json", "w"), ensure_ascii=False, indent=1)
print(sum(1 for v in res.values() if v), "van", len(res), "met afbeelding")

# Kan elke YouTube-video ingebed worden? (embed.json: url -> true/false)
try: emb = json.load(open("embed.json"))
except Exception: emb = {}
for u in res:
    if yt_thumb(u) and emb.get(u) is None:
        v = embeddable(u)
        if v is not None: emb[u] = v
json.dump({u: v for u, v in emb.items() if u in res}, open("embed.json", "w"), indent=1)
