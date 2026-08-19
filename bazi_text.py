# -*- coding: utf-8 -*-
"""
bazi_text.py — Lapisan interpretasi & laporan Bahasa Indonesia.

Mengubah hasil hitungan bazi_core.py menjadi laporan yang mudah dipahami:
kepribadian, analisis unsur, kekuatan Hari Utama, unsur keberuntungan,
fase 大运, peruntungan tahunan (流年), dan peruntungan bulanan (流月) —
semua dalam bahasa sehari-hari.
"""

from __future__ import annotations

import unicodedata

from bazi_core import (Chart, DaYun, LiuNian, LiuYue, GENERATES, CONTROLS,
                       STEM_ELEMENT, BRANCH_ELEMENT, BRANCHES, element_lucky,
                       JIE_NAMES, CITIES)

# ---------------------------------------------------------------------------
# KAMUS BAHASA SEHARI-HARI
# ---------------------------------------------------------------------------

SHIO = ["Tikus", "Kerbau", "Harimau", "Kelinci", "Naga", "Ular",
        "Kuda", "Kambing", "Monyet", "Ayam", "Anjing", "Babi"]

ELEMENT_NAME = {"木": "Kayu", "火": "Api", "土": "Tanah", "金": "Logam", "水": "Air"}

# --- Kepribadian berdasarkan unsur Hari Utama (日主) ---
ELEMENT_PERSONALITY = {
    "木": ("Pribadi yang terus bertumbuh — idealis, berprinsip, suka membangun, "
          "berorganisasi, dan mengembangkan orang lain. Kelemahan: keras kepala, "
          "sulit berkompromi saat sudah berpegang pada prinsip."),
    "火": ("Pribadi hangat dan bercahaya — karismatik, ekspresif, cepat bertindak, "
          "mampu menginspirasi orang di sekitarnya. Kelemahan: mudah terbakar emosi, "
          "tidak sabar, dan cenderung terburu-buru."),
    "土": ("Pribadi kokoh seperti tanah — stabil, dapat dipercaya, setia, praktis, "
          "dan selalu menepati janji. Kelemahan: kaku, lambat berubah, dan kadang "
          "terlalu banyak khawatir."),
    "金": ("Pribadi tegas seperti logam — disiplin, analitis, perfeksionis, dan "
          "menjunjung keadilan. Kelemahan: kaku, sulit memaafkan, dan terlalu keras "
          "pada diri sendiri."),
    "水": ("Pribadi bijak seperti air — fleksibel, adaptif, komunikatif, penuh ide, "
          "dan mudah bergaul. Kelemahan: overthinking, sulit mengambil keputusan, "
          "dan kadang plin-plan."),
}

# --- Makna 十神 dalam bahasa sehari-hari ---
TEN_GOD_DESC = {
    "比肩": ("Saudara Sejati", "mandiri, pekerja keras, setia kawan; suka bersaing sehat. "
            "Hati-hati: keras kepala dan sulit meminta bantuan."),
    "劫财": ("Saudara Perebut", "energik, berani, suka menolong, tetapi boros. "
            "Waspadai pinjam-meminjam uang dan pengeluaran impulsif."),
    "食神": ("Bintang Makanan", "kreatif, tenang, menikmati hidup; berbakat seni & kuliner. "
            "Rezeki mengalir dari karya dan keahlian."),
    "伤官": ("Bintang Luka", "cerdas, inovatif, ekspresif; berbakat seni/teknologi. "
            "Kurang sabar dengan aturan dan atasan."),
    "偏财": ("Harta Sampingan", "berbakat bisnis, dermawan, kharismatik; rezeki besar "
            "kadang datang tak terduga. Gemar gaya hidup nyaman."),
    "正财": ("Harta Utama", "teliti, hemat, dapat diandalkan; rezeki dari pekerjaan tetap "
            "dan usaha yang tekun. Setia dalam hubungan."),
    "七杀": ("Bintang Penakluk", "ambisius, berani, tahan tekanan; unggul di medan sulit. "
            "Butuh saluran sehat untuk stres (olahraga/hobi)."),
    "正官": ("Bintang Pejabat", "disiplin, bertanggung jawab, menjunjung aturan; "
            "cocok untuk karier formal dan jabatan."),
    "偏印": ("Bintang Sumber Tak Langsung", "intuitif, unik, suka riset dan hal-hal "
            "non-mainstream; kadang suka menyendiri."),
    "正印": ("Bintang Sumber Langsung", "suka belajar, bijaksana, sering dilindungi "
            "nasib baik lewat pendidikan, dokumen, dan figur senior."),
}

