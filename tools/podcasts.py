#!/usr/bin/env python3
"""Haalt de nieuwste afleveringen op uit de echte RSS-feeds van de podcasts (zelfde feed die Spotify gebruikt).
Feed-URL's worden via de Apple iTunes-zoek-API gevonden. Schrijft podcasts.json. Draait in GitHub Actions (vrij internet)."""
import json, re, sys, html, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime
from zoneinfo import ZoneInfo

SHOWS = [
  {"show": "De Lange Termijn", "term": "De Lange Termijn", "match": "lange termijn",
   "show_url": "https://open.spotify.com/show/2s8EwhUs3YoaU5mnjtkBWz"},
  {"show": "Mind to Invest", "term": "Mind to Invest", "match": "mind to invest",
   "show_url": "https://open.spotify.com/search/Mind%20to%20Invest/podcasts"},
]
UA = {"User-Agent": "Mozilla/5.0 (startpagina podcasts)"}

def get(url, t=30):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=t).read()

def find_feed(s):
    q = "https://itunes.apple.com/search?media=podcast&entity=podcast&limit=15&term=" + urllib.parse.quote(s["term"])
    res = json.loads(get(q)).get("results", [])
    best = [r for r in res if s["match"] in (r.get("collectionName") or "").lower() and r.get("feedUrl")]
    if not best: raise RuntimeError("geen feed voor " + s["show"])
    return best[0]["feedUrl"]

def clean(t, n=260):
    t = html.unescape(re.sub(r"<[^>]+>", " ", t or "")); t = re.sub(r"\s+", " ", t).strip()
    if len(t) > n: t = t[:n].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
    return t

def episodes(feed, n=3):
    root = ET.fromstring(get(feed))
    out = []
    for it in root.iter("item"):
        d = it.findtext("pubDate")
        try: dt = parsedate_to_datetime(d).astimezone(ZoneInfo("Europe/Brussels"))
        except Exception: continue
        link = it.findtext("link") or ""
        enc = it.find("enclosure")
        desc = it.findtext("description") or it.findtext("{http://www.itunes.com/dtds/podcast-1.0.dtd}summary") or ""
        out.append({"titel": clean(it.findtext("title"), 160), "datum": dt.strftime("%Y-%m-%d"),
                    "_ts": dt.timestamp(), "url": link if link.startswith("http") else "", "kort": clean(desc)})
    out.sort(key=lambda e: -e["_ts"])
    for e in out: e.pop("_ts")
    return out[:n]

def main():
    old = {}
    try: old = {p["show"]: p for p in json.load(open("podcasts.json", encoding="utf-8")).get("podcasts", [])}
    except Exception: pass
    pods = []
    for s in SHOWS:
        try:
            eps = episodes(find_feed(s))
            for e in eps:
                if not e["url"]: e["url"] = s["show_url"]
            pods.append({"show": s["show"], "show_url": s["show_url"], "afleveringen": eps})
            print("OK", s["show"], eps[0]["datum"], eps[0]["titel"])
        except Exception as ex:
            print("FOUT", s["show"], ex, file=sys.stderr)
            if s["show"] in old: pods.append(old[s["show"]])
    if pods:
        json.dump({"bijgewerkt": datetime.now(ZoneInfo("Europe/Brussels")).isoformat(timespec="seconds"), "podcasts": pods},
                  open("podcasts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

if __name__ == "__main__": main()
