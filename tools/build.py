#!/usr/bin/env python3
"""Voegt content.json (nieuws) en health.json (logboek) samen tot data.json."""
import json, sys
c = json.load(open(sys.argv[1])); h = json.load(open(sys.argv[2]))
c["gezondheid"] = h
json.dump(c, open(sys.argv[3], "w"), ensure_ascii=False, indent=1)
print("ok", sys.argv[3])