# --- Deskripsi 神煞 ---
SHEN_SHA_DESC = {
    "天乙贵人": "penolong agung — sering selamat dari kesulitan dan dibantu orang berpengaruh",
    "文昌贵人": "bintang pelajar — cerdas, sukses di akademik, suka menulis",
    "桃花": "bunga cinta — menarik & karismatik; waspadai godaan dan drama asmara",
    "驿马": "kuda pos — suka bepergian; karier melibatkan mobilitas/perantauan",
    "华盖": "tudung bintang — minat spiritual & seni; kadang merasa kesepian",
    "将星": "bintang jenderal — jiwa kepemimpinan dan wibawa alami",
    "禄神": "bintang rezeki — pencari nafkah ulung, rezeki relatif stabil",
    "羊刃": "mata pedang — pemberani tetapi mudah konflik; jaga diri dari luka/operasi",
}

# --- Tema & ramalan tahunan (流年) per 十神 ---
TEN_GOD_YEAR = {
    "正印": {
        "tema": "tahun belajar, perlindungan, dan dokumen. Banyak hal 'dibereskan' lewat jalur resmi.",
        "karir": "Karier mulus; atasan/senior membuka jalan. Cocok mengambil sertifikasi, pendidikan lanjut, atau pengurusan administrasi penting.",
        "keuangan": "Keuangan stabil; ada rezeki dari sumber tak terduga (hibah, warisan, tunjangan). Hindari pinjam-meminjam besar.",
        "asmara": "Hubungan harmonis dan saling mendukung; cocok untuk memperkuat komitmen.",
        "kesehatan": "Kesehatan terjaga; perhatikan pola makan dan istirahat.",
        "studi": "Sangat baik untuk belajar, ujian, dan mengejar gelar.",
        "saran": "Perbanyak belajar dan minta bimbingan orang berpengalaman.",
    },
    "偏印": {
        "tema": "tahun riset, intuisi, dan hal-hal unik. Energi pendukung datang dari bidang non-mainstream.",
        "karir": "Karier menuntut pemikiran di luar kotak; cocok untuk riset, analisis, teknologi, atau profesi spesialis.",
        "keuangan": "Keuangan pas-pasan menantang; hindari investasi yang belum dipahami benar.",
        "asmara": "Cenderung menyendiri; komunikasikan perasaan agar tidak salah paham.",
        "kesehatan": "Perhatikan kesehatan mental; jangan memendam masalah sendirian.",
        "studi": "Bagus untuk riset mendalam; hindari belajar yang terlalu melompat-lompat.",
        "saran": "Percaya intuisi, tapi tetap cek fakta sebelum bertindak.",
    },
    "正官": {
        "tema": "tahun jabatan, reputasi, dan aturan. Dunia 'formal' sedang memperhatikan Anda.",
        "karir": "Peluang naik jabatan, penugasan resmi, dan pengakuan profesional terbuka lebar.",
        "keuangan": "Keuangan meningkat seiring karier; tetap disiplin menabung.",
        "asmara": "Hubungan serius; bagi yang lajang, ada peluang bertemu pasangan lewat lingkungan kerja/formal.",
        "kesehatan": "Jaga tekanan darah dan manajemen stres karena beban tanggung jawab bertambah.",
        "studi": "Cocok untuk ujian kedinasan, sertifikasi profesi, dan jenjang akademik.",
        "saran": "Jaga nama baik dan patuhi aturan; disiplin adalah kunci tahun ini.",
    },
    "七杀": {
        "tema": "tahun tantangan, tekanan, dan persaingan. Medan pertempuran sedang terbuka.",
        "karir": "Tekanan kerja meningkat; ini ujian ketangguhan. Berani mengambil tanggung jawab besar, tetapi jangan memaksakan diri.",
        "keuangan": "Keuangan berisiko; hindari utang dan spekulasi besar.",
        "asmara": "Potensi konflik dengan pasangan; kendalikan emosi dan ego.",
        "kesehatan": "Rawan kecelakaan kecil dan penyakit mendadak; istirahat cukup, jaga diri ekstra.",
        "studi": "Belajar penuh tekanan; target ambisius bisa tercapai jika terorganisir.",
        "saran": "Hadapi tantangan dengan kepala dingin; olahraga untuk melepas stres.",
    },
    "正财": {
        "tema": "tahun rezeki utama: gaji, usaha, dan hasil kerja keras. Energi uang sedang mengalir.",
        "karir": "Kinerja dihargai; cocok mengejar target, kenaikan gaji, atau ekspansi usaha.",
        "keuangan": "Keuangan membaik; waktu yang tepat menabung, investasi aman, dan melunasi utang.",
        "asmara": "Hubungan stabil; bagi pria, energi 'istri' positif — cocok menikah atau memperkuat rumah tangga.",
        "kesehatan": "Baik; jaga pola makan agar tidak kekenyangan saat perayaan.",
        "studi": "Disiplin belajar membuahkan nilai bagus.",
        "saran": "Kerja keras Anda akan dibayar; kelola pemasukan dengan bijak.",
    },
    "偏财": {
        "tema": "tahun rezeki sampingan: bisnis, peluang besar, dan kejutan finansial.",
        "karir": "Peluang usaha sampingan, proyek besar, atau tawaran menggiurkan bermunculan. Jeli menangkapnya.",
        "keuangan": "Ada potensi untung besar, tetapi juga risiko besar; kelola dengan hati-hati, jangan serakah.",
        "asmara": "Karisma naik, banyak perhatian; bagi yang berpasangan, jaga diri dari godaan.",
        "kesehatan": "Perhatikan pola hidup karena kecenderungan hura-hura; batasi alkohol dan lemak.",
        "studi": "Bagus untuk beasiswa dan kompetisi; jangan mudah teralihkan.",
        "saran": "Tangkap peluang besar, tapi pasang batas kerugian sebelum memulai.",
    },
    "比肩": {
        "tema": "tahun kemandirian, persaingan, dan teman. Energi 'sesama' sedang kuat.",
        "karir": "Persaingan ketat; andalkan kekuatan sendiri, tetapi jangan menolak kerja sama.",
        "keuangan": "Pengeluaran untuk relasi meningkat; hindari jadi penjamin utang teman.",
        "asmara": "Ego bisa memicu pertengkaran; belajar mengalah.",
        "kesehatan": "Cukup baik; waspadai kelelahan karena terlalu banyak aktivitas.",
        "studi": "Belajar mandiri efektif; bergabung kelompok belajar untuk saling menguatkan.",
        "saran": "Berdiri di atas kaki sendiri, tapi tetap jaga relasi.",
    },
    "劫财": {
        "tema": "tahun pengeluaran tak terduga dan relasi yang menguras. Berhati-hatilah dengan 'teman'.",
        "karir": "Rezeki ada tetapi cepat keluar; waspadai mitra yang bermasalah dan janji palsu.",
        "keuangan": "Rentan bocor: pinjaman, ditipu, atau pengeluaran impulsif. Catat setiap rupiah.",
        "asmara": "Ada pihak ketiga/gangguan; perkuat komunikasi dengan pasangan.",
        "kesehatan": "Jaga kesehatan pencernaan dan hindari minuman keras.",
        "studi": "Jangan mudah terganggu ajakan teman; fokus pada target.",
        "saran": "Disiplin anggaran; jangan meminjamkan uang yang Anda butuhkan.",
    },
    "食神": {
        "tema": "tahun kreativitas, karya, dan kenikmatan hidup. Rezeki datang dari bakat.",
        "karir": "Cocok meluncurkan produk, karya seni, atau inovasi; hasil kerja Anda diapresiasi publik.",
        "keuangan": "Rezeki mengalir dari karya dan keahlian; peluang mengembangkan usaha kuliner/kreatif.",
        "asmara": "Suasana hangat dan romantis; waktu yang baik untuk quality time.",
        "kesehatan": "Bagus — energi positif; jaga berat badan karena nafsu makan meningkat.",
        "studi": "Belajar terasa ringan; hasilkan karya tulis/proyek yang dipamerkan.",
        "saran": "Salurkan kreativitas; jangan menunda ide yang sudah matang.",
    },
    "伤官": {
        "tema": "tahun bakat, inovasi, dan keinginan bebas. Energi 'membongkar' sedang aktif.",
        "karir": "Ide cemerlang tetapi rawan konflik dengan atasan/aturan; sampaikan pendapat dengan sopan.",
        "keuangan": "Pendapatan dari bakat bisa bagus, tetapi gaya hidup boros menggerus; buat anggaran.",
        "asmara": "Emosi naik-turun; hindari berkata-kata tajam yang melukai pasangan.",
        "kesehatan": "Perhatikan tenggorokan, kulit, dan kecenderungan begadang.",
        "studi": "Kreativitas tinggi; cocok lomba, karya ilmiah, dan proyek inovatif.",
        "saran": "Salurkan energi lewat karya; kendalikan lidah di tempat kerja.",
    },
}

