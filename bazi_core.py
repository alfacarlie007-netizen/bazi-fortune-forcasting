# -*- coding: utf-8 -*-
"""
bazi_core.py — Mesin perhitungan Bazi (Empat Pilar / 四柱) murni Python.

TANPA dependensi eksternal (hanya stdlib). Semua perhitungan dilakukan
langsung dan transparan:

  1. Kalender & astronomi
     - Julian Day Number (JDN) dari tanggal Masehi
     - Posisi matahari (bujur ekliptika semu) via algoritma Meeus
     - Waktu 24 节气 (solar terms) — khususnya 12 "节" penentu pilar bulan
     - Koreksi waktu matahari sejati (真太阳时) dari bujur & zona waktu
  2. Empat Pilar (年柱, 月柱, 日柱, 时柱)
     - Batas tahun: 立春;  batas bulan: 12 节;  batas hari: jam 23:00
     - Batang (天干) & Cabang (地支), elemen 五行, yin/yang
     - 纳音 (Na Yin), 藏干 (hidden stems), 十神 (Ten Gods)
     - 神煞: 天乙贵人, 文昌, 桃花, 驿马, 华盖, 将星, 禄神, 羊刃
     - 空亡 (Kong Wang), 胎元, 命宫
  3. Analisis kekuatan Hari Utama (日主) & penentuan unsur keberuntungan
     (喜用神 / 忌神) — metode skor 扶抑 yang transparan
  4. 大运 (Da Yun / siklus 10 tahunan) — arah, usia mulai, pilar-pilar
  5. 流年 (Liu Nian / peruntungan tahunan) & 流月 (bulanan)

Referensi utama:
  - J. Meeus, "Astronomical Algorithms" (posisi matahari, equation of time)
  - Konvensi paipan umum: pergantian hari jam 23:00, pergantian tahun 立春.

Penulis: Meong (Hermes Agent) untuk Bang.
Lisensi: MIT.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# 1. TABEL DASAR
# ---------------------------------------------------------------------------

# 天干 (10 batang langit)
STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]

# 地支 (12 cabang bumi)
BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# Elemen 五行 tiap batang
STEM_ELEMENT = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}

# Elemen utama tiap cabang
BRANCH_ELEMENT = {
    "子": "水", "丑": "土", "寅": "木", "卯": "木", "辰": "土", "巳": "火",
    "午": "火", "未": "土", "申": "金", "酉": "金", "戌": "土", "亥": "水",
}

# Polaritas (Yin/Yang): indeks genap = Yang
def polarity(stem: str) -> str:
    return "Yang" if STEMS.index(stem) % 2 == 0 else "Yin"

# 藏干 (batang tersembunyi di dalam cabang) — urutan: qi utama, qi tengah, qi sisa
HIDDEN = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}

# Bobot qi dalam cabang (本气 0.6 / 中气 0.3 / 余气 0.1)
HIDDEN_WEIGHTS = [0.6, 0.3, 0.1]

# 纳音 (Na Yin) — 30 pasang untuk 60 siklus (indeks siklus // 2)
NAYIN = [
    "海中金", "炉中火", "大林木", "路旁土", "剑锋金",
    "山头火", "涧下水", "城头土", "白蜡金", "杨柳木",
    "泉中水", "屋上土", "霹雳火", "松柏木", "长流水",
    "沙中金", "山下火", "平地木", "壁上土", "金箔金",
    "覆灯火", "天河水", "大驿土", "钗钏金", "桑柘木",
    "大溪水", "沙中土", "天上火", "石榴木", "大海水",
]

# Siklus generasi (生) & kontrol (克) antar unsur
GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
CONTROLS = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}


def element_that_controls(el: str) -> str:
    """Unsur X yang menguasai (克) unsur `el`. Contoh: pengontrol 土 adalah 木."""
    for x, y in CONTROLS.items():
        if y == el:
            return x
    raise ValueError(f"tidak ada unsur pengontrol untuk {el}")


def element_that_generates(el: str) -> str:
    """Unsur X yang melahirkan (生) unsur `el`. Contoh: pelahir 土 adalah 火."""
    for x, y in GENERATES.items():
        if y == el:
            return x
    raise ValueError(f"tidak ada unsur pelahir untuk {el}")

# 六合 (enam kombinasi)
LIUHE = {
    "子": "丑", "丑": "子", "寅": "亥", "亥": "寅",
    "卯": "戌", "戌": "卯", "辰": "酉", "酉": "辰",
    "巳": "申", "申": "巳", "午": "未", "未": "午",
}

# 六冲 (enam benturan)
LIUCHONG = {
    "子": "午", "午": "子", "丑": "未", "未": "丑",
    "寅": "申", "申": "寅", "卯": "酉", "酉": "卯",
    "辰": "戌", "戌": "辰", "巳": "亥", "亥": "巳",
}

# 六害 (enam gangguan)
LIUHAI = {
    "子": "未", "未": "子", "丑": "午", "午": "丑",
    "寅": "巳", "巳": "寅", "卯": "辰", "辰": "卯",
    "申": "亥", "亥": "申", "酉": "戌", "戌": "酉",
}

# 三合 (tiga kombinasi) → unsur hasil
SANHE = {
    "申": ("水", ["子", "辰"]), "子": ("水", ["申", "辰"]), "辰": ("水", ["申", "子"]),
    "亥": ("木", ["卯", "未"]), "卯": ("木", ["亥", "未"]), "未": ("木", ["亥", "卯"]),
    "寅": ("火", ["午", "戌"]), "午": ("火", ["寅", "戌"]), "戌": ("火", ["寅", "午"]),
    "巳": ("金", ["酉", "丑"]), "酉": ("金", ["巳", "丑"]), "丑": ("金", ["巳", "酉"]),
}

# 三刑 & 自刑
XING_GROUPS = [{"寅", "巳", "申"}, {"丑", "戌", "未"}, {"子", "卯"}]
ZIXING = {"辰", "午", "酉", "亥"}

# 10 天干 index → 节气 sudut bujur matahari (dalam derajat) untuk 12 "节"
# (节 penentu pilar bulan): 立春315, 惊蛰345, 清明15, 立夏45, 芒种75,
#  小暑105, 立秋135, 白露165, 寒露195, 立冬225, 大雪255, 小寒285
# Format: (sudut_bujur, bulan_masehi_perkiraan)
JIE = [
    (315, 2),   # 立春 -> bulan Masehi ~Feb
    (345, 3),   # 惊蛰 -> ~Mar
    (15, 4),    # 清明 -> ~Apr
    (45, 5),    # 立夏 -> ~Mei
    (75, 6),    # 芒种 -> ~Jun
    (105, 7),   # 小暑 -> ~Jul
    (135, 8),   # 立秋 -> ~Agu
    (165, 9),   # 白露 -> ~Sep
    (195, 10),  # 寒露 -> ~Okt
    (225, 11),  # 立冬 -> ~Nov
    (255, 12),  # 大雪 -> ~Des
    (285, 1),   # 小寒 -> ~Jan
]

# Nama-nama 节 untuk ditampilkan
JIE_NAMES = ["立春", "惊蛰", "清明", "立夏", "芒种", "小暑",
             "立秋", "白露", "寒露", "立冬", "大雪", "小寒"]

# Nama-nama 气 (untuk informasi)
QI_NAMES = ["雨水", "春分", "谷雨", "小满", "夏至", "大暑",
            "处暑", "秋分", "霜降", "小雪", "冬至", "大寒"]

# Daftar kota Indonesia: nama -> (bujur timur, zona UTC)
CITIES = {
    "semarang": (110.42, 7), "jakarta": (106.85, 7), "surabaya": (112.75, 7),
    "bandung": (107.62, 7), "medan": (98.67, 7), "yogyakarta": (110.37, 7),
    "solo": (110.83, 7), "malang": (112.63, 7), "palembang": (104.75, 7),
    "pekanbaru": (101.45, 7), "padang": (100.35, 7), "bandar lampung": (105.26, 7),
    "pontianak": (109.33, 7), "banjarmasin": (114.59, 8), "samarinda": (117.15, 8),
    "balikpapan": (116.83, 8), "makassar": (119.42, 8), "kendari": (122.51, 8),
    "denpasar": (115.22, 8), "kupang": (123.58, 8), "manado": (124.84, 8),
    "ternate": (127.38, 9), "ambon": (128.18, 9), "jayapura": (140.72, 9),
    "sorong": (131.29, 9), "merauke": (140.40, 9), "banda aceh": (95.32, 7),
    "cirebon": (108.55, 7), "tegal": (109.14, 7), "pekalongan": (109.67, 7),
    "surakarta": (110.83, 7), "kediri": (112.02, 7), "bogor": (106.79, 7),
    "depok": (106.82, 7), "tangerang": (106.63, 7), "bekasi": (106.99, 7),
    "jambi": (103.61, 7), "bengkulu": (102.27, 7), "palu": (119.87, 8),
    "gorontalo": (123.06, 8), "mamuju": (118.89, 8), "tarakan": (117.58, 8),
    "batam": (104.03, 7), "tanjung pinang": (104.46, 7), "pangkal pinang": (106.11, 7),
    "bukittinggi": (100.37, 7), "purwokerto": (109.42, 7), "madiun": (111.52, 7),
    "probolinggo": (113.22, 7), "jember": (113.70, 7), "banyuwangi": (114.37, 7),
    "denpasar": (115.22, 8), "mataram": (116.12, 8), "bima": (118.72, 8),
}

# ---------------------------------------------------------------------------
# 2. ASTRONOMI & KALENDER
# ---------------------------------------------------------------------------

def jdn_from_ymd(y: int, m: int, d: int) -> int:
    """Julian Day Number (integer, jam 0h) untuk tanggal Masehi proleptik."""
    yy, mm = y, m
    if mm <= 2:
        yy -= 1
        mm += 12
    a = yy // 100
    b = 2 - a + a // 4
    jd = int(365.25 * (yy + 4716)) + int(30.6001 * (mm + 1)) + d + b - 1524
    return jd  # JDN (JD pada tengah malam)


def jd_from_dt(dt: datetime) -> float:
    """Julian Day (pecahan) dari datetime lokal."""
    y, m = dt.year, dt.month
    d = dt.day + (dt.hour + dt.minute / 60.0 + dt.second / 3600.0) / 24.0
    yy, mm = y, m
    if mm <= 2:
        yy -= 1
        mm += 12
    a = yy // 100
    b = 2 - a + a // 4
    return int(365.25 * (yy + 4716)) + int(30.6001 * (mm + 1)) + d + b - 1524.5


def sun_longitude(jd: float) -> float:
    """
    Bujur ekliptika semu matahari (derajat, equinox tanggal) — algoritma Meeus.
    Akurasi ~0.01 derajat (cukup untuk 节气: kesalahan < ~15 menit waktu).
    """
    t = (jd - 2451545.0) / 36525.0
    l0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
    m = 357.52911 + 35999.05029 * t - 0.0001537 * t * t
    e = 0.016708634 - 0.000042037 * t - 0.0000001267 * t * t
    c = ((1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(math.radians(m))
         + (0.019993 - 0.000101 * t) * math.sin(math.radians(2 * m))
         + 0.000289 * math.sin(math.radians(3 * m)))
    true_long = l0 + c
    omega = 125.04 - 1934.136 * t
    return (true_long - 0.00569 - 0.00478 * math.sin(math.radians(omega))) % 360.0


def _crossed(jd: float, target: float) -> bool:
    """True jika matahari sudah melewati bujur target."""
    return ((sun_longitude(jd) - target) % 360.0) < 180.0


def find_jie_time(year: int, angle: float, approx_month: int) -> datetime:
    """
    Cari waktu persis matahari melintasi bujur `angle` (salah satu 节) pada
    tahun Masehi `year`, dengan pencarian biner hingga presisi ~1 menit.
    """
    start = datetime(year, approx_month, 1) - timedelta(days=2)
    if approx_month == 12:
        end = datetime(year + 1, 1, 1) + timedelta(days=2)
    else:
        end = datetime(year, approx_month + 1, 1) + timedelta(days=2)

    lo = jd_from_dt(start)
    hi = jd_from_dt(end)
    # Pastikan invarianta: lo belum lewat, hi sudah lewat
    guard = 0
    while _crossed(lo, angle) and guard < 400:
        lo -= 1.0
        guard += 1
    guard = 0
    while not _crossed(hi, angle) and guard < 400:
        hi += 1.0
        guard += 1
    for _ in range(40):
        mid = (lo + hi) / 2.0
        if _crossed(mid, angle):
            hi = mid
        else:
            lo = mid
    jd = (lo + hi) / 2.0
    # JDN -> datetime lokal
    return datetime(2000, 1, 1, 12) + timedelta(days=jd - 2451545.0)


_JIE_CACHE: dict = {}


def jie_boundaries(bazi_year: int) -> list:
    """
    12 batas 节 untuk tahun bazi `bazi_year` (tahun yang dimulai dari 立春):
    [立春(BY), 惊蛰(BY), ..., 大雪(BY), 小寒(BY+1)].
    Mengembalikan list (pos_cabang_bulan, datetime).
    pos 0 = 寅月 ... pos 11 = 丑月.
    """
    key = bazi_year
    if key in _JIE_CACHE:
        return _JIE_CACHE[key]
    bounds = []
    for i, (angle, month) in enumerate(JIE):
        y = bazi_year
        if month == 1:      # 小寒 Jan -> untuk posisi 11 dipakai 小寒(BY+1)
            y = bazi_year + 1
        bounds.append((i, find_jie_time(y, angle, month)))
    _JIE_CACHE[key] = bounds
    return bounds


def li_chun(year: int) -> datetime:
    """Waktu 立春 (awal tahun bazi) pada tahun Masehi `year`."""
    return find_jie_time(year, 315, 2)


def equation_of_time_minutes(dt: datetime) -> float:
    """Equation of time dalam menit (Meeus, aproksimasi akurasi ~30 detik)."""
    jd = jd_from_dt(dt)
    t = (jd - 2451545.0) / 36525.0
    l0 = math.radians(280.46646 + 36000.76983 * t + 0.0003032 * t * t)
    m = math.radians(357.52911 + 35999.05029 * t - 0.0001537 * t * t)
    e = 0.016708634 - 0.000042037 * t - 0.0000001267 * t * t
    eps = 23.43929111 - 0.0130042 * t - 1.64e-7 * t * t + 5.04e-7 * t * t * t
    y = math.tan(math.radians(eps / 2.0)) ** 2
    eot = 4.0 * (y * math.sin(2 * l0) - 2 * e * math.sin(m)
                 + 4 * e * y * math.sin(m) * math.cos(2 * l0)
                 - 0.5 * y * y * math.sin(4 * l0)
                 - 1.25 * e * e * math.sin(2 * m))
    return eot


def true_solar_time(dt: datetime, longitude: float, tz_hours: float = 7.0) -> datetime:
    """
    Koreksi waktu standar -> waktu matahari sejati (真太阳时):
      koreksi = (bujur - meridian_zona) * 4 menit + equation_of_time
    """
    meridian = tz_hours * 15.0
    delta_min = (longitude - meridian) * 4.0 + equation_of_time_minutes(dt)
    return dt + timedelta(minutes=delta_min)


# ---------------------------------------------------------------------------
# 3. GANZHI (batang & cabang)
# ---------------------------------------------------------------------------

def year_ganzhi(bazi_year: int) -> tuple:
    """(indeks batang, indeks cabang) untuk tahun bazi `bazi_year`."""
    return ((bazi_year - 4) % 10, (bazi_year - 4) % 12)


def month_stem_index(year_stem_idx: int, month_pos: int) -> int:
    """五虎遁: batang bulan dari batang tahun. month_pos: 0=寅 ... 11=丑."""
    return (2 * year_stem_idx + 2 + month_pos) % 10


def day_ganzhi(dt: datetime) -> tuple:
    """(indeks batang, indeks cabang) pilar hari. Pergantian hari jam 23:00."""
    d = dt.date()
    if dt.hour >= 23:
        d += timedelta(days=1)
    idx = (jdn_from_ymd(d.year, d.month, d.day) + 49) % 60
    return (idx % 10, idx % 12)


def hour_branch_index(hour: int, minute: int = 0) -> int:
    """Cabang jam: 子(23-00:59), 丑(01-02:59), ... 亥(21-22:59)."""
    h = hour
    if h == 23:
        return 0
    return ((h + 1) // 2) % 12


def hour_stem_index(day_stem_idx: int, hour_branch_idx: int) -> int:
    """五鼠遁: batang jam dari batang hari."""
    return (2 * day_stem_idx + hour_branch_idx) % 10


def ganzhi_from_index(idx: int) -> str:
    return STEMS[idx % 10] + BRANCHES[idx % 12]


def cycle_index(stem_idx: int, branch_idx: int) -> int:
    """Indeks 0..59 dari pasangan batang-cabang."""
    for i in range(60):
        if i % 10 == stem_idx and i % 12 == branch_idx:
            return i
    raise ValueError("pasangan gan-zhi tidak valid")


# ---------------------------------------------------------------------------
# 4. TEN GODS (十神), NAYIN, SHEN SHA
# ---------------------------------------------------------------------------

def ten_god(day_stem: str, other_stem: str) -> str:
    """十神 dari `other_stem` relatif terhadap `day_stem` (Hari Utama)."""
    dm_e = STEM_ELEMENT[day_stem]
    o_e = STEM_ELEMENT[other_stem]
    same_pol = (STEMS.index(day_stem) % 2) == (STEMS.index(other_stem) % 2)

    if o_e == dm_e:
        return "比肩" if same_pol else "劫财"
    if GENERATES[dm_e] == o_e:
        return "食神" if same_pol else "伤官"
    if CONTROLS[dm_e] == o_e:
        return "偏财" if same_pol else "正财"
    if CONTROLS[o_e] == dm_e:
        return "七杀" if same_pol else "正官"
    if GENERATES[o_e] == dm_e:
        return "偏印" if same_pol else "正印"
    raise ValueError("hubungan unsur tidak dikenal")


def na_yin(cycle_idx: int) -> str:
    return NAYIN[cycle_idx // 2]


# --- Peta aturan 神煞 ---

TIANYI = {  # 天乙贵人 (berdasarkan batang hari)
    "甲": ["丑", "未"], "戊": ["丑", "未"], "庚": ["丑", "未"],
    "乙": ["子", "申"], "己": ["子", "申"],
    "丙": ["亥", "酉"], "丁": ["亥", "酉"],
    "壬": ["卯", "巳"], "癸": ["卯", "巳"],
    "辛": ["寅", "午"],
}

WENCHANG = {  # 文昌 (berdasarkan batang hari)
    "甲": "巳", "乙": "午", "丙": "申", "丁": "酉", "戊": "申",
    "己": "酉", "庚": "亥", "辛": "子", "壬": "寅", "癸": "卯",
}

LUSHEN = {  # 禄神 (berdasarkan batang hari)
    "甲": "寅", "乙": "卯", "丙": "巳", "丁": "午", "戊": "巳",
    "己": "午", "庚": "申", "辛": "酉", "壬": "亥", "癸": "子",
}

YANGREN = {  # 羊刃 (berdasarkan batang hari)
    "甲": "卯", "乙": "辰", "丙": "午", "丁": "未", "戊": "午",
    "己": "未", "庚": "酉", "辛": "戌", "壬": "子", "癸": "丑",
}

_SANHE_GROUP = {"申": "申子辰", "子": "申子辰", "辰": "申子辰",
                "亥": "亥卯未", "卯": "亥卯未", "未": "亥卯未",
                "寅": "寅午戌", "午": "寅午戌", "戌": "寅午戌",
                "巳": "巳酉丑", "酉": "巳酉丑", "丑": "巳酉丑"}

TAOHUA = {"申子辰": "酉", "寅午戌": "卯", "巳酉丑": "午", "亥卯未": "子"}
YIMA = {"申子辰": "寅", "寅午戌": "申", "巳酉丑": "亥", "亥卯未": "巳"}
HUAGAI = {"申子辰": "辰", "寅午戌": "戌", "巳酉丑": "丑", "亥卯未": "未"}
JIANGXING = {"申子辰": "子", "寅午戌": "午", "巳酉丑": "酉", "亥卯未": "卯"}


def shen_sha_for_branch(day_stem: str, year_branch: str, day_branch: str,
                        branch: str) -> list:
    """Daftar 神煞 yang terdapat pada sebuah cabang."""
    out = []
    if branch in TIANYI.get(day_stem, []):
        out.append("天乙贵人")
    if WENCHANG.get(day_stem) == branch:
        out.append("文昌贵人")
    if LUSHEN.get(day_stem) == branch:
        out.append("禄神")
    if YANGREN.get(day_stem) == branch:
        out.append("羊刃")

    for base in (year_branch, day_branch):
        g = _SANHE_GROUP.get(base)
        if g:
            if TAOHUA[g] == branch and "桃花" not in out:
                out.append("桃花")
            if YIMA[g] == branch and "驿马" not in out:
                out.append("驿马")
            if HUAGAI[g] == branch and "华盖" not in out:
                out.append("华盖")
            if JIANGXING[g] == branch and "将星" not in out:
                out.append("将星")
    return out


# ---------------------------------------------------------------------------
# 5. STRUKTUR DATA
# ---------------------------------------------------------------------------

@dataclass
class Pillar:
    name: str                 # Tahun / Bulan / Hari / Jam
    stem: str
    branch: str
    stem_idx: int
    branch_idx: int
    cycle_idx: int
    hidden: list              # [(batang, unsur, shishen, bobot), ...]
    ten_god_stem: str         # 十神 batang terhadap Hari Utama
    ten_god_branch: str       # 十神 qi utama cabang terhadap Hari Utama
    na_yin: str
    shen_sha: list = field(default_factory=list)
    kong: bool = False        # cabang ini kena 空亡 (mengacu pilar hari)

    @property
    def stem_element(self) -> str:
        return STEM_ELEMENT[self.stem]

    @property
    def branch_element(self) -> str:
        return BRANCH_ELEMENT[self.branch]

    @property
    def stem_polarity(self) -> str:
        return polarity(self.stem)


@dataclass
class DaYun:
    index: int
    gan_zhi: str
    stem: str
    branch: str
    start_age: int
    end_age: int
    start_year: int
    end_year: int
    start_date: datetime
    stem_element: str
    branch_element: str
    ten_god_stem: str
    ten_god_branch: str
    favorable: bool          # fase ini selaras dengan unsur keberuntungan?
    score: int = 0
    grade: str = ""


@dataclass
class LiuNian:
    year: int
    phase: str               # "utama" / "awal (sebelum 立春)"
    gan_zhi: str
    stem: str
    branch: str
    stem_element: str
    branch_element: str
    ten_god_stem: str
    ten_god_branch: str
    age: int
    score: int
    grade: str
    flags: list = field(default_factory=list)


@dataclass
class LiuYue:
    name: str                # nama bulan (mis. "Feb 2026")
    month_pos: int
    gan_zhi: str
    stem: str
    branch: str
    stem_element: str
    branch_element: str
    ten_god_stem: str
    score: int
    grade: str
    jie_name: str            # 节 pembuka bulan ini


@dataclass
class Chart:
    birth: datetime
    true_solar: datetime
    gender: str              # "pria" / "wanita"
    city: str = ""
    longitude: float | None = None
    tz: float = 7.0

    year_pillar: Pillar = None
    month_pillar: Pillar = None
    day_pillar: Pillar = None
    hour_pillar: Pillar = None

    bazi_year: int = 0
    element_score: dict = field(default_factory=dict)   # skor tiap unsur
    element_raw: dict = field(default_factory=dict)     # jumlah karakter
    element_detail: dict = field(default_factory=dict)  # rincian per posisi
    dm: str = ""
    dm_element: str = ""
    strength: dict = field(default_factory=dict)
    favorable: list = field(default_factory=list)       # 喜用 (urut prioritas)
    unfavorable: list = field(default_factory=list)     # 忌
    ten_god_counts: dict = field(default_factory=dict)
    kong_wang: list = field(default_factory=list)
    tai_yuan: tuple = ()        # (batang, cabang)
    ming_gong: tuple = ()       # (batang, cabang)
    shen_sha_by_branch: dict = field(default_factory=dict)

    @property
    def pillars(self) -> list:
        return [self.year_pillar, self.month_pillar, self.day_pillar, self.hour_pillar]

    @property
    def ganzhi(self) -> str:
        return "".join(p.stem + p.branch for p in self.pillars)


# ---------------------------------------------------------------------------
# 6. PEMBENTUKAN PILAR (PAIPAN)
# ---------------------------------------------------------------------------

def build_chart(birth: datetime, gender: str,
                city: str = "", longitude: float | None = None,
                tz_hours: float = 7.0,
                apply_true_solar: bool = False) -> Chart:
    """
    Susun bagan Bazi lengkap dari tanggal & jam lahir Masehi.
    - `birth`: waktu standar lokal (datetime naive)
    - `gender`: "pria" / "wanita" (untuk arah 大运)
    - `city` / `longitude` + `tz_hours`: koreksi waktu matahari sejati
    """
    if gender not in ("pria", "wanita"):
        raise ValueError("gender harus 'pria' atau 'wanita'")
    if not (1800 <= birth.year <= 2200):
        raise ValueError("rentang tahun didukung: 1800-2200")

    # --- waktu matahari sejati ---
    if apply_true_solar and (longitude is not None or city):
        lon = longitude if longitude is not None else CITIES[city][0]
        tz = tz_hours if longitude is not None else float(CITIES[city][1])
        true_dt = true_solar_time(birth, lon, tz)
    else:
        lon = longitude
        tz = tz_hours
        true_dt = birth

    chart = Chart(birth=birth, true_solar=true_dt, gender=gender,
                  city=city, longitude=lon, tz=tz)

    # --- tahun bazi (batas 立春) ---
    lc = li_chun(true_dt.year)
    bazi_year = true_dt.year if true_dt >= lc else true_dt.year - 1
    chart.bazi_year = bazi_year
    ys, yb = year_ganzhi(bazi_year)

    # --- bulan bazi (batas 12 节) ---
    # Pilar bulan = bulan yang sedang berjalan, yaitu bulan yang dimulai pada
    # 节 TERAKHIR yang sudah lewat (atau tepat) sebelum waktu lahir.
    bounds = jie_boundaries(bazi_year)
    month_pos = 0  # default: 寅月 (mulai 立春)
    for i, (pos, btime) in enumerate(bounds):
        if btime <= true_dt:
            month_pos = i
    ms = month_stem_index(ys, month_pos)
    mb = (2 + month_pos) % 12  # 寅=2, 卯=3, ..., 丑=1

    # --- hari bazi (batas jam 23:00) ---
    ds, db = day_ganzhi(true_dt)

    # --- jam bazi ---
    hb = hour_branch_index(true_dt.hour, true_dt.minute)
    hs = hour_stem_index(ds, hb)

    dm = STEMS[ds]
    dm_e = STEM_ELEMENT[dm]

    def make_pillar(name, si, bi, is_day=False):
        branch = BRANCHES[bi]
        hid = []
        for k, hstem in enumerate(HIDDEN[branch]):
            w = HIDDEN_WEIGHTS[k] if k < len(HIDDEN_WEIGHTS) else 0.1
            hid.append((hstem, STEM_ELEMENT[hstem], ten_god(dm, hstem), w))
        p = Pillar(
            name=name, stem=STEMS[si], branch=branch,
            stem_idx=si, branch_idx=bi, cycle_idx=cycle_index(si, bi),
            hidden=hid,
            ten_god_stem=ten_god(dm, STEMS[si]),
            ten_god_branch=ten_god(dm, HIDDEN[branch][0]),
            na_yin=na_yin(cycle_index(si, bi)),
        )
        return p

    chart.year_pillar = make_pillar("Tahun", ys, yb)
    chart.month_pillar = make_pillar("Bulan", ms, mb)
    chart.day_pillar = make_pillar("Hari", ds, db, is_day=True)
    chart.hour_pillar = make_pillar("Jam", hs, hb)
    chart.dm = dm
    chart.dm_element = dm_e

    # --- 空亡 (dari 旬 pilar hari) ---
    day_idx = chart.day_pillar.cycle_idx
    xun_start = day_idx - (day_idx % 10)
    void_branches = [BRANCHES[(xun_start + 10) % 12], BRANCHES[(xun_start + 11) % 12]]
    chart.kong_wang = void_branches
    for p in chart.pillars:
        if p.branch in void_branches:
            p.kong = True

    # --- 神煞 per cabang ---
    for p in chart.pillars:
        p.shen_sha = shen_sha_for_branch(dm, chart.year_pillar.branch,
                                         chart.day_pillar.branch, p.branch)
        chart.shen_sha_by_branch.setdefault(p.branch, [])
        for s in p.shen_sha:
            if s not in chart.shen_sha_by_branch[p.branch]:
                chart.shen_sha_by_branch[p.branch].append(s)

    # --- 胎元 & 命宫 ---
    mp = chart.month_pillar
    chart.tai_yuan = (STEMS[(mp.stem_idx + 1) % 10], BRANCHES[(mp.branch_idx + 3) % 12])
    m_idx = mp.branch_idx + 1   # 子=1 ... 亥=12
    h_idx = chart.hour_pillar.branch_idx + 1
    ming = 14 - (m_idx + h_idx)
    while ming < 1:
        ming += 12
    while ming > 12:
        ming -= 12
    ming_pos = (ming - 2) % 12          # posisi relatif 寅=0
    ming_stem = (2 * ys + 2 + ming_pos) % 10
    chart.ming_gong = (STEMS[ming_stem], BRANCHES[ming - 1])

    # --- hitung unsur 五行 ---
    element_score = {e: 0.0 for e in GENERATES}
    element_raw = {e: 0 for e in GENERATES}
    element_detail = {}
    for p in chart.pillars:
        detail = {}
        # batang: bobot 1.0
        el = p.stem_element
        element_score[el] += 1.0
        element_raw[el] += 1
        detail["batang:" + p.stem] = (el, 1.0)
        # cabang: qi tersembunyi berbobot
        for hstem, hel, hten, w in p.hidden:
            element_score[hel] += w
            element_raw[hel] += 1
            detail[f"cabang:{p.branch}({hstem})"] = (hel, w)
        element_detail[p.name] = detail
    # bonus bulan (月令): qi utama cabang bulan +1.2
    month_main = BRANCH_ELEMENT[chart.month_pillar.branch]
    element_score[month_main] += 1.2
    chart.element_score = element_score
    chart.element_raw = element_raw
    chart.element_detail = element_detail

    # --- hitung kekuatan Hari Utama ---
    total = sum(element_score.values())
    dm_share = element_score[dm_e] / total if total else 0.0

    # 得令: lahir di musim unsur sendiri / musim yang menopangnya
    season = BRANCH_ELEMENT[chart.month_pillar.branch]
    de_ling = 0
    if season == dm_e:
        de_ling = 2
    elif GENERATES[season] == dm_e:
        de_ling = 1
    # 得地: akar di cabang (keberadaan unsur Hari Utama di cabang)
    root_score = 0.0
    for p in chart.pillars:
        for hstem, hel, hten, w in p.hidden:
            if hel == dm_e:
                root_score += w
    # 得势/得助: dukungan sesama unsur & unsur yang melahirkan
    support = 0.0
    for p in chart.pillars:
        if STEM_ELEMENT[p.stem] == dm_e or GENERATES[STEM_ELEMENT[p.stem]] == dm_e:
            support += 1.0
        for hstem, hel, hten, w in p.hidden:
            if hel == dm_e or GENERATES[hel] == dm_e:
                support += w

    share_pct = dm_share * 100
    if de_ling == 2 and share_pct >= 26:
        verdict = "KUAT"
    elif de_ling >= 1 and share_pct >= 30:
        verdict = "KUAT"
    elif share_pct >= 32:
        verdict = "KUAT"
    elif share_pct <= 18:
        verdict = "LEMAH"
    else:
        verdict = "SEIMBANG"

    chart.strength = {
        "share": share_pct, "total": total,
        "de_ling": de_ling, "season": season,
        "root_score": root_score, "support": support,
        "verdict": verdict,
    }

    # --- 喜用神 / 忌神 (metode 扶抑) ---
    all_el = list(GENERATES.keys())
    if verdict == "KUAT":
        # Hari Utama kuat → butuh penyalur: 克我(官杀), 我生(食伤), 我克(财).
        # Pilih yang paling LEMAH di bagan (paling dibutuhkan).
        ke_wo = element_that_controls(dm_e)   # unsur yang menguasai Hari Utama
        wo_sheng = GENERATES[dm_e]            # yang dilahirkan Hari Utama
        wo_ke = CONTROLS[dm_e]                # yang dikuasai Hari Utama
        cands = sorted(set([ke_wo, wo_sheng, wo_ke]), key=lambda e: element_score[e])
        chart.favorable = cands
        # Penghambat: sesama unsur (比劫) & pelahir (印) yang paling kuat.
        yin = element_that_generates(dm_e)
        ji = [dm_e, yin]
        chart.unfavorable = sorted(ji, key=lambda e: -element_score[e])
    elif verdict == "LEMAH":
        # Hari Utama lemah → butuh penopang: 生我(印), 同我(比劫).
        cands = sorted(set([element_that_generates(dm_e), dm_e]),
                       key=lambda e: element_score[e])
        chart.favorable = cands
        # Penghambat: yang menyerang/menguras Hari Utama.
        ke_wo = element_that_controls(dm_e)
        wo_ke = CONTROLS[dm_e]
        wo_sheng = GENERATES[dm_e]
        ji = [ke_wo, wo_ke, wo_sheng]
        chart.unfavorable = sorted(ji, key=lambda e: -element_score[e])
    else:  # SEIMBANG: unsur paling lemah = pendukung, paling kuat = penghambat
        ranked = sorted(all_el, key=lambda e: element_score[e])
        chart.favorable = ranked[:2]
        chart.unfavorable = ranked[-2:][::-1]

    # --- hitung 十神 (kemunculan) ---
    counts = {}
    for p in chart.pillars:
        counts[p.ten_god_stem] = counts.get(p.ten_god_stem, 0) + 1
        for hstem, hel, hten, w in p.hidden:
            counts[hten] = counts.get(hten, 0) + w
    chart.ten_god_counts = counts

    return chart


# ---------------------------------------------------------------------------
# 7. 大运 (DA YUN)
# ---------------------------------------------------------------------------

def add_months(dt: datetime, months: int) -> datetime:
    y = dt.year + (dt.month - 1 + months) // 12
    m = (dt.month - 1 + months) % 12 + 1
    day = min(dt.day, [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28,
                       31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return datetime(y, m, day, dt.hour, dt.minute, dt.second)


def compute_da_yun(chart: Chart, count: int = 10) -> list:
    """
    Hitung pilar-pilar 大运.

    Arah: tahun Yang (batang 甲丙戊庚壬) + pria -> maju;  tahun Yang + wanita -> mundur;
          tahun Yin + pria -> mundur;  tahun Yin + wanita -> maju.
    Usia mulai: jarak kelahiran ke 节 terdekat (maju: 节 berikutnya; mundur: 节
    sebelumnya), dengan konversi 3 hari = 1 tahun (1 hari = 4 bulan, 1 jam = 5 hari).
    """
    year_stem_idx = chart.year_pillar.stem_idx
    yang_year = year_stem_idx % 2 == 0
    forward = (yang_year and chart.gender == "pria") or (not yang_year and chart.gender == "wanita")

    birth = chart.true_solar
    bounds = jie_boundaries(chart.bazi_year)
    # batas 立春 tahun berikutnya juga relevan utk bulan terakhir (丑月)
    next_lc = li_chun(chart.bazi_year + 1)
    all_bounds = [t for _, t in bounds] + [next_lc]

    if forward:
        target = next((t for t in all_bounds if t > birth), None)
        if target is None:
            target = li_chun(chart.bazi_year + 2)
        hours = (target - birth).total_seconds() / 3600.0
    else:
        prev = [t for t in all_bounds if t < birth]
        target = prev[-1] if prev else li_chun(chart.bazi_year)
        hours = (birth - target).total_seconds() / 3600.0

    total_months = hours / 6.0          # 1 bulan = 6 jam
    start_years = int(total_months // 12)
    start_months = int(total_months % 12)
    start_date = add_months(birth, start_years * 12 + start_months)

    month_cycle = chart.month_pillar.cycle_idx
    step = 1 if forward else -1

    dys = []
    for i in range(count):
        idx = (month_cycle + step * (i + 1)) % 60
        stem = STEMS[idx % 10]
        branch = BRANCHES[idx % 12]
        sy = start_date.year + i * 10
        ey = sy + 9
        sa = start_years + i * 10
        ea = sa + 9
        sdate = add_months(start_date, i * 120)
        fav = (STEM_ELEMENT[stem] in chart.favorable
               or BRANCH_ELEMENT[branch] in chart.favorable)
        dys.append(DaYun(
            index=i + 1, gan_zhi=stem + branch, stem=stem, branch=branch,
            start_age=sa, end_age=ea, start_year=sy, end_year=ey,
            start_date=sdate,
            stem_element=STEM_ELEMENT[stem], branch_element=BRANCH_ELEMENT[branch],
            ten_god_stem=ten_god(chart.dm, stem),
            ten_god_branch=ten_god(chart.dm, HIDDEN[branch][0]),
            favorable=fav,
        ))
    return dys


# ---------------------------------------------------------------------------
# 8. 流年 (LIU NIAN) & 流月 (LIU YUE)
# ---------------------------------------------------------------------------

TEN_GOD_YEAR_BASE = {
    "正印": 10, "偏印": 2, "食神": 10, "伤官": 0, "正财": 8,
    "偏财": 6, "比肩": 2, "劫财": -6, "正官": 6, "七杀": -8,
}


def _grade(score: int) -> str:
    if score >= 85:
        return "SANGAT BAIK"
    if score >= 70:
        return "BAIK"
    if score >= 60:
        return "CUKUP"
    if score >= 45:
        return "NETRAL"
    if score >= 30:
        return "KURANG"
    return "HATI-HATI"


def _interact(a: str, b: str) -> list:
    """Bentuk interaksi antar cabang: 冲/合/刑/害."""
    flags = []
    if LIUCHONG.get(a) == b:
        flags.append("冲")
    if LIUHE.get(a) == b:
        flags.append("合")
    g = _SANHE_GROUP.get(a)
    if g and b in SANHE[a][1]:
        flags.append("三合")
    # 三刑: pasangan BEDA dalam satu grup (寅巳申 / 丑戌未 / 子卯);
    # 自刑: cabang sama yang termasuk {辰,午,酉,亥}.
    # CATATAN: harus subset-check, BUKAN kesetaraan set — pasangan 2 elemen
    # tidak akan pernah sama dengan grup 3 elemen ({寅,巳,申} dll), sehingga
    # bug lama `{a,b} in [set(x) ...]` hanya menangkap 子卯. (fix 2026-08-20)
    if (a in ZIXING and a == b) or (a != b and any({a, b} <= set(x) for x in XING_GROUPS)):
        flags.append("刑")
    if LIUHAI.get(a) == b:
        flags.append("害")
    return flags


def score_liu_nian(chart: Chart, year: int, da_yun_list: list, da_yun_idx: int = -1) -> LiuNian:
    """Skor & evaluasi sebuah 流年 terhadap bagan + 大运 yang sedang berjalan."""
    idx = (year - 4) % 60
    stem = STEMS[idx % 10]
    branch = BRANCHES[idx % 12]
    age = year - chart.birth.year

    score = 50
    flags = []

    # 1) keselarasan unsur dengan 喜用/忌
    fav_el = [e for e in chart.favorable if e == STEM_ELEMENT[stem] or e == BRANCH_ELEMENT[branch]]
    unf_el = [e for e in chart.unfavorable if e == STEM_ELEMENT[stem] or e == BRANCH_ELEMENT[branch]]
    if fav_el:
        score += 12
    if unf_el:
        score -= 12

    # 2) 十神 batang & cabang
    tg_s = ten_god(chart.dm, stem)
    tg_b = ten_god(chart.dm, HIDDEN[branch][0])
    score += TEN_GOD_YEAR_BASE.get(tg_s, 0)
    score += TEN_GOD_YEAR_BASE.get(tg_b, 0) // 2

    # 3) interaksi dengan pilar bagan & 大运
    day_b = chart.day_pillar.branch
    year_b = chart.year_pillar.branch
    dy_branch = None
    if 0 <= da_yun_idx < len(da_yun_list):
        dy_branch = da_yun_list[da_yun_idx].branch

    for target, weight, label in [(day_b, 15, "pilar hari"), (year_b, 8, "pilar tahun")]:
        fl = _interact(branch, target)
        if "冲" in fl:
            score -= weight
            flags.append(f"冲 {label} ({branch} vs {target})")
        if "刑" in fl:
            score -= 6
            flags.append(f"刑 {label}")
        if "害" in fl:
            score -= 5
            flags.append(f"害 {label}")
        if "合" in fl or "三合" in fl:
            score += 8
            flags.append(f"合 {label}")

    if dy_branch:
        fl = _interact(branch, dy_branch)
        if "冲" in fl:
            score -= 5
            flags.append(f"冲 大运 ({branch} vs {dy_branch})")
        if "合" in fl or "三合" in fl:
            score += 4

    # 4) 桃花 aktif
    g = _SANHE_GROUP.get(year_b)
    if g and TAOHUA[g] == branch:
        score += 5
        flags.append("桃花 aktif")
    gd = _SANHE_GROUP.get(day_b)
    if gd and TAOHUA[gd] == branch and "桃花 aktif" not in flags:
        score += 3
        flags.append("桃花 aktif")

    # 5) 空亡
    if branch in chart.kong_wang:
        score -= 5
        flags.append("kena 空亡")

    # 6) bonus kekuatan Hari Utama
    if chart.strength["verdict"] == "KUAT" and STEM_ELEMENT[stem] in chart.favorable:
        score += 3

    score = max(5, min(98, score))
    return LiuNian(
        year=year, phase="utama", gan_zhi=stem + branch, stem=stem, branch=branch,
        stem_element=STEM_ELEMENT[stem], branch_element=BRANCH_ELEMENT[branch],
        ten_god_stem=tg_s, ten_god_branch=tg_b, age=age,
        score=score, grade=_grade(score), flags=flags,
    )


def active_da_yun_index(da_yun_list: list, year: int) -> int:
    """Indeks 大运 yang sedang berjalan pada tahun tertentu (-1 jika belum mulai)."""
    for i, dy in enumerate(da_yun_list):
        if dy.start_year <= year <= dy.end_year:
            return i
    if year < da_yun_list[0].start_year:
        return -1
    return len(da_yun_list) - 1


def compute_liu_nian_range(chart: Chart, year_from: int, year_to: int,
                           da_yun_list: list) -> list:
    """Daftar 流年 untuk rentang tahun (dengan catatan fase sebelum 立春)."""
    out = []
    for y in range(year_from, year_to + 1):
        dyi = active_da_yun_index(da_yun_list, y)
        out.append(score_liu_nian(chart, y, da_yun_list, dyi))
    return out


def compute_liu_yue(chart: Chart, year: int) -> list:
    """
    Peruntungan 12 bulan bazi (流月) mulai dari 立春 tahun `year`.
    Setiap bulan dimulai pada salah satu 12 节.
    """
    bazi_year = year
    lc = li_chun(year)
    if lc > datetime(year, 1, 1):
        # bulan-bulan sebelum 立春 masih 流年 tahun sebelumnya; kita mulai dari 立春
        pass
    ys, _ = year_ganzhi(bazi_year)
    bounds = jie_boundaries(bazi_year)
    months = []
    for pos, (mp, btime) in enumerate(bounds):
        ms = month_stem_index(ys, mp)
        mb = (2 + mp) % 12
        stem = STEMS[ms]
        branch = BRANCHES[mb]
        gmonth = btime.month
        gname = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
                 "Jul", "Agu", "Sep", "Okt", "Nov", "Des"][gmonth - 1]
        # skor sederhana: unsur + 十神 + interaksi dengan pilar hari
        score = 50
        if STEM_ELEMENT[stem] in chart.favorable or BRANCH_ELEMENT[branch] in chart.favorable:
            score += 8
        if STEM_ELEMENT[stem] in chart.unfavorable or BRANCH_ELEMENT[branch] in chart.unfavorable:
            score -= 8
        score += TEN_GOD_YEAR_BASE.get(ten_god(chart.dm, stem), 0) // 2
        fl = _interact(branch, chart.day_pillar.branch)
        if "冲" in fl:
            score -= 10
        if "合" in fl or "三合" in fl:
            score += 6
        score = max(5, min(98, score))
        months.append(LiuYue(
            name=f"{gname} {btime.year}", month_pos=mp, gan_zhi=stem + branch,
            stem=stem, branch=branch,
            stem_element=STEM_ELEMENT[stem], branch_element=BRANCH_ELEMENT[branch],
            ten_god_stem=ten_god(chart.dm, stem),
            score=score, grade=_grade(score),
            jie_name=JIE_NAMES[mp],
        ))
    return months


# ---------------------------------------------------------------------------
# 9. UTILITAS TAMPILAN
# ---------------------------------------------------------------------------

ELEMENT_COLOR = {"木": "hijau", "火": "merah/oranye", "土": "kuning/cokelat",
                 "金": "putih/perak/emas", "水": "hitam/biru"}
ELEMENT_NUMBER = {"木": "3, 8", "火": "2, 7", "土": "5, 10", "金": "4, 9", "水": "1, 6"}
ELEMENT_DIRECTION = {"木": "Timur", "火": "Selatan", "土": "Tengah",
                     "金": "Barat", "水": "Utara"}
ELEMENT_BODY = {"木": "hati, mata, otot, tendon", "火": "jantung, usus halus, darah",
                "土": "lambung, limpa, otot perut", "金": "paru-paru, kulit, usus besar",
                "水": "ginjal, kandung kemih, telinga, tulang"}


def element_lucky(el: str) -> dict:
    return {
        "color": ELEMENT_COLOR[el], "number": ELEMENT_NUMBER[el],
        "direction": ELEMENT_DIRECTION[el], "body": ELEMENT_BODY[el],
    }
