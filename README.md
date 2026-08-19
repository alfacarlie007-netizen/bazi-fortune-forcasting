# Bazi Fortune Forecasting

Peramal keberuntungan berbasis **Bazi (八字 / Empat Pilar Takdir)** — tradisi
metafisika Tionghoa — dengan **perhitungan unsur (五行) lengkap dan transparan**,
ditulis murni dalam Python **tanpa dependensi eksternal** (hanya stdlib).

Program ini menghitung bagan Bazi dari tanggal & jam lahir Masehi, menganalisis
kekuatan unsur, menentukan unsur keberuntungan (喜用神), lalu meramalkan
peruntungan **大运 (siklus 10 tahunan)**, **流年 (tahunan)**, dan **流月 (bulanan)**
dalam **bahasa sehari-hari yang mudah dipahami**.

---

## Fitur

| Fitur | Keterangan |
|-------|------------|
| 四柱 (Empat Pilar) | Tahun, Bulan, Hari, Jam — batas 立春 / 12 节气 / jam 23:00 |
| 五行 (Lima Unsur) | Distribusi bobot Kayu-Api-Tanah-Logam-Air + grafik + siklus 生/克 |
| 纳音 (Na Yin) | 60 tabel lengkap (mis. 海中金, 炉中火, ...) |
| 藏干 (Hidden Stems) | Qi tersembunyi tiap cabang + bobot 0.6/0.3/0.1 |
| 十神 (Ten Gods) | 比肩/劫财/食神/伤官/偏财/正财/七杀/正官/偏印/正印 |
| 神煞 (Shen Sha) | 天乙贵人, 文昌, 桃花, 驿马, 华盖, 将星, 禄神, 羊刃 |
| 空亡 / 胎元 / 命宫 | Cabang kosong, asal janin, istana takdir |
| Kekuatan 日主 | 得令 / 得地 / 得势 + verdict KUAT / LEMAH / SEIMBANG |
| 喜用神 & 忌神 | Metode 扶抑 transparan + warna/angka/arah keberuntungan |
| 大运 | Arah 顺行/逆行, usia mulai (3 hari = 1 tahun), 10 fase |
| 流年 | Skor 0-100 per tahun + tema karier/keuangan/asmara/kesehatan/studi |
| 流月 | Peruntungan 12 bulan bazi |
| Waktu matahari sejati | Koreksi bujur + equation of time (opsional, via --kota/--lon) |
| Interaktif & CLI | Argumen baris perintah atau mode tanya-jawab |

---

## Cara Pakai

Tidak perlu `pip install` — **murni stdlib Python 3.8+**.

```bash
# Perintah dasar
python3 main.py --tanggal 1995-08-17 --jam 09:30 --gender pria

# Dengan kota lahir (koreksi waktu matahari sejati) + rentang ramalan
python3 main.py --tanggal 1995-08-17 --jam 09:30 --gender pria \
                --kota semarang --dari 2026 --sampai 2046

# Simpan laporan ke file
python3 main.py --tanggal 1995-08-17 --jam 09:30 --gender pria \
                --kota semarang -o hasil_bazi.txt

# Demo cepat dengan data contoh
python3 main.py --contoh

# Mode interaktif (tanya-jawab)
python3 main.py
```

### Opsi Lengkap

```
--tanggal   YYYY-MM-DD      tanggal lahir Masehi
--jam       HH:MM           jam lahir (24 jam)
--gender    pria|wanita     jenis kelamin (menentukan arah 大运)
--kota      NAMA            kota lahir (koreksi waktu matahari sejati)
--lon       DERAJAT         bujur timur lokasi (kustom)
--zona      UTC             zona waktu (default 7 = WIB)
--dari      TAHUN           tahun awal peruntungan (default 2026)
--sampai    TAHUN           tahun akhir peruntungan (default 2046)
--bulanan   TAHUN           tampilkan 流月 12 bulan bazi pada tahun itu
--output/-o FILE            simpan laporan ke file
--no-warna                  matikan warna ANSI
--contoh                    jalankan demo
```

Contoh keluaran lengkap tersedia di [`examples/contoh_keluaran.txt`](examples/contoh_keluaran.txt).

---

## Metode Perhitungan

### 1. Kalender & astronomi
- **Julian Day Number (JDN)** dihitung langsung dari tanggal Masehi.
- **Posisi matahari** dihitung dengan algoritma J. Meeus
  (*Astronomical Algorithms*) — bujur ekliptika semu, akurasi ~0.01°.