# --- Catatan bulanan (流月) per 十神 batang bulan ---
MONTH_NOTE = {
    "正印": "bulan belajar & berkah dokumen — baik mengurus administrasi, menuntut ilmu, dan minta bimbingan.",
    "偏印": "bulan riset & intuisi — cocok analisis mendalam; jangan ambil keputusan besar sendirian.",
    "正官": "bulan tanggung jawab — peluang pengakuan/jabatan; jaga sikap dan nama baik.",
    "七杀": "bulan tekanan — waspadai konflik & kecelakaan kecil; kerjakan hal penting lebih awal.",
    "正财": "bulan rezeki utama — kerja keras dihargai; baik menabung dan melunasi utang.",
    "偏财": "bulan peluang sampingan — tawaran bisnis bermunculan; kelola risiko dengan cermat.",
    "比肩": "bulan persaingan — andalkan diri sendiri; cocok kerja tim bila egonya dikelola.",
    "劫财": "bulan boros — waspadai pengeluaran dan pinjaman; pegang erat anggaran.",
    "食神": "bulan kreativitas — rezeki dari karya; baik meluncurkan ide dan menikmati hidup.",
    "伤官": "bulan inovasi & gejolak — ide bagus, tetapi jaga ucapan; hindari konflik dengan atasan.",
}

