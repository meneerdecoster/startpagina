#!/usr/bin/env python3
"""Gezondheidslogboek -> health-blok voor data.json van Michaëls startpagina.

Gebruik:  python3 health.py <pad-naar-Gezondheidslogboek.xlsx> [YYYY-MM-DD]
Schrijft JSON naar stdout. Leest het tabblad van Michaël voor het jaar van de
gevraagde datum (2026 = 'Michaël', 2027 = '27_Michaël', 2025 = '25_Michaël', ...).
"""
import json, sys, datetime as dt, statistics as st
import openpyxl

ALIASES = {
    "fysiek": "fysiek", "fysiek (0 - 2)": "fysiek",
    "mentaal": "mentaal", "mentaal (0 - 2)": "mentaal",
    "sport": "sport", "sp": "sport", "sporttype": "sporttype",
    "ziek": "ziek", "z": "ziek", "koffie": "koffie", "alcohol": "alcohol",
    "water (l)": "water", "sauna": "sauna", "1up": "oneup", "1up?": "oneup",
    "vrijaf": "vrijaf", "vrijaf?": "vrijaf", "notitie": "notitie", "meer uitleg": "notitie",
    "ingevuld op": "ingevuld", "stappen": "stappen", "slaap (u)": "slaap",
    "rusthartslag": "rhr", "hrv": "hrv", "diepe slaap (min)": "diep", "diepe slaap": "diep",
    "rem (min)": "rem", "bedtijd": "bedtijd", "opstaan": "opstaan", "datum": "datum", "dag": "dag",
}
TRUTHY = {"x", "X", 1, 1.0, True, "ja", "1"}


def sheet_for_year(wb, year):
    cur = dt.date.today().year
    names = [f"{str(year)[2:]}_Michaël"]
    if year == 2026:
        names.insert(0, "Michaël")
    for n in names:
        if n in wb.sheetnames:
            return wb[n]
    raise SystemExit(f"Geen tabblad voor Michaël in {year}")


def parse(ws, year):
    rows = list(ws.iter_rows(values_only=True))
    hdr_i = next(i for i, r in enumerate(rows) if any(str(c).strip().lower() == "stappen" for c in r if c))
    cols = {}
    for j, c in enumerate(rows[hdr_i]):
        if c is None:
            continue
        key = ALIASES.get(str(c).strip().lower())
        if key and key not in cols:
            cols[key] = j
    days = []
    for r in rows[hdr_i + 1:]:
        d = next((c for c in r if isinstance(c, (dt.datetime, dt.date))), None)
        if d is None:
            continue
        d = d.date() if isinstance(d, dt.datetime) else d
        try:
            d = d.replace(year=year)  # sommige tabbladen tonen een verkeerd jaartal
        except ValueError:
            continue
        g = lambda k: r[cols[k]] if k in cols and cols[k] < len(r) else None
        rec = {k: g(k) for k in cols}
        rec["date"] = d
        rec["logged"] = any(rec.get(k) not in (None, "") for k in ("stappen", "slaap", "water", "notitie", "ingevuld", "koffie"))
        days.append(rec)
    return days


def num(v):
    try:
        return float(str(v).replace(",", "."))
    except (TypeError, ValueError):
        return None


def avg(vals):
    vals = [v for v in vals if v is not None]
    return round(st.mean(vals), 2) if vals else None


