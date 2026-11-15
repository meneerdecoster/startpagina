import json, urllib.request, sys
UA = {"User-Agent": "Mozilla/5.0 (compatible; StartpaginaBot/1.0)"}
cands = ["0GGH.L","IB1T.PA","IB1T.SW","IB1T.DE"] + ["XS2940466316"+s for s in ["",".SG",".F",".DE",".BE",".MU",".HM",".DU",".HA",".VI",".AS",".PA",".MI"]]
out = []
for t in cands:
    try:
        u = f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=10d&interval=1d"
        j = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20))
        r = j["chart"]["result"][0]
        cl = [c for c in r["indicators"]["quote"][0]["close"] if c is not None]
        out.append(f"{t}\t{r['meta'].get('currency')}\t{r['meta'].get('exchangeName')}\t{cl[-1]:.4f}\t{(cl[-1]/cl[-2]-1)*100:.2f}%")
    except Exception as e:
        out.append(f"{t}\tFOUT {e}")
open("probe.txt", "w").write("\n".join(out) + "\n")
print("\n".join(out))