# --- Fase 大运 ---
DA_YUN_QUALITY = {
    (True, "正印"): "FASE EMAS — masa belajar, perlindungan, dan pembangunan fondasi. Energi tahun-tahun ini menopang Anda.",
    (True, "食神"): "FASE EMAS — kreativitas mekar dan rezeki mengalir dari karya. Waktu terbaik meluncurkan sesuatu.",
    (True, "正财"): "FASE EMAS — masa panen finansial. Kerja keras dibayar lunas; cocok menabung, investasi, dan menikah.",
    (True, "正官"): "FASE EMAS — masa pengakuan. Jabatan, reputasi, dan kepercayaan publik meningkat.",
    (True, "偏财"): "FASE BAIK — peluang besar di bisnis dan proyek; untung besar dengan risiko yang harus dikelola.",
    (True, "偏印"): "FASE BAIK — keahlian spesialis & riset berkembang; jalan unik Anda terbuka.",
    (True, "比肩"): "FASE BAIK — kemandirian menguat; cocok membangun usaha sendiri meski persaingan ada.",
    (True, "七杀"): "FASE BAIK-MENANTANG — ambisi besar bisa menang besar, tetapi tekanannya nyata.",
    (True, "伤官"): "FASE BAIK-MENANTANG — bakat meledak, tetapi konflik dengan aturan menghantui; jaga sikap.",
    (True, "劫财"): "FASE MENCAMPUR — semangat tinggi, tetapi uang cepat keluar; disiplin anggaran wajib.",
    (False, "正印"): "FASE MENENANGKAN — tetap ada perlindungan, tetapi pertumbuhan melambat; fokus konsolidasi.",
    (False, "食神"): "FASE NETRAL — kreativitas ada tetapi hasil belum maksimal; terus berproses.",
    (False, "正财"): "FASE MENJAGA — rezeki ada tetapi seret; hindari ekspansi besar, perkuat cadangan.",
    (False, "正官"): "FASE MENJAGA — beban tanggung jawab bertambah; jalani dengan disiplin, jangan memaksakan diri.",
    (False, "偏财"): "FASE BERISIKO — godaan untung cepat besar; waspadai penipuan dan spekulasi.",
    (False, "偏印"): "FASE RENUNG — energi menurun, pikiran berat; perbanyak istirahat dan jangan mengambil keputusan besar.",
    (False, "比肩"): "FASE BERAT — harus mandiri di tengah persaingan; jangan bergantung pada orang lain.",
    (False, "七杀"): "FASE SULIT — tekanan dan hambatan besar; bertahan dengan disiplin, jaga kesehatan.",
    (False, "伤官"): "FASE SULIT — konflik dengan aturan/atasan berisiko; kendalikan emosi dan ucapan.",
    (False, "劫财"): "FASE SULIT — kehilangan uang/relasi; jangan meminjamkan, hindari utang baru.",
}


def _da_yun_quality(dy: DaYun) -> str:
    return DA_YUN_QUALITY.get((dy.favorable, dy.ten_god_stem),
                              "FASE TRANSISI — energi campuran; jalani dengan penuh kewaspadaan dan kesabaran.")


# ---------------------------------------------------------------------------
# UTILITAS FORMAT
# ---------------------------------------------------------------------------

def bar(value: float, total: float, width: int = 18) -> str:
    """Grafik batang teks."""
    ratio = value / total if total else 0
    filled = int(round(ratio * width))
    return "█" * filled + "░" * (width - filled)


def wlen(s: str) -> int:
    """Lebar tampilan string dengan memperhitungkan karakter CJK (lebar ganda)."""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)


def pad(s, width: int) -> str:
    """Pad kanan dengan perhitungan lebar CJK agar tabel rapi di terminal."""
    return s + " " * max(0, width - wlen(str(s)))


def line(char: str = "-", width: int = 72) -> str:
    return char * width


def center(text: str, width: int = 72, fill: str = "=") -> str:
    pad = max(0, width - len(text))
    left = pad // 2
    return fill * left + text + fill * (pad - left)


