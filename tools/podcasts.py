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
  {"show": "Mind to Invest", "term": "Mind to Invest", "terms": ["Mind to Invest", "Mind to Invest Archer", "Archer Academy", "Mind to Invest podcast"], "match": "mind to invest",
   "yt": "UCyYqCWGMWLWyoaGNIrO_Dag", "yt_re": r"EP\s?\d+",
   "show_url": "https://open.spotify.com/search/Mind%20to%20Invest/podcasts"},
]
UA = {"User-Agent": "Mozilla/5.0 (startpagina podcasts)"}

def get(url, t=30):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=t).read()

def find_feed(s):
    for term in s.get("terms", [s["term"]]):
        for country in ("be", "nl", "us"):
            q = "https://itunes.apple.com/search?media=podcast&entity=podcast&limit=20&country=%s&term=%s" % (country, urllib.parse.quote(term))
            try: res = json.loads(get(q)).get("results", [])
            except Exception as ex: print("itunes fout", ex); continue
            print("zoek", term, country, [r.get("collectionName") for r in res][:8])
            best = [r for r in res if s["match"] in ((r.get("collectionName") or "") + " " + (r.get("artistName") or "")).lower() and r.get("feedUrl")]
            if best: return best[0]["feedUrl"]
    raise RuntimeError("geen feed voor " + s["show"])

def yt_episodes(cid, rx, n=3):
    root = ET.fromstring(get("https://www.youtube.com/feeds/videos.xml?channel_id=" + cid))
    ns = {"a": "http://www.w3.org/2005/Atom"}; out = []
    for e in root.findall("a:entry", ns):
        t = e.findtext("a:title", "", ns)
        if not re.search(rx, t): continue
        dt = datetime.fromisoformat(e.findtext("a:published", "", ns).replace("Z", "+00:00")).astimezone(ZoneInfo("Europe/Brussels"))
        g = e.find("{http://search.yahoo.com/mrss/}group")
        d = g.findtext("{http://search.yahoo.com/mrss/}description", "") if g is not None else ""
        out.append({"titel": clean(t, 160), "datum": dt.strftime("%Y-%m-%d"), "_ts": dt.timestamp(), "url": "", "kort": clean(d)})
    out.sort(key=lambda x: -x["_ts"])
    for x in out: x.pop("_ts")
    return out[:n]

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
            try: eps = episodes(find_feed(s))
            except Exception as ex:
                if not s.get("yt"): raise
                print("terugval YouTube-feed:", ex); eps = yt_episodes(s["yt"], s["yt_re"])
                if not eps: raise
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
