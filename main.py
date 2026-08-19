#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py — Antarmuka baris perintah (CLI) Bazi Fortune Forecasting.

Contoh penggunaan:
    python3 main.py --tanggal 1995-08-17 --jam 09:30 --gender pria
    python3 main.py --tanggal 1995-08-17 --jam 09:30 --gender pria \
                     --kota semarang --dari 2026 --sampai 2046 --output hasil.txt
    python3 main.py --contoh          # demo cepat dengan data contoh
    python3 main.py                   # mode interaktif (tanya jawab)
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime

from bazi_core import (build_chart, compute_da_yun, compute_liu_nian_range,
                       compute_liu_yue, CITIES)
from bazi_text import full_report

# ANSI warna sederhana untuk terminal
COLOR = {
    "bold": "\033[1m", "cyan": "\033[96m", "green": "\033[92m",
    "yellow": "\033[93m", "red": "\033[91m", "reset": "\033[0m",
}


def parse_args(argv):
    p = argparse.ArgumentParser(
        prog="bazi-fortune",
        description="Peramal keberuntungan metode Bazi (Empat Pilar) — "
                    "perhitungan unsur lengkap + ramalan tahunan bahasa sehari-hari.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--tanggal", help="Tanggal lahir Masehi, format YYYY-MM-DD (mis. 1995-08-17)")
    p.add_argument("--jam", help="Jam lahir, format HH:MM (mis. 09:30; 24 jam)")
    p.add_argument("--gender", choices=["pria", "wanita"], help="Jenis kelamin (untuk arah 大运)")
    p.add_argument("--kota", default="", help="Kota lahir untuk koreksi waktu matahari sejati "
                                              "(mis. semarang, jakarta, surabaya)")
    p.add_argument("--lon", type=float, default=None, help="Bujur timur lokasi lahir (derajat)")
    p.add_argument("--zona", type=float, default=7.0, help="Zona waktu UTC (default 7 = WIB)")
    p.add_argument("--dari", type=int, default=2026, help="Tahun awal peruntungan (default 2026)")
    p.add_argument("--sampai", type=int, default=2046, help="Tahun akhir peruntungan (default 2046)")
    p.add_argument("--bulanan", type=int, default=None, nargs="?",
                   help="Tampilkan peruntungan 12 bulan bazi pada tahun ini (default: tahun berjalan)")
    p.add_argument("--output", "-o", default="", help="Simpan laporan lengkap ke file teks")
    p.add_argument("--no-warna", action="store_true", help="Nonaktifkan warna ANSI di terminal")
    p.add_argument("--contoh", action="store_true", help="Jalankan demo dengan data contoh")
    return p.parse_args(argv)


def prompt(msg: str) -> str:
    return input(msg).strip()


def interactive():
    print("=== BAZI FORTUNE FORECASTING — mode interaktif ===")
    print("(Ketik kosong lalu Enter untuk keluar)\n")
    while True:
        tgl = prompt("Tanggal lahir (YYYY-MM-DD): ")
        if not tgl:
            return None
        try:
            tanggal = datetime.strptime(tgl, "%Y-%m-%d")
        except ValueError:
            print("  Format salah. Contoh: 1995-08-17\n")
            continue
        jam = prompt("Jam lahir (HH:MM, 24 jam): ")
        if not jam:
            return None
        try:
            jam_t = datetime.strptime(jam, "%H:%M")
        except ValueError:
            print("  Format salah. Contoh: 09:30\n")
            continue
        gender = prompt("Jenis kelamin (pria/wanita): ").lower()
        if gender not in ("pria", "wanita"):
            print("  Pilih 'pria' atau 'wanita'.\n")
            continue
        kota = prompt("Kota lahir (opsional, Enter untuk lewati): ").lower()
        dari = prompt("Tahun awal ramalan (Enter = 2026): ") or "2026"
        sampai = prompt("Tahun akhir ramalan (Enter = 2046): ") or "2046"
        try:
            birth = datetime(tanggal.year, tanggal.month, tanggal.day,
                             jam_t.hour, jam_t.minute)
            return {
                "birth": birth, "gender": gender, "kota": kota,
                "dari": int(dari), "sampai": int(sampai),
                "bulanan": datetime.now().year,
            }
        except ValueError as e:
            print(f"  Input tidak valid: {e}\n")
            continue


def main(argv=None):
    args = parse_args(argv)

    # --- siapkan input ---
    if args.contoh:
        birth = datetime(1995, 8, 17, 9, 30)
        gender, kota = "pria", "semarang"
        dari, sampai, bulanan = args.dari, args.sampai, args.bulanan or 2026
        print("  [demo] Data contoh: lahir 17-08-1995 09:30, pria, Semarang.\n")
    elif args.tanggal and args.jam and args.gender:
        try:
            birth = datetime.strptime(f"{args.tanggal} {args.jam}", "%Y-%m-%d %H:%M")
        except ValueError:
            print("Format tanggal/jam salah. Gunakan --tanggal YYYY-MM-DD --jam HH:MM")
            return 2
        gender = args.gender
        kota = args.kota.lower()
        dari, sampai = args.dari, args.sampai
        bulanan = args.bulanan
        if bulanan is None:
            bulanan = datetime.now().year
    else:
        data = interactive()
        if data is None:
            print("Dibatalkan.")
            return 0
        birth = data["birth"]
        gender = data["gender"]
        kota = data["kota"]
        dari, sampai = data["dari"], data["sampai"]
        bulanan = data["bulanan"]

    if dari > sampai:
        print("--dari harus <= --sampai")
        return 2

    # --- koreksi kota ---
    lon = args.lon if args.lon is not None else None
    apply_ts = bool(kota or lon)
    if kota and kota not in CITIES:
        print(f"Kota '{kota}' tidak ada dalam tabel. Kota yang tersedia: "
              f"{', '.join(sorted(CITIES))}")
        print("Gunakan --lon <bujur> dan --zona <UTC> untuk lokasi lain.")
        return 2

    # --- hitung ---
    chart = build_chart(birth, gender, city=kota, longitude=lon,
                        tz_hours=args.zona, apply_true_solar=apply_ts)
    dys = compute_da_yun(chart, count=10)
    lns = compute_liu_nian_range(chart, dari, sampai, dys)
    lms = compute_liu_yue(chart, bulanan) if bulanan else []

    report = full_report(chart, dys, lns, lms, dari, sampai)

    # --- keluaran ---
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report + "\n")
        print(f"Laporan tersimpan: {args.output}")
        print("=" * 72)
    if not args.no_warna and sys.stdout.isatty():
        # warna minimal: header cyan, angka skor hijau/merah
        lines = report.split("\n")
        out = []
        for ln in lines:
            if ln.startswith("=") or "BAGAN BAZI" in ln:
                out.append(COLOR["cyan"] + ln + COLOR["reset"])
            elif ln.strip().startswith("SKOR") and ("HATI-HATI" in ln or "KURANG" in ln):
                out.append(COLOR["red"] + ln + COLOR["reset"])
            elif "SKOR" in ln and "SANGAT BAIK" in ln:
                out.append(COLOR["green"] + ln + COLOR["reset"])
            else:
                out.append(ln)
        print("\n".join(out))
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