# ---------------------------------------------------------------------------
# BAGIAN-BAGIAN LAPORAN
# ---------------------------------------------------------------------------

def section_header(num: int, title: str) -> str:
    return f"\n{center(f' {num}. {title} ')}"


def input_info(chart: Chart) -> str:
    s = []
    s.append(center(" BAGAN BAZI (四柱) — RAMALAN NASIB ", fill="="))
    s.append("")
    s.append(f"  Tanggal lahir (Masehi) : {chart.birth:%d %B %Y}")
    s.append(f"  Jam lahir              : {chart.birth:%H:%M}")
    if chart.longitude is not None or chart.city:
        s.append(f"  Waktu matahari sejati  : {chart.true_solar:%d %B %Y %H:%M}"
                 f"  (koreksi bujur {chart.longitude}°E, zona UTC+{chart.tz:g})")
    else:
        s.append("  Waktu matahari sejati  : (tidak dikoreksi — gunakan --kota/--lon)")
    s.append(f"  Jenis kelamin          : {chart.gender}")
    if chart.city:
        s.append(f"  Kota lahir             : {chart.city}")
    s.append(f"  Bagan lengkap          : {chart.ganzhi}")
    return "\n".join(s)


def pillar_table(chart: Chart) -> str:
    s = []
    heads = ["Pilar", "Batang", "Unsur", "Cabang", "Unsur Cbg", "十神 Batang"]
    widths = [8, 8, 8, 8, 10, 12]
    s.append("  " + " ".join(pad(h, w) for h, w in zip(heads, widths)))
    s.append("  " + line("-", 68))
    for p in chart.pillars:
        row = [p.name, p.stem, p.stem_element, p.branch,
               p.branch_element, p.ten_god_stem]
        s.append("  " + " ".join(pad(x, w) for x, w in zip(row, widths)))
    s.append("  " + line("-", 68))
    return "\n".join(s)


def pillar_detail(chart: Chart) -> str:
    s = []
    for p in chart.pillars:
        s.append(f"  {p.name}柱 : {p.stem}{p.branch}  "
                 f"({p.stem_element} {p.stem_polarity} / {p.branch_element})")
        s.append(f"      Na Yin       : {p.na_yin}")
        hid = ", ".join(f"{h}({h_el},{h_tg},{w:g})" for h, h_el, h_tg, w in p.hidden)
        s.append(f"      藏干        : {hid}")
        s.append(f"      十神 batang : {p.ten_god_stem}   |   十神 cabang (qi utama): {p.ten_god_branch}")
        if p.shen_sha:
            s.append(f"      神煞        : {', '.join(p.shen_sha)}")
        if p.kong:
            s.append(f"      空亡        : cabang {p.branch} kena 空亡 (dianggap 'kosong')")
        s.append("")
    return "\n".join(s)


def element_analysis(chart: Chart) -> str:
    s = []
    total = chart.strength["total"]
    ranked = sorted(chart.element_score.items(), key=lambda kv: -kv[1])
    s.append("  Distribusi kekuatan 五行 (batang berbobot 1.0; cabang = qi "
             "tersembunyi 0.6/0.3/0.1; bonus 月令 +1.2):")
    s.append("")
    for el, sc in ranked:
        share = sc / total * 100 if total else 0
        s.append(f"     {el} {ELEMENT_NAME[el]:<5} {bar(sc, total)} {sc:5.1f}  ({share:4.1f}%)")
    s.append("")
    s.append("  Siklus 生 (melahirkan): " + " → ".join(
        f"{ELEMENT_NAME[e]}" for e in ["木", "火", "土", "金", "水", "木"]))
    s.append("  Siklus 克 (menguasai):  " + ", ".join(
        f"{ELEMENT_NAME[a]}克{ELEMENT_NAME[b]}" for a, b in CONTROLS.items()))
    s.append("")
    strongest = ranked[0][0]
    weakest = ranked[-1][0]
    s.append(f"  → Unsur terkuat: {ELEMENT_NAME[strongest]} ({strongest});  "
             f"terlemah: {ELEMENT_NAME[weakest]} ({weakest}).")
    # rincian per posisi
    s.append("")
    s.append("  Rincian bobot per posisi:")
    for pname, det in chart.element_detail.items():
        parts = ", ".join(f"{pos}:{el}({w:g})" for pos, (el, w) in det.items())
        s.append(f"     {pname}: {parts}")
    return "\n".join(s)


