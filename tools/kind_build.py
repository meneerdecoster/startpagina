#!/usr/bin/env python3
"""Bouwt ida.html, otto.html en severine.html uit tools/kind.tpl.html (config per persoon hieronder)."""
import json

SKY = lambda a,b,c,d: "\n".join(
    f'.hero[data-part="{k}"]{{--sky:linear-gradient(160deg,{v})}}' for k,v in
    zip(("ochtend","middag","avond","nacht"),(a,b,c,d)))

DEF_SKY = SKY("#FF9A62 0%,#F7678A 38%,#5B5BD6 78%,#2B2F77 100%","#38BDF8 0%,#2F7FE0 45%,#1D4ED8 75%,#1E2A78 100%",
              "#F97362 0%,#B83A7A 35%,#3B1D6E 72%,#0F1030 100%","#1E2A55 0%,#121A3A 50%,#05070F 100%")

P = {
 "ida": dict(
  titel="Idas Startpagina", accent="#EC4899", icoon="icon-ida.png",
  sky=SKY("#FFB38A 0%,#FF7EB6 40%,#B47BFF 80%,#6A4FD6 100%","#7DD3FC 0%,#A78BFA 50%,#F472B6 100%",
          "#FB7185 0%,#C026D3 45%,#5B21B6 80%,#1E1B4B 100%","#312E81 0%,#1E1B4B 55%,#0B0B24 100%"),
  iconen=["🦄","🌈","🦋","🌸","⭐","💖","🐱","🐶","🎀","🍓","🧁","🌷"],
  groet={
   "ochtend":["Goeiemorgen, {naam}!","Hoi {naam}! Klaar voor een toffe {dag}?","Goeiemorgen, zonnetje!","Hey {naam}, wat gaan we vandaag beleven?","Nieuwe dag, nieuwe avonturen, {naam}!","Opstaan, slaapkop! 😄","Fijne {dag}, {naam}!"],
   "middag":["Goeiemiddag, {naam}!","Hoi {naam}, alles goed?","Smakelijk, {naam}!","Hey {naam}, hoe is je {dag}?","Even pauze, {naam}?"],
   "avond":["Goeienavond, {naam}!","Gezellige {dag}avond, {naam}!","Hey {naam}, wat was het leukste van vandaag?","Bijna bedtijd, {naam}!"],
   "nacht":["Slaap zacht, {naam}!","Welterusten, {naam}! 🌙","Droom maar fijn, {naam}!"]},
  sub={"ochtend":["Dit is er vandaag te beleven voor jou.","Kijk eens wat er vandaag nieuw is!"],"middag":["Tijd voor wat leuks lezen en kijken.","Kijk eens wat er nieuw is!"],"avond":["Nog even snuisteren voor het slapengaan.","Zie je morgen weer?"],"nacht":["Tijd om te gaan slapen."]},
  secties=[
   dict(key="nieuws",type="news",titel="Karrewiet",meta="Nieuws voor jou",span=7,kleur="#EF4444"),
   dict(key="raadsel",type="quiz",titel="Raadsel van de dag",meta="Kan jij het oplossen?",span=5,kleur="#8B5CF6"),
   dict(key="dieren",type="media",titel="Schattig",meta="Hondjes en katjes",span=5,kleur="#F59E0B",max=2),
   dict(key="mensen",type="media",titel="Je favorieten",meta="Camille · Pommelien · Aaron · Maksim",span=7,kleur="#EC4899"),
   dict(key="land",type="land",titel="Land van de week",meta="Elke week een nieuw land",span=12,kleur="#10B981"),
   dict(key="films",type="media",titel="Tekenfilms",meta="Pixar en Disney",span=12,kleur="#3B82F6"),
  ]),
 "otto": dict(
  titel="Otto's Startpagina", accent="#0EA5E9", icoon="icon-otto.png",
  sky=SKY("#FDBA74 0%,#38BDF8 45%,#2563EB 80%,#1E3A8A 100%","#67E8F9 0%,#3B82F6 50%,#1D4ED8 100%",
          "#FB923C 0%,#DB2777 40%,#4338CA 80%,#0F172A 100%","#1E3A8A 0%,#0F172A 60%,#020617 100%"),
  iconen=["🚀","⚽","🦖","🦈","🤖","🌍","⭐","🪐","🦁","🏎️","🔭","🐙"],
  groet={
   "ochtend":["Goeiemorgen, {naam}!","Hoi {naam}! Klaar voor een avontuur?","Goeiemorgen, ontdekkingsreiziger!","Hey {naam}, wat ontdek jij vandaag?","Fijne {dag}, {naam}!","Opstaan, kapitein {naam}! 🚀","Nieuwe dag, nieuwe missie!"],
   "middag":["Goeiemiddag, {naam}!","Hoi {naam}, alles goed?","Smakelijk, {naam}!","Hey {naam}, hoe is je {dag}?","Missie voltooid, tijd voor pauze!"],
   "avond":["Goeienavond, {naam}!","Gezellige {dag}avond, {naam}!","Hey {naam}, wat was het coolste van vandaag?","Bijna bedtijd, astronaut!"],
   "nacht":["Slaap zacht, {naam}!","Welterusten, {naam}! 🌙","Droom maar fijn, {naam}!"]},
  sub={"ochtend":["Dit is er vandaag te ontdekken voor jou.","Kijk eens wat er vandaag nieuw is!"],"middag":["Tijd voor wat coole weetjes.","Kijk eens wat er nieuw is!"],"avond":["Nog even snuisteren voor het slapengaan.","Zie je morgen weer?"],"nacht":["Tijd om te gaan slapen."]},
  secties=[
   dict(key="nieuws",type="news",titel="Karrewiet",meta="Nieuws voor jou",span=7,kleur="#EF4444"),
   dict(key="raadsel",type="quiz",titel="Wiskunderaadsel",meta="Kan jij het oplossen?",span=5,kleur="#10B981"),
   dict(key="wetenschap",type="feiten",titel="Wist je dat?",meta="Ruimte · dieren · lichaam",span=12,kleur="#8B5CF6",breed=True),
   dict(key="films",type="media",titel="Nieuwe films",meta="Pixar en Disney",span=12,kleur="#3B82F6"),
   dict(key="duivels",type="news",titel="Rode Duivels",meta="Voetbal",span=7,kleur="#DC2626"),
   dict(key="mop",type="mop",titel="Mop van de dag",meta="Even lachen",span=5,kleur="#F59E0B"),
   dict(key="land",type="land",titel="Land van de week",meta="Elke week een nieuw land",span=12,kleur="#0EA5E9"),
  ]),
 "severine": dict(
  titel="Sévérines Startpagina", accent="#E03A3E", icoon="icon-severine.png",
  sky=DEF_SKY, iconen=[],
  groet={
   "ochtend":["Goeiemorgen, {naam}","Fijne {dag}, {naam}","Hey {naam}, klaar voor vandaag?","Bonjour, {naam}","Een frisse {dag}, {naam}"],
   "middag":["Fijne middag, {naam}","Hoi {naam}, alles goed?","Smakelijk, {naam}"],
   "avond":["Goeienavond, {naam}","Fijne {dag}avond, {naam}","Tijd om te landen, {naam}"],
   "nacht":["Nog wakker, {naam}?","Slaap zacht straks, {naam}"]},
  sub={"ochtend":["Je dag in één oogopslag."],"middag":["Even bijlezen."],"avond":["Rustig afronden."],"nacht":["Kort bijlezen en dan slapen."]},
  secties=[
   dict(key="gezondheid",type="gezond",titel="Gezondheid",meta="Je logboek",span=12,kleur="#0E9F6E"),
   dict(key="lifestyle",type="news",titel="Lifestyle",meta="Mode · wonen · interieur",span=12,kleur="#E03A3E",kolommen=True),
   dict(key="voeding",type="news",titel="Voeding",meta="Recepten · gezond leven",span=12,kleur="#10B981",kolommen=True),
   dict(key="boeken",type="tiles",titel="Nieuwe boeken",meta="Nederlandstalig",span=12,kleur="#8B5CF6",emoji="📖",portret=True),
   dict(key="uitgaan",type="uitgaan",titel="Uitgaan in de buurt",meta="Muziek · comedy",span=12,kleur="#6366F1"),
  ]),
}
NAMEN={"ida":"Ida","otto":"Otto","severine":"Sévérine"}
tpl=open("tools/kind.tpl.html",encoding="utf-8").read()
for k,p in P.items():
    cfg=dict(naam=NAMEN[k],json=f"{k}.json",iconen=p["iconen"],groet=p["groet"],sub=p["sub"],secties=p["secties"])
    out=(tpl.replace("__TITLE__",p["titel"]).replace("__ICON__",p["icoon"]+"?v=1").replace("__ACCENT__",p["accent"])
            .replace("__SKIES__",p["sky"]).replace("/*CFG*/{}",json.dumps(cfg,ensure_ascii=False)))
    open(f"{k}.html","w",encoding="utf-8").write(out)
    print("gebouwd",k)