- **24 节气**: waktu matahari melintasi bujur kelipatan 15° dicari dengan
  pencarian biner hingga presisi ~1 menit. Yang dipakai untuk pilar bulan
  adalah 12 "节": 立春, 惊蛰, 清明, 立夏, 芒种, 小暑, 立秋, 白露, 寒露,
  立冬, 大雪, 小寒.
- **Waktu matahari sejati** (opsional): `koreksi = (bujur − meridian zona) × 4
  menit + equation of time`. Tabel 50+ kota Indonesia tersedia.

### 2. Empat Pilar (四柱)
- **Tahun**: berganti di **立春** (bukan 1 Januari).
- **Bulan**: berganti di 12 节; batang bulan memakai rumus 五虎遁.
- **Hari**: berganti **jam 23:00**; indeks dari JDN (anchor: 1949-10-01 = 甲子).
- **Jam**: 子=23:00–00:59, dst.; batang jam memakai rumus 五鼠遁.

### 3. Analisis unsur & kekuatan
- Batang berbobot 1.0; cabang diurai ke 藏干 berbobot 0.6/0.3/0.1;
  bonus 月令 +1.2 untuk qi utama bulan.
- Kekuatan Hari Utama dinilai dari 得令 (musim), 得地 (akar di cabang),
  得势 (dukungan sesama + pelahir), dan porsi skor total.
- **喜用神/忌神** memakai **metode 扶抑**: Hari Utama kuat → butuh penyalur
  (官杀/食伤/财); lemah → butuh penopang (印/比劫). Pilihan diurutkan dari
  unsur yang paling kurang di bagan.

### 4. 大运
- Arah: tahun Yang + pria / tahun Yin + wanita → **顺行 (maju)**; sebaliknya
  **逆行 (mundur)** dari pilar bulan.
- Usia mulai: jarak kelahiran ke 节 terdekat, konversi **3 hari = 1 tahun**
  (1 hari = 4 bulan, 1 jam = 5 hari).

### 5. 流年 & 流月
- Skor 0–100 tiap tahun dari: keselarasan unsur dengan 喜用/忌, 十神 tahun,
  interaksi 冲/合/刑/害/空亡 dengan pilar hari-tahun-大运, serta 桃花.
- Ramalan ditulis per bidang: karier, keuangan, asmara, kesehatan, studi.

---

## Struktur Proyek

```
bazi-fortune-forcasting/
├── main.py               # CLI + mode interaktif
├── bazi_core.py          # Mesin perhitungan (stdlib, tanpa dependensi)
├── bazi_text.py          # Interpretasi & laporan Bahasa Indonesia
├── tests/
│   ├── test_core.py      # Uji otomatis (anchor bersejarah + konsistensi)
│   └── verify_smoke.py   # Pemeriksaan cepat hasil perbaikan
├── examples/
│   └── contoh_keluaran.txt   # Contoh laporan lengkap
├── README.md
└── LICENSE               # MIT
```

---

## Validasi & Akurasi

- Anchor bersejarah yang terverifikasi di test:
  - `1949-10-01` (proklamasi RRT) = hari **甲子**
  - `2000-01-01` = hari **戊午** (bagan millennium: 己卯 丙子 戊午 戊午)
  - `1984-02-02` (sebelum 立春) = tahun **癸亥**; `1984-02-05` = **甲子**
  - 五虎遁/五鼠遁/纳音/十神: seluruh tabel diuji
  - 50 tanggal acak: konsistensi 喜用/忌
- Akurasi 节气 ~±15 menit (algoritma Meeus); kelahiran tepat di perbatasan
  jam 23:00 atau 节气 dapat mengubah pilar — lihat Catatan di laporan.

> Program ini murni offline: tidak memanggil API apa pun (bandingkan dengan
> skill `bazi` bawaan Hermes yang berbasis API online bagezi.top).

---

## Disclaimer

Bazi adalah tradisi metafisika Tionghoa berusia ribuan tahun. Hasil program ini
merupakan interpretasi simbolik untuk **refleksi & hiburan, bukan kepastian
ilmiah**. Keputusan penting (keuangan, kesehatan, karier, pernikahan) tetap
harus berdasarkan pertimbangan rasional dan nasihat profesional.

## Lisensi

MIT — silakan digunakan, disalin, dan dikembangkan bebas.