def strength_analysis(chart: Chart) -> str:
    st = chart.strength
    s = []
    dm = chart.dm
    s.append(f"  Hari Utama (日主): {dm} ({ELEMENT_NAME[chart.dm_element]}) — "
             f"pribadi {chart.dm_element} seperti dijelaskan di atas.")
    s.append("")
    de_ling = {0: "tidak 得令", 1: "得相 (musim menopang)", 2: "得令 (lahir di musimnya)"}[st["de_ling"]]
    s.append(f"  得令 (musim)   : {de_ling} — bulan lahir berunsur {ELEMENT_NAME[st['season']]}")
    s.append(f"  得地 (akar)    : skor akar unsur Hari Utama di cabang = {st['root_score']:.2f}")
    s.append(f"  得势 (dukungan): skor dukungan sesama unsur + unsur pelahir = {st['support']:.2f}")
    s.append(f"  Porsi kekuatan : {st['share']:.1f}% dari total kekuatan bagan")
    s.append("")
    verdict = st["verdict"]
    if verdict == "KUAT":
        vtext = ("Hari Utama Anda KUAT — pribadi mandiri, bertenaga, dan tahan banting. "
                 "Keberuntungan datang dari hal-hal yang 'menguras' energi: karier yang "
                 "menuntut, pengelolaan uang, dan karya yang dikeluarkan ke dunia.")
    elif verdict == "LEMAH":
        vtext = ("Hari Utama Anda LEMAH — pribadi yang sensitif dan membutuhkan dukungan. "
                 "Keberuntungan datang dari belajar (印), kerja sama, dan lingkungan yang "
                 "mendukung. Jangan memaksakan diri sendirian.")
    else:
        vtext = ("Hari Utama Anda SEIMBANG — pribadi yang fleksibel, mudah menyesuaikan diri. "
                 "Keberuntungan datang dari menambah unsur yang kurang dan mengendalikan "
                 "unsur yang berlebih di dalam diri.")
    s.append(f"  Verdict: {verdict}")
    s.append(f"  {vtext}")
    return "\n".join(s)


def lucky_analysis(chart: Chart) -> str:
    s = []
    fav = chart.favorable
    unf = chart.unfavorable
    s.append("  Berdasarkan metode 扶抑 (menyeimbangkan kekuatan):")
    s.append("")
    s.append(f"  喜用神 (unsur keberuntungan) : {', '.join(fav)}  "
             f"({', '.join(ELEMENT_NAME[e] for e in fav)})")
    s.append(f"  忌神   (unsur penghambat)    : {', '.join(unf)}  "
             f"({', '.join(ELEMENT_NAME[e] for e in unf)})")
    s.append("")
    s.append("  Panduan praktis:")
    for el in fav:
        luck = element_lucky(el)
        s.append(f"     Unsur {ELEMENT_NAME[el]} ({el}): warna {luck['color']}, "
                 f"angka {luck['number']}, arah {luck['direction']}.")
    s.append("")
    s.append("  Catatan 调候 (penyesuaian iklim): ")
    dm_e = chart.dm_element
    season = chart.strength["season"]
    if season == "水" and dm_e != "火":
        s.append("     lahir di musim dingin (亥子丑月) → tambahkan unsur 火 (Api) "
                 "sebagai penghangat: warna merah, aktifitas sosial, paparan sinar matahari.")
    elif dm_e == "木" and season == "金":
        s.append("     lahir di musim gugur (logam kuat menebang kayu) → perkuat 水 (Air) "
                 "sebagai perantara, dan hindari terlalu banyak 金.")
    elif dm_e == "火" and season in ("水", "金"):
        s.append("     lahir di musim dingin/gugur → perkuat 木 (Kayu) sebagai "
                 "'bahan bakar' api agar semangat tetap menyala.")
    else:
        s.append("     tidak ada penyesuaian iklim khusus; gunakan panduan 喜用 di atas.")
    return "\n".join(s)


def ten_god_profile(chart: Chart) -> str:
    s = []
    counts = sorted(chart.ten_god_counts.items(), key=lambda kv: -kv[1])
    total = sum(v for _, v in counts)
    s.append("  Kemunculan 十神 dalam bagan (batang=1.0, qi cabang sesuai bobot):")
    s.append("")
    for tg, v in counts:
        share = v / total * 100 if total else 0
        name, desc = TEN_GOD_DESC.get(tg, (tg, ""))
        s.append(f"     {tg:<4} ({name:<12}) {v:4.1f}  ({share:4.1f}%)  — {desc}")
    s.append("")
    top = [tg for tg, _ in counts[:2] if counts[0][1] > 0]
    if top:
        names = ", ".join(TEN_GOD_DESC.get(t, (t, ""))[0] for t in top)
        s.append(f"  → Pola dominan: {names}. Sifat ini paling menonjol dalam "
                 "kepribadian dan arah hidup Anda.")
    return "\n".join(s)


