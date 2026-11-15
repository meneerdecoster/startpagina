#!/usr/bin/env python3
"""Haalt koersen op bij Yahoo Finance en schrijft enkel percentages (dag en 1 maand) naar quotes.json."""
import json, sys, datetime, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; StartpaginaBot/1.0)"}

def meta(t, rng):
    for host in ("query1", "query2"):
        try:
            u = f"https://{host}.finance.yahoo.com/v8/finance/chart/{t}?range={rng}&interval=1d"
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20) as r:
                return json.load(r)["chart"]["result"][0]["meta"]
        except Exception as e:
            print("fout", t, rng, host, e, file=sys.stderr)
    return None

items = []
for p in json.load(open("tools/positions.json")):
    it = {"naam": p["naam"], "dag": None, "maand": None, "datum": None}
    d = meta(p["ticker"], "1d")
    if d and d.get("regularMarketPrice"):
        pct = d.get("regularMarketChangePercent")
        if pct is None and d.get("chartPreviousClose"):
            pct = (d["regularMarketPrice"] / d["chartPreviousClose"] - 1) * 100
        if pct is not None: it["dag"] = round(pct, 2)
        if d.get("regularMarketTime"):
            it["datum"] = datetime.datetime.utcfromtimestamp(d["regularMarketTime"]).strftime("%Y-%m-%d")
    m = meta(p["ticker"], "1mo")
    if m and m.get("regularMarketPrice") and m.get("chartPreviousClose"):
        it["maand"] = round((m["regularMarketPrice"] / m["chartPreviousClose"] - 1) * 100, 2)
    items.append(it)
try: old = {i["naam"]: i for i in json.load(open("quotes.json")).get("items", [])}
except Exception: old = {}
for it in items:
    if it["dag"] is None and old.get(it["naam"], {}).get("dag") is not None:
        it.update({k: old[it["naam"]].get(k) for k in ("dag", "maand", "datum")})
json.dump({"bijgewerkt": datetime.datetime.utcnow().isoformat() + "Z", "items": items}, open("quotes.json", "w"), ensure_ascii=False, indent=1)
print(items)
