#!/usr/bin/env python3
"""Gezondheidslogboek -> gezondheid-blok voor Sévérines pagina (severine.json).
Gebruik: python3 health_s.py <Gezondheidslogboek.xlsx> [YYYY-MM-DD]
Leest haar tabblad ('Sévérine' = 2026, '27_Sévérine' = 2027, ...). Geen stappen/Apple Watch.
De kolom 'SE' wordt bewust nooit gelezen of getoond."""
import json, sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import openpyxl
from health import parse, sheet_for_year, num, avg, TRUTHY

def main():
    wb = openpyxl.load_workbook(sys.argv[1], data_only=True)
    today = dt.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else dt.date.today()
    P = "Sévérine"
    days = parse(sheet_for_year(wb, today.year, P), today.year)
    if today.month == 1 and today.day <= 14:
        try: days = parse(sheet_for_year(wb, today.year - 1, P), today.year - 1) + days
        except SystemExit: pass
    days = sorted([d for d in days if d["date"] <= today], key=lambda d: d["date"])
    for d in days:  # enkel dagen waarop effectief iets is ingevuld
        d["logged"] = any(d.get(k) not in (None, "") for k in ("water", "koffie", "alcohol", "notitie"))
    logged = [d for d in days if d["logged"]]
    last = logged[-1] if logged else None
    by = {d["date"]: d for d in days}
    streak, cur = 0, (today if last and last["date"] == today else today - dt.timedelta(days=1))
    while by.get(cur, {}).get("logged"):
        streak += 1; cur -= dt.timedelta(days=1)
    w7 = [d for d in logged if 0 <= (today - d["date"]).days <= 6]
    w14 = [d for d in days if 0 <= (today - d["date"]).days <= 13]
    series = lambda k: [{"d": d["date"].isoformat(), "v": num(d.get(k)) if d["logged"] else None} for d in w14]
    k = lambda key: [num(d.get(key)) for d in w7]
    w = {"dagen": len(w7), "water": avg(k("water")), "koffie": avg(k("koffie")),
         "sport": sum(1 for d in w7 if d.get("sport") in TRUTHY),
         "sauna": sum(1 for d in w7 if (num(d.get("sauna")) or 0) > 0),
         "alcoholvrij": sum(1 for d in w7 if (num(d.get("alcohol")) or 0) == 0),
         "alcohol": round(sum(num(d.get("alcohol")) or 0 for d in w7), 1),
         "fysiek": avg(k("fysiek")), "mentaal": avg(k("mentaal")),
         "ziek": sum(1 for d in w7 if d.get("ziek") in TRUTHY),
         "water25": sum(1 for v in k("water") if v and v >= 2.5)}
    ytd = [d for d in logged if d["date"].year == today.year]
    jaar = {"dagen": len(ytd),
            "sport_pct": round(100 * sum(1 for d in ytd if d.get("sport") in TRUTHY) / len(ytd)) if ytd else None,
            "water": avg([num(d.get("water")) for d in ytd]),
            "alcohol_week": round(7 * sum(num(d.get("alcohol")) or 0 for d in ytd) / len(ytd), 1) if ytd else None,
            "sauna": sum(1 for d in ytd if (num(d.get("sauna")) or 0) > 0),
            "oneup": sum(1 for d in ytd if (num(d.get("oneup")) or 0) > 0)}
    nl = lambda v: str(v).replace(".", ",")
    ins = []
    if w["dagen"]:
        if w["water"] is not None:
            gap = round(2.5 - w["water"], 2)
            ins.append(f"Water: gemiddeld {nl(w['water'])} l per dag. " + (f"Nog {nl(gap)} l tot je doel van 2,5 l." if gap > 0 else "Doel van 2,5 l gehaald."))
        if w["alcoholvrij"] == w["dagen"]: ins.append(f"{w['dagen']} van {w['dagen']} dagen alcoholvrij.")
        elif w["alcohol"]: ins.append(f"{nl(w['alcohol'])} glazen alcohol in {w['dagen']} dagen.")
        if w["sport"]: ins.append(f"{w['sport']} sportdag{'en' if w['sport'] != 1 else ''} deze week.")
        if w["sauna"]: ins.append(f"{w['sauna']}× in de sauna deze week.")
        if w["ziek"]: ins.append(f"{w['ziek']} dag{'en' if w['ziek'] != 1 else ''} ziek gemeld.")
    if last and (today - last["date"]).days >= 2:
        ins.insert(0, f"Laatste invoer was {last['date'].strftime('%d/%m')}. Even bijwerken?")
    if not logged: ins.append("Nog niets ingevuld dit jaar.")
    L = last or {}
    out = {"streak": streak,
           "laatste": {"datum": L["date"].isoformat() if L else None, "water": num(L.get("water")) if L else None,
                       "sporttype": L.get("sporttype") if L else None, "notitie": None},
           "week": w, "jaar": jaar,
           "reeksen": {"water": series("water"), "koffie": series("koffie"), "alcohol": series("alcohol")},
           "inzichten": ins}
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))
if __name__ == "__main__": main()