def shen_sha_summary(chart: Chart) -> str:
    s = []
    found = False
    for p in chart.pillars:
        if p.shen_sha:
            found = True
            for sh in p.shen_sha:
                desc = SHEN_SHA_DESC.get(sh, "")
                s.append(f"     {p.name}柱 ({p.branch}): {sh} — {desc}")
    if not found:
        s.append("     Tidak ada 神煞 utama yang aktif pada cabang-cabang bagan.")
    s.append("")
    s.append(f"  空亡 (cabang 'kosong'): {', '.join(chart.kong_wang)} — pengaruh cabang ini "
             "dianggap melemah/hampa pada periode yang bersesuaian.")
    ty_s, ty_b = chart.tai_yuan
    mg_s, mg_b = chart.ming_gong
    s.append(f"  胎元 (asal janin) : {ty_s}{ty_b} — gambaran pengaruh masa kandungan.")
    s.append(f"  命宫 (istana takdir): {mg_s}{mg_b} — gambaran 'rumah' bakat utama Anda.")
    return "\n".join(s)


def da_yun_report(dys: list, chart: Chart) -> str:
    s = []
    ys = chart.year_pillar.stem_idx
    forward = (ys % 2 == 0 and chart.gender == "pria") or (ys % 2 == 1 and chart.gender == "wanita")
    s.append(f"  Arah 大运: {'顺行 MAJU — pilar bergeser maju dari pilar bulan' if forward else '逆行 MUNDUR — pilar bergeser mundur dari pilar bulan'}")
    first = dys[0]
    s.append(f"  Usia mulai 大运 pertama: {first.start_age} tahun "
             f"(±{first.start_date:%d %B %Y}).")
    s.append("")
    heads = ["No", "Pilar", "Rentang Usia", "Rentang Tahun", "十神", "Kualitas"]
    widths = [4, 8, 12, 12, 8, 18]
    s.append("  " + " ".join(pad(h, w) for h, w in zip(heads, widths)))
    s.append("  " + line("-", 68))
    for dy in dys:
        row = [str(dy.index), dy.gan_zhi, f"{dy.start_age}-{dy.end_age}",
               f"{dy.start_year}-{dy.end_year}", dy.ten_god_stem,
               "selaras" if dy.favorable else "kurang selaras"]
        s.append("  " + " ".join(pad(x, w) for x, w in zip(row, widths)))
    s.append("  " + line("-", 68))
    s.append("")
    s.append("  Penjelasan setiap fase (bahasa sehari-hari):")
    for dy in dys:
        s.append(f"")
        s.append(f"  ● {dy.gan_zhi} ({ELEMENT_NAME[dy.stem_element]} {dy.stem_element} + "
                 f"{ELEMENT_NAME[dy.branch_element]} {dy.branch_element}) — usia "
                 f"{dy.start_age}-{dy.end_age} ({dy.start_year}-{dy.end_year})")
        s.append(f"      {_da_yun_quality(dy)}")
        _, tg_desc = TEN_GOD_DESC.get(dy.ten_god_stem, (dy.ten_god_stem, ""))
        s.append(f"      十神 batang: {dy.ten_god_stem} — {tg_desc}")
        if dy.favorable:
            s.append(f"      Saran: manfaatkan fase ini untuk {_dy_advice(dy)}.")
        else:
            s.append(f"      Saran: fokus bertahan & konsolidasi; hindari ekspansi besar; "
                     f"{_dy_advice(dy)}.")
    return "\n".join(s)


def _dy_advice(dy: DaYun) -> str:
    tg = dy.ten_god_stem
    if tg in ("正印", "偏印"):
        return "pendidikan, sertifikasi, dan membangun fondasi"
    if tg in ("正财", "偏财"):
        return "menabung, investasi, dan mengelola arus kas"
    if tg in ("正官", "七杀"):
        return "meniti karier, kepemimpinan, dan reputasi"
    if tg in ("食神", "伤官"):
        return "karya, kreativitas, dan meluncurkan produk"
    return "memperkuat jejaring dan kemandirian"


