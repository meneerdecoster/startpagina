#!/usr/bin/env python3
"""Haalt koersen op bij Yahoo Finance en schrijft enkel percentages (dag en 1 maand) naar quotes.json."""
import json, sys, datetime, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; StartpaginaBot/1.0)"}

def chart(t, rng):
    for host in ("query1", "query2"):
        try:
            u = f"https://{host}.finance.yahoo.com/v8/finance/chart/{t}?range={rng}&interval=1d"
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20) as r:
                return json.load(r)["chart"]["result"][0]
        except Exception as e:
            print("fout", t, rng, host, e, file=sys.stderr)
    return None

def meta(t, rng):
    c = chart(t, rng)
    return c["meta"] if c else None

def maand_pct(t):
    """Koers nu t.o.v. de laatste slotkoers op of vóór dezelfde dag een maand geleden (niet chartPreviousClose, dat bij dun verhandelde fondsen gewoon gisteren is)."""
    c = chart(t, "1y")
    if not c: return None
    ts = c.get("timestamp") or []
    cl = (c.get("indicators", {}).get("quote") or [{}])[0].get("close") or []
    pts = [(a, b) for a, b in zip(ts, cl) if b]
    if len(pts) < 2: return None
    now_ts, now = pts[-1]
    nu = datetime.datetime.utcfromtimestamp(now_ts)
    m = nu.month - 1 or 12; y = nu.year - (1 if nu.month == 1 else 0)
    day = min(nu.day, 28)
    cut = datetime.datetime(y, m, day, 23, 59).timestamp()
    ref = [b for a, b in pts if a <= cut]
    print("debug", t, len(pts), datetime.datetime.utcfromtimestamp(pts[0][0]), "->", nu, file=sys.stderr)
    if not ref:
        a, b = pts[0]
        if a - cut > 7 * 86400: return None
        ref = [b]
    return round((now / ref[-1] - 1) * 100, 2)

items = []
for p in json.load(open("tools/positions.json")):
    it = {"naam": p["naam"], "dag": None, "maand": None, "koers": None, "valuta": None, "datum": None}
    d = meta(p["ticker"], "1d")
    if d and d.get("regularMarketPrice"):
        pct = d.get("regularMarketChangePercent")
        if pct is None and d.get("chartPreviousClose"):
            pct = (d["regularMarketPrice"] / d["chartPreviousClose"] - 1) * 100
        if pct is not None: it["dag"] = round(pct, 2)
        it["koers"] = d["regularMarketPrice"]; it["valuta"] = d.get("currency")
        if d.get("regularMarketTime"):
            it["datum"] = datetime.datetime.utcfromtimestamp(d["regularMarketTime"]).strftime("%Y-%m-%d")
    it["maand"] = maand_pct(p["ticker"])
    if it["maand"] is None and p.get("maand_ticker"): it["maand"] = maand_pct(p["maand_ticker"])
    items.append(it)
try: old = {i["naam"]: i for i in json.load(open("quotes.json")).get("items", [])}
except Exception: old = {}
for it in items:
    if it["dag"] is None and old.get(it["naam"], {}).get("dag") is not None:
        it.update({k: old[it["naam"]].get(k) for k in ("dag", "maand", "koers", "valuta", "datum")})
json.dump({"bijgewerkt": datetime.datetime.utcnow().isoformat() + "Z", "items": items}, open("quotes.json", "w"), ensure_ascii=False, indent=1)
print(items)
