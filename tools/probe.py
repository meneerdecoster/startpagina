import json, urllib.request
UA = {"User-Agent": "Mozilla/5.0 (compatible; StartpaginaBot/1.0)"}
out = []
for t in ["SPYI.DE","0GGH.L","IB1T.PA","IB1T.DE","XS2940466316.SG","PHAG.AS"]:
    for rng in ["1d","5d"]:
        try:
            u = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range={rng}&interval=1d"
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20))["chart"]["result"][0]
            m = r["meta"]
            p = m.get("regularMarketPrice"); prev = m.get("chartPreviousClose"); pc = m.get("previousClose")
            out.append(f"{t}\t{rng}\tprice={p}\tchartPrev={prev}\tprevClose={pc}\t{((p/prev-1)*100 if p and prev else float('nan')):.2f}%\tkeys={[k for k in m if 'rev' in k or 'hange' in k]}")
        except Exception as e:
            out.append(f"{t}\t{rng}\tFOUT {e}")
open("probe.txt", "w").write("\n".join(out) + "\n"); print("\n".join(out))
