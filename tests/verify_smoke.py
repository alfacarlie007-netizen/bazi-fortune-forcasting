#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_smoke.py — Pemeriksaan cepat (smoke test) hasil perbaikan:
  - resolve bujur/zona dari kota
  - 喜用/忌 tidak boleh tumpang tindih
  - bagan contoh yang dikenal

Jalankan:  python3 tests/verify_smoke.py
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bazi_core import build_chart

OK = True


def check(name, cond):
    global OK
    status = "PASS" if cond else "FAIL"
    if not cond:
        OK = False
    print(f"  [{status}] {name}")


print("== Smoke test ==")

# 1) resolve bujur dari kota
c = build_chart(datetime(2000, 1, 1, 12, 0), "pria", city="jakarta", apply_true_solar=True)
check("bujur Jakarta terresolve ~106.85", abs(c.longitude - 106.85) < 0.01)
check("zona Jakarta = 7", c.tz == 7.0)

# 2) 喜用 vs 忌 tidak tumpang tindih
overlap = set(c.favorable) & set(c.unfavorable)
check("2000-01-01 喜用/忌 tidak tumpang tindih", not overlap)
print(f"     2000-01-01: 喜用={c.favorable} 忌={c.unfavorable}")

c2 = build_chart(datetime(1995, 8, 17, 9, 30), "wanita", city="semarang", apply_true_solar=True)
overlap2 = set(c2.favorable) & set(c2.unfavorable)
check("1995-08-17 喜用/忌 tidak tumpang tindih", not overlap2)
print(f"     1995-08-17: bagan={c2.ganzhi} 喜用={c2.favorable} 忌={c2.unfavorable}")

# 3) bagan 1995-08-17: tahun 乙亥, bulan 甲申 (乙年 五虎遁 -> 甲申)
check("tahun 1995-08-17 = 乙亥", c2.year_pillar.stem == "乙" and c2.year_pillar.branch == "亥")
check("bulan 1995-08-17 = 甲申", c2.month_pillar.stem == "甲" and c2.month_pillar.branch == "申")

# 4) 2000-01-01 12:00 = 己卯 丙子 戊午 戊午 (bagan millennium terkenal)
check("2000-01-01 12:00 = 己卯丙子戊午戊午", c.ganzhi == "己卯丙子戊午戊午")

# 5) kasus tanpa kota: tidak ada koreksi
c3 = build_chart(datetime(1990, 5, 20, 10, 0), "pria")
check("tanpa kota: longitude None", c3.longitude is None)
check("tanpa kota: true_solar == birth", c3.true_solar == c3.birth)

# 6) lintas rentang: banyak tanggal acak, 喜用/忌 konsisten
import random
random.seed(42)
ok_all = True
for _ in range(50):
    dt = datetime(random.randint(1920, 2100), random.randint(1, 12),
                  random.randint(1, 28), random.randint(0, 23), random.randint(0, 59))
    g = random.choice(["pria", "wanita"])
    cc = build_chart(dt, g)
    if set(cc.favorable) & set(cc.unfavorable):
        ok_all = False
        print(f"     OVERLAP pada {dt} {g}: {cc.favorable} / {cc.unfavorable}")
    if cc.strength["total"] <= 0:
        ok_all = False
check("50 tanggal acak: 喜用/忌 konsisten", ok_all)

print()
print("SEMUA LULUS" if OK else "ADA KEGAGALAN")
sys.exit(0 if OK else 1)
