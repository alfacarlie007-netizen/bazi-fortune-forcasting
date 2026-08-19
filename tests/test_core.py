#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_core.py — Uji otomatis mesin Bazi (stdlib unittest).

Ancangan validasi:
  1. Anchor tanggal bersejarah yang gan-zhinya sudah dikenal luas:
     - 1949-10-01 (HUT RRT) = hari 甲子
     - 2000-01-01 = hari 戊午
     - 1984 = tahun 甲子 (mulai 立春 4 Feb 1984)
  2. Konsistensi internal: pilar, 藏干, 十神, 纳音, siklus, 节气.
  3. Sifat matematis: pilar hari maju 1 per hari; bulan bergeser di 节.

Jalankan:  python3 tests/test_core.py -v
"""

import sys
import os
import unittest
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bazi_core import (STEMS, BRANCHES, STEM_ELEMENT, BRANCH_ELEMENT, HIDDEN,
                       NAYIN, GENERATES, CONTROLS, LIUHE, LIUCHONG,
                       jdn_from_ymd, day_ganzhi, year_ganzhi, hour_branch_index,
                       hour_stem_index, month_stem_index, ten_god, na_yin,
                       cycle_index, ganzhi_from_index, li_chun, find_jie_time,
                       build_chart, compute_da_yun, compute_liu_nian_range,
                       compute_liu_yue, true_solar_time)


class TestGanzhi(unittest.TestCase):
    def test_known_days(self):
        # 1949-10-01 = 甲子 (hari proklamasi RRT, terkenal)
        self.assertEqual(day_ganzhi(datetime(1949, 10, 1, 12)), (0, 0))
        # 2000-01-01 = 戊午
        self.assertEqual(day_ganzhi(datetime(2000, 1, 1, 12)), (4, 6))
        # hari bertambah 1 setiap hari
        d1 = day_ganzhi(datetime(2000, 1, 1, 12))
        d2 = day_ganzhi(datetime(2000, 1, 2, 12))
        self.assertEqual((d2[0] - d1[0]) % 10, 1)
        self.assertEqual((d2[1] - d1[1]) % 12, 1)
        # pergantian hari jam 23:00
        self.assertEqual(day_ganzhi(datetime(2000, 1, 1, 22, 59)),
                         day_ganzhi(datetime(2000, 1, 1, 12)))
        self.assertEqual(day_ganzhi(datetime(2000, 1, 1, 23, 0)),
                         day_ganzhi(datetime(2000, 1, 2, 12)))

    def test_year(self):
        # 1984 = 甲子 (index 0,0) mulai 立春
        self.assertEqual(year_ganzhi(1984), (0, 0))
        # 2026 = 丙午: (2026-4)%10=2 (丙), (2026-4)%12=6 (午)
        self.assertEqual(year_ganzhi(2026), (2, 6))
        # sebelum 立春 1984 masih tahun 癸亥
        chart = build_chart(datetime(1984, 2, 2, 12, 0), "pria")
        self.assertEqual(chart.year_pillar.stem, "癸")
        self.assertEqual(chart.year_pillar.branch, "亥")
        chart2 = build_chart(datetime(1984, 2, 5, 12, 0), "pria")
        self.assertEqual(chart2.year_pillar.stem + chart2.year_pillar.branch, "甲子")

    def test_hour_branch(self):
        self.assertEqual(hour_branch_index(0), 0)    # 00:00 子
        self.assertEqual(hour_branch_index(23), 0)   # 23:00 子
        self.assertEqual(hour_branch_index(1), 1)    # 01:00 丑
        self.assertEqual(hour_branch_index(11), 6)   # 11:00 午
        self.assertEqual(hour_branch_index(13), 7)   # 13:00 未
        self.assertEqual(hour_branch_index(21), 11)  # 21:00 亥

    def test_hour_stem_wushu(self):
        # 五鼠遁: 甲己 -> 甲子; 乙庚 -> 丙子; 丙辛 -> 戊子; 丁壬 -> 庚子; 戊癸 -> 壬子
        self.assertEqual(hour_stem_index(0, 0), 0)
        self.assertEqual(hour_stem_index(5, 0), 0)
        self.assertEqual(hour_stem_index(1, 0), 2)
        self.assertEqual(hour_stem_index(6, 0), 2)
        self.assertEqual(hour_stem_index(2, 0), 4)
        self.assertEqual(hour_stem_index(7, 0), 4)
        self.assertEqual(hour_stem_index(3, 0), 6)
        self.assertEqual(hour_stem_index(8, 0), 6)
        self.assertEqual(hour_stem_index(4, 0), 8)
        self.assertEqual(hour_stem_index(9, 0), 8)

    def test_month_stem_wuhu(self):
        # 五虎遁: 甲己年 -> 丙寅; 乙庚 -> 戊寅; 丙辛 -> 庚寅; 丁壬 -> 壬寅; 戊癸 -> 甲寅
        self.assertEqual(month_stem_index(0, 0), 2)
        self.assertEqual(month_stem_index(5, 0), 2)
        self.assertEqual(month_stem_index(1, 0), 4)
        self.assertEqual(month_stem_index(6, 0), 4)
        self.assertEqual(month_stem_index(2, 0), 6)
        self.assertEqual(month_stem_index(7, 0), 6)
        self.assertEqual(month_stem_index(3, 0), 8)
        self.assertEqual(month_stem_index(8, 0), 8)
        self.assertEqual(month_stem_index(4, 0), 0)
        self.assertEqual(month_stem_index(9, 0), 0)

    def test_ten_god(self):
        self.assertEqual(ten_god("甲", "甲"), "比肩")
        self.assertEqual(ten_god("甲", "乙"), "劫财")
        self.assertEqual(ten_god("甲", "丙"), "食神")
        self.assertEqual(ten_god("甲", "丁"), "伤官")
        self.assertEqual(ten_god("甲", "戊"), "偏财")
        self.assertEqual(ten_god("甲", "己"), "正财")
        self.assertEqual(ten_god("甲", "庚"), "七杀")
        self.assertEqual(ten_god("甲", "辛"), "正官")
        self.assertEqual(ten_god("甲", "壬"), "偏印")
        self.assertEqual(ten_god("甲", "癸"), "正印")

    def test_nayin(self):
        self.assertEqual(na_yin(0), "海中金")    # 甲子
        self.assertEqual(na_yin(1), "海中金")    # 乙丑
        self.assertEqual(na_yin(58), "大海水")   # 壬戌
        self.assertEqual(na_yin(59), "大海水")   # 癸亥

    def test_cycle(self):
        self.assertEqual(cycle_index(0, 0), 0)
        self.assertEqual(cycle_index(9, 11), 59)
        self.assertEqual(ganzhi_from_index(0), "甲子")
        self.assertEqual(ganzhi_from_index(59), "癸亥")
        for i in range(60):
            self.assertEqual(cycle_index(i % 10, i % 12), i)


class TestSolarTerms(unittest.TestCase):
    def test_jie_date_ranges(self):
        # rentang tanggal 节气 yang dikenal (almanak umum)
        cases = [
            (2026, 315, (2, 3), (2, 5)),    # 立春
            (2026, 345, (3, 5), (3, 7)),    # 惊蛰
            (2026, 15, (4, 4), (4, 6)),     # 清明
            (2026, 75, (6, 5), (6, 7)),     # 芒种
            (2026, 105, (7, 6), (7, 8)),    # 小暑
            (2026, 165, (9, 7), (9, 9)),    # 白露
            (2026, 225, (11, 6), (11, 8)),  # 立冬
            (2026, 285, (1, 4), (1, 6)),    # 小寒
        ]
        for year, angle, (m1, d1), (m2, d2) in cases:
            t = find_jie_time(year, angle, {315: 2, 345: 3, 15: 4, 75: 6,
                                            105: 7, 165: 9, 225: 11, 285: 1}[angle])
            self.assertGreaterEqual((t.month, t.day), (m1, d1))
            self.assertLessEqual((t.month, t.day), (m2, d2))

    def test_li_chun_2026(self):
        t = li_chun(2026)
        self.assertEqual(t.month, 2)
        self.assertIn(t.day, (3, 4, 5))


class TestChart(unittest.TestCase):
    def test_full_chart_consistency(self):
        for dt in [datetime(1995, 8, 17, 9, 30), datetime(2000, 1, 1, 0, 0),
                   datetime(1984, 2, 5, 23, 30), datetime(2026, 12, 31, 23, 59)]:
            c = build_chart(dt, "pria")
            # semua pilar valid
            for p in c.pillars:
                self.assertIn(p.stem, STEMS)
                self.assertIn(p.branch, BRANCHES)
                self.assertIn(p.stem_element, GENERATES)
                self.assertIn(p.branch_element, GENERATES)
                self.assertTrue(p.hidden)
                for h, hel, htg, w in p.hidden:
                    self.assertIn(h, STEMS)
                    self.assertEqual(STEM_ELEMENT[h], hel)
            # unsur selalu lengkap 5 macam (skor > 0 utk semua? bisa 0 utk yg langka)
            self.assertEqual(set(c.element_score), set(GENERATES))
            # 十神 batang selalu berupa salah satu dari 10 十神
            ALL_TG = ["比肩", "劫财", "食神", "伤官", "偏财", "正财",
                      "七杀", "正官", "偏印", "正印"]
            for p in c.pillars:
                self.assertIn(p.ten_god_stem, ALL_TG)
                self.assertIn(p.ten_god_branch, ALL_TG)
            # da yun 10 fase, berurutan usia
            dys = compute_da_yun(c)
            self.assertEqual(len(dys), 10)
            for i, dy in enumerate(dys):
                self.assertEqual(dy.start_age, dys[0].start_age + i * 10)
                self.assertEqual(dy.end_age, dy.start_age + 9)
            # 流年
            lns = compute_liu_nian_range(c, 2026, 2030, dys)
            self.assertEqual(len(lns), 5)
            for ln in lns:
                self.assertGreaterEqual(ln.score, 5)
                self.assertLessEqual(ln.score, 98)
            # 流月 12 bulan
            lms = compute_liu_yue(c, 2026)
            self.assertEqual(len(lms), 12)

    def test_month_pillar_boundary(self):
        # 1995: 立秋 sekitar 8 Agustus -> sebelum = 未月, sesudah = 申月
        c1 = build_chart(datetime(1995, 8, 7, 12, 0), "pria")
        c2 = build_chart(datetime(1995, 8, 9, 12, 0), "pria")
        self.assertEqual(c1.month_pillar.branch, "未")
        self.assertEqual(c2.month_pillar.branch, "申")
        # batang bulan via 五虎遁 tahun 乙 (index 1): 申月 pos 6 -> (2*1+2+6)%10 = 0 -> 甲
        self.assertEqual(c2.month_pillar.stem, "甲")
        self.assertEqual(c2.month_pillar.gan_zhi if hasattr(c2.month_pillar, "gan_zhi") else
                         c2.month_pillar.stem + c2.month_pillar.branch, "甲申")

    def test_true_solar(self):
        # Jakarta: bujur 106.85, meridian WIB 105 -> +7.4 menit + EoT
        dt = datetime(2026, 8, 17, 9, 30)
        ts = true_solar_time(dt, 106.85, 7.0)
        diff = (ts - dt).total_seconds() / 60.0
        # EoT Agustus sekitar -4..-6 menit, jadi total antara -5 dan +12 menit
        self.assertGreater(diff, -10)
        self.assertLess(diff, 15)


if __name__ == "__main__":
    unittest.main(verbosity=2)
