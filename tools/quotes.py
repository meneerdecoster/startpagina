#!/usr/bin/env python3
"""Haalt koersen op bij Yahoo Finance en schrijft enkel percentages naar quotes.json."""
import json, sys, datetime, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (compatible; StartpaginaBot/1.0)"}

def closes(t):
    for host in ("query1", "query2"):
        try:
            u = f"https://{host}.finance.yahoo.com/v8/finance/chart/{t}?range=10d&interval=1d"
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20) as r:
                j = json.load(r)
            res = j["chart"]["result"][0]
            ts = res["timestamp"]; cl = res["indicators"]["quote"][0]["close"]
            pts = [(a, b) for a, b in zip(ts, cl) if b is not None]
            if len(pts) >= 2: return pts
        except Exception as e:
            print("fout", t, host, e, file=sys.stderr)
    return None

items = []
for p in json.load(open("tools/positions.json")):
    it = {"naam": p["naam"], "dag": None, "inleg": None, "datum": None}
    if p.get("ticker"):
        pts = closes(p["ticker"])
        if pts:
            (t0, c0), (t1, c1) = pts[-2], pts[-1]
            it["dag"] = round((c1 / c0 - 1) * 100, 2)
            if p.get("inleg"): it["inleg"] = round((c1 / p["inleg"] - 1) * 100, 2)
            it["datum"] = datetime.datetime.utcfromtimestamp(t1).strftime("%Y-%m-%d")
    items.append(it)
try: old = json.load(open("quotes.json"))
except Exception: old = {"items": []}
# behoud oude waarde als ophalen mislukte
oldmap = {i["naam"]: i for i in old.get("items", [])}
for it in items:
    if it["dag"] is None and it["naam"] in oldmap and oldmap[it["naam"]].get("dag") is not None:
        it.update(oldmap[it["naam"]])
json.dump({"bijgewerkt": datetime.datetime.utcnow().isoformat() + "Z", "items": items}, open("quotes.json", "w"), ensure_ascii=False, indent=1)
print(items)