def main():
    path = sys.argv[1]
    today = dt.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else dt.date.today()
    wb = openpyxl.load_workbook(path, data_only=True)
    days = parse(sheet_for_year(wb, today.year), today.year)
    if today.month == 1 and today.day <= 14:  # jaarwissel: neem ook vorig jaar mee
        try:
            days = parse(sheet_for_year(wb, today.year - 1), today.year - 1) + days
        except SystemExit:
            pass
    days = sorted([d for d in days if d["date"] <= today], key=lambda d: d["date"])
    logged = [d for d in days if d["logged"]]
    last = logged[-1] if logged else None

    # reeks: opeenvolgende ingevulde dagen tot gisteren of vandaag
    streak = 0
    cursor = today if (last and last["date"] == today) else today - dt.timedelta(days=1)
    bydate = {d["date"]: d for d in days}
    while bydate.get(cursor, {}).get("logged"):
        streak += 1
        cursor -= dt.timedelta(days=1)

    w7 = [d for d in days if (today - d["date"]).days < 7 and d["date"] < today or d["date"] == today and d["logged"]]
    w7 = [d for d in days if 0 <= (today - d["date"]).days <= 7 and d["logged"]][-7:]
    w14 = [d for d in days if 0 <= (today - d["date"]).days <= 14]

    def series(key):
        return [{"d": d["date"].isoformat(), "v": num(d.get(key)) if d["logged"] else None} for d in w14]

    k = lambda key: [num(d.get(key)) for d in w7]
    kpi = {
        "stappen": avg(k("stappen")), "slaap": avg(k("slaap")), "hrv": avg(k("hrv")),
        "rhr": avg(k("rhr")), "water": avg(k("water")), "diep": avg(k("diep")), "rem": avg(k("rem")),
        "dagen": len(w7),
        "sportdagen": sum(1 for d in w7 if d.get("sport") in TRUTHY),
        "alcoholvrij": sum(1 for d in w7 if (num(d.get("alcohol")) or 0) == 0),
        "koffie": avg(k("koffie")),
        "stappen10k": sum(1 for v in k("stappen") if v and v >= 10000),
        "water3l": sum(1 for v in k("water") if v and v >= 3),
    }

    # jaar-tot-nu (enkel ingevulde dagen)
    ytd = [d for d in logged if d["date"].year == today.year]
    ytd_kpi = {
        "dagen": len(ytd),
        "sport_pct": round(100 * sum(1 for d in ytd if d.get("sport") in TRUTHY) / len(ytd)) if ytd else None,
        "water": avg([num(d.get("water")) for d in ytd]),
        "alcohol_week": round(7 * sum(num(d.get("alcohol")) or 0 for d in ytd) / len(ytd), 1) if ytd else None,
    }

    insights = []
    if kpi["dagen"]:
        if kpi["stappen10k"] == kpi["dagen"]:
            insights.append(f"Elke ingevulde dag deze week boven de 10.000 stappen (gemiddeld {int(kpi['stappen']):,}).".replace(",", "."))
        elif kpi["stappen"]:
            insights.append(f"Gemiddeld {int(kpi['stappen']):,} stappen per dag; {kpi['stappen10k']} van {kpi['dagen']} dagen boven 10.000.".replace(",", "."))
        if kpi["water"] is not None:
            gap = round(3 - kpi["water"], 2)
            insights.append(f"Water: gemiddeld {str(kpi['water']).replace('.', ',')} l. " + (f"Nog {str(gap).replace('.', ',')} l per dag tot je doel van 3 l." if gap > 0 else "Doel van 3 l gehaald."))
        if kpi["alcoholvrij"] == kpi["dagen"]:
            insights.append(f"{kpi['dagen']} van {kpi['dagen']} dagen alcoholvrij.")
        if last and num(last.get("slaap")) and kpi["slaap"] and num(last.get("slaap")) < kpi["slaap"] - 0.5:
            insights.append(f"Afgelopen nacht {str(num(last.get('slaap'))).replace('.', ',')} u slaap, onder je weekgemiddelde van {str(kpi['slaap']).replace('.', ',')} u. Bedtijd was {last.get('bedtijd')}.")
        if last and num(last.get("hrv")) and kpi["hrv"] and num(last.get("hrv")) > kpi["hrv"] * 1.08:
            insights.append(f"HRV laatst gemeten op {int(num(last.get('hrv')))}, boven je gemiddelde ({int(kpi['hrv'])}). Goed hersteld.")
    if last and (today - last["date"]).days >= 2:
        insights.insert(0, f"Laatste invoer was {last['date'].strftime('%d/%m')}. Even bijwerken?")
    if not logged:
        insights.append("Nog niets ingevuld dit jaar.")

    out = {
        "streak": streak,
        "laatste": {
            "datum": last["date"].isoformat() if last else None,
            "stappen": num(last.get("stappen")) if last else None,
            "slaap": num(last.get("slaap")) if last else None,
            "hrv": num(last.get("hrv")) if last else None,
            "rhr": num(last.get("rhr")) if last else None,
            "water": num(last.get("water")) if last else None,
            "sporttype": last.get("sporttype") if last else None,
            "bedtijd": last.get("bedtijd") if last else None,
            "opstaan": last.get("opstaan") if last else None,
        },
        "week": kpi,
        "jaar": ytd_kpi,
        "reeksen": {"stappen": series("stappen"), "slaap": series("slaap"), "hrv": series("hrv")},
        "inzichten": insights,
        "logboek_url": "https://docs.google.com/spreadsheets/d/1sesegvvXNE2gad7gHHlkSNobu6emh-iQlCn71dA4Hi8/edit",
    }
    print(json.dumps(out, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