def liu_nian_report(lns: list, chart: Chart, year_from: int, year_to: int) -> str:
    s = []
    # ringkasan rentang
    s.append(f"  Rentang: {year_from}-{year_to} (usia {year_from - chart.birth.year}–"
             f"{year_to - chart.birth.year} tahun). Skor 0-100; semakin tinggi semakin baik.")
    s.append("")
    for ln in lns:
        shio = SHIO[BRANCHES.index(ln.branch)]
        s.append(f"  {line('-', 68)}")
        s.append(f"  {ln.year} — {ln.gan_zhi} ({ELEMENT_NAME[ln.stem_element]} "
                 f"{ln.stem_element}, shio {shio}) — usia {ln.age} th — "
                 f"SKOR {ln.score}/100 — {ln.grade}")
        tg = ln.ten_god_stem
        info = TEN_GOD_YEAR.get(tg)
        if info:
            s.append(f"  Tema besar : {info['tema']}")
            s.append(f"  Karier     : {info['karir']}")
            s.append(f"  Keuangan   : {info['keuangan']}")
            s.append(f"  Asmara     : {info['asmara']}")
            s.append(f"  Kesehatan  : {info['kesehatan']}")
            s.append(f"  Studi      : {info['studi']}")
            s.append(f"  Saran      : {info['saran']}")
        if ln.flags:
            neg = [f for f in ln.flags if any(k in f for k in ("冲", "刑", "害", "空亡"))]
            pos = [f for f in ln.flags if any(k in f for k in ("合", "桃花"))]
            if pos:
                s.append(f"  Kabar baik : " + "; ".join(pos) +
                         " — energi menyatu: kerja sama, relasi, dan bantuan "
                         "mengalir lebih lancar. Manfaatkan momen ini.")
            if neg:
                s.append(f"  Waspada    : " + "; ".join(neg) +
                         " — hindari keputusan besar saat energi bentrok; "
                         "jaga kesehatan dan arus kas.")
        if ln.score >= 70:
            s.append(f"  ★ Momentum tahun ini positif — manfaatkan untuk langkah besar.")
        elif ln.score <= 44:
            s.append(f"  ⚠ Tahun ini menuntut kehati-hatian ekstra — jaga kesehatan, "
                     f"arus kas, dan jangan memaksakan keputusan besar.")
        s.append("")
    return "\n".join(s)


def liu_yue_report(lms: list) -> str:
    s = []
    for lm in lms:
        tg = lm.ten_god_stem
        note = MONTH_NOTE.get(tg, "bulan energi campuran.")
        s.append(f"  {lm.name:<12} {lm.gan_zhi} (mulai {lm.jie_name}) — skor {lm.score:2d}/100 "
                 f"[{lm.grade:<12}] — {tg}: {note}")
    return "\n".join(s)


def disclaimer() -> str:
    return (
        "\n" + line("=", 72) + "\n"
        "  CATATAN PENTING\n"
        "  • Bazi adalah tradisi metafisika Tionghoa (Ziwshu) berusia ribuan tahun. "
        "Hasil ini\n"
        "    adalah interpretasi simbolik untuk refleksi & hiburan, BUKAN kepastian "
        "ilmiah.\n"
        "  • Keputusan penting (keuangan, kesehatan, karier, pernikahan) tetap "
        "berdasarkan\n"
        "    pertimbangan rasional dan nasihat profesional.\n"
        "  • Perhitungan 节气 memakai algoritma astronomi (akurasi ±15 menit); kelahiran\n"
        "    tepat di perbatasan jam 23:00 / 节气 dapat mengubah pilar.\n"
        "  • Metode kekuatan Hari Utama & skor tahunan adalah penyederhanaan "
        "pedagogis\n"
        "    (扶抑法) — peramal profesional dapat memberi analisis yang lebih "
        "mendalam.\n"
        + line("=", 72)
    )


# ---------------------------------------------------------------------------
# LAPORAN UTUH
# ---------------------------------------------------------------------------

def full_report(chart: Chart, dys: list, lns: list, lms: list,
                year_from: int, year_to: int) -> str:
    parts = []
    parts.append(input_info(chart))
    parts.append(section_header(1, "EMPAT PILAR (四柱)"))
    parts.append(pillar_table(chart))
    parts.append("")
    parts.append(pillar_detail(chart))
    parts.append(section_header(2, "ANALISIS UNSUR (五行)"))
    parts.append(element_analysis(chart))
    parts.append(section_header(3, "KEKUATAN HARI UTAMA (日主)"))
    parts.append(strength_analysis(chart))
    parts.append("")
    parts.append(f"  Kepribadian {chart.dm_element}: {ELEMENT_PERSONALITY[chart.dm_element]}")
    parts.append(section_header(4, "UNSUR KEBERUNTUNGAN (喜用神 & 忌神)"))
    parts.append(lucky_analysis(chart))
    parts.append(section_header(5, "PROFIL 十神 (Sepuluh Dewa)"))
    parts.append(ten_god_profile(chart))
    parts.append(section_header(6, "神煞, 空亡, 胎元 & 命宫"))
    parts.append(shen_sha_summary(chart))
    parts.append(section_header(7, "大运 — SIKLUS 10 TAHUNAN"))
    parts.append(da_yun_report(dys, chart))
    parts.append(section_header(8, f"PERUNTUNGAN TAHUNAN (流年) {year_from}-{year_to}"))
    parts.append(liu_nian_report(lns, chart, year_from, year_to))
    if lms:
        parts.append(section_header(9, f"PERUNTUNGAN BULANAN (流月) {lms[0].name.split()[-1]}"))
        parts.append(liu_yue_report(lms))
    parts.append(disclaimer())
    return "\n".join(parts)
