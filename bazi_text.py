# -*- coding: utf-8 -*-
"""
bazi_text.py — Lapisan interpretasi & laporan Bahasa Indonesia.

Mengubah hasil hitungan bazi_core.py menjadi laporan yang mudah dipahami:
kepribadian, analisis unsur, kekuatan Hari Utama, unsur keberuntungan,
fase 大运, peruntungan tahunan (流年), dan peruntungan bulanan (流月) — semua
dalam bahasa sehari-hari yang LUGAS.

Setiap ramalan tahunan (流年) kini disajikan LENGKAP:
  • Peluang  — sisi baik tahun ini (karier, keuangan, asmara, kesehatan, studi)
  • Risiko   — tanda bahaya & ancaman yang disebutkan DETAIL tanpa ditutup-tutupi
  • Penangkal — nasihat/penawar praktis agar bahaya batal terjadi
  • Saran    — ringkasan sikap terbaik
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

# ---------------------------------------------------------------------------
# RAMALAN TAHUNAN (流年) per 十神 — versi LENGKAP & LUGAS
# tiap entri: tema, peluang{5}, risiko{5} (detail & blak-blakan), risiko_utama,
# penangkal[...], saran.
# ---------------------------------------------------------------------------
TEN_GOD_YEAR = {
    "正印": {
        "tema": "tahun belajar, perlindungan, dan dokumen. Banyak hal 'dibereskan' lewat jalur resmi.",
        "peluang": {
            "karier": "Karier mulus; atasan atau figur senior membuka jalan. Peluang sertifikasi, pendidikan lanjut, dan pengurusan administrasi penting sangat baik.",
            "keuangan": "Keuangan stabil dengan kemungkinan rezeki tak terduga (hibah, warisan, tunjangan). Cocok menabung dan membereskan utang lama.",
            "asmara": "Hubungan harmonis dan saling mendukung — waktu yang baik memperkuat komitmen atau membangun rumah tangga yang tenang.",
            "kesehatan": "Kesehatan cenderung terjaga; energi pemulihan baik setelah masa sulit.",
            "studi": "Sangat baik — ujian, beasiswa, dan mengejar gelar sangat diuntungkan.",
        },
        "risiko": {
            "karier": "Rasa puas diri dan 'terlalu nyaman' bisa membuat Anda lengah: promosi direbut orang lain, proyek diremehkan, atau dianggap pasif oleh atasan. Hati-hati juga terhadap dokumen yang ditunda — bisa berujung masalah administrasi, pencairan dana tertahan, atau sanksi kecil di tempat kerja.",
            "keuangan": "Aliran uang yang 'aman' membuat pengeluaran diam-diam membengkak. Waspadai utang yang ditagih mendadak, orang yang meminjam atas nama kasihan, dan dokumen keuangan yang ditandatangani tanpa dibaca.",
            "asmara": "Rutinitas bisa membuat pasangan merasa diabaikan. Ada risiko orang ketiga memanfaatkan 'kebaikan' Anda; jangan sampai kebaikan disalahartikan sebagai kedekatan berlebih.",
            "kesehatan": "Kurang gerak karena terlalu nyaman — risiko gula darah, kolesterol, dan berat badan naik. Penyakit 'diam-diam' bisa muncul tanpa gejala awal.",
            "studi": "Jangan mengandalkan 'keberuntungan' saja; soal ujian tahun ini bisa berubah bentuk. Plagiarisme atau kerja kelompok yang tidak transparan berisiko dilaporkan.",
        },
        "risiko_utama": "Kemalasan & kenyamanan semu — jangan lengah di tengah jalan, dan waspadai dokumen yang ditunda.",
        "penangkal": [
            "Tetap proaktif: jangan menunggu perintah — ambil inisiatif di tempat kerja dan studi.",
            "Buat daftar urusan administrasi & dokumen; tuntaskan paling lambat 2 minggu setelah jatuh tempo.",
            "Jangan percaya mentah-mentah figur berwibawa; verifikasi dokumen, kontrak, dan ucapan 'orang besar'.",
            "Gerakkan tubuh: olahraga 3x seminggu; cek gula darah & kolesterol bila berusia 35+.",
            "Perkuat unsur 喜用 Anda (lihat panduan warna/angka/arah) untuk menahan energi pasif.",
        ],
        "saran": "Perbanyak belajar dan minta bimbingan orang berpengalaman — tetapi tetap jalankan sendiri urusan penting Anda.",
    },
    "偏印": {
        "tema": "tahun riset, intuisi, dan hal-hal unik. Energi pendukung datang dari bidang non-mainstream.",
        "peluang": {
            "karier": "Karier menuntut pemikiran di luar kotak — riset, analisis data, teknologi, spiritualitas, atau profesi spesialis sangat diuntungkan. Temuan 'kecil' Anda bisa menjadi terobosan.",
            "keuangan": "Ada peluang pendapatan dari keahlian khusus dan proyek sampingan yang tidak banyak orang pahami.",
            "asmara": "Kedalaman batin Anda menarik tipe pasangan yang serius; hubungan bisa berkembang lewat percakapan mendalam, bukan basa-basi.",
            "kesehatan": "Energi mental kuat untuk meditasi dan pemulihan psikologis.",
            "studi": "Bagus untuk riset mendalam, skripsi/tesis, dan kajian spesifik; hindari belajar yang melompat-lompat.",
        },
        "risiko": {
            "karier": "Isolasi diri dianggap angkuh; ide non-mainstream bisa ditolak atasan dan membuat Anda frustrasi. Waspadai keputusan besar yang diambil sendirian — berisiko salah arah dan sulit diperbaiki.",
            "keuangan": "Rentan tertipu investasi 'eksotis' (kripto abal-abal, skema MLM, jual beli ilegal) karena daya tarik keunikan. Uang bisa hangus di proyek yang tidak pernah tuntas.",
            "asmara": "Cenderung menyendiri dan curiga; kesalahpahaman kecil bisa membesar menjadi perpecahan. Waspadai kecurigaan tanpa bukti.",
            "kesehatan": "Risiko gangguan tidur, overthinking, stres berkepanjangan, dan kesehatan mental. Insomnia kronis bisa memicu imun tubuh turun.",
            "studi": "Penelitian bisa tersendat: data hilang, plagiarisme tak sengaja, atau pembimbing yang tidak kooperatif — periksa ulang semua referensi.",
        },
        "risiko_utama": "Overthinking, keputusan sendirian yang keliru, dan penipuan berkedok 'ilmu unik' — jangan menutup diri.",
        "penangkal": [
            "Jangan ambil keputusan besar sendirian: uji dengan 2–3 orang tepercaya sebelum bertindak.",
            "Verifikasi fakta: cek legalitas investasi/lembaga (OJK, Kemenkumham) sebelum mengeluarkan uang.",
            "Jaga jadwal tidur tetap (tidur ≤ 23:00); meditasi/olahraga untuk menyalurkan overthinking.",
            "Keluar dari ruang tertutup: hadiri komunitas, bagikan riset Anda, minta masukan.",
            "Tulis setiap keputusan & alasannya — dokumentasi menyelamatkan Anda dari penyesalan.",
        ],
        "saran": "Percaya intuisi, tapi tetap cek fakta sebelum bertindak — dan jangan berjalan sendirian.",
    },
    "正官": {
        "tema": "tahun jabatan, reputasi, dan aturan. Dunia 'formal' sedang memperhatikan Anda.",
        "peluang": {
            "karier": "Peluang naik jabatan, penugasan resmi, dan pengakuan profesional terbuka lebar. Nilai Anda sedang 'terbaca' oleh pimpinan.",
            "keuangan": "Keuangan meningkat seiring karier; tunjangan dan penghasilan tetap menguat.",
            "asmara": "Hubungan serius menguat; yang lajang berpeluang bertemu pasangan lewat lingkungan kerja/formal.",
            "kesehatan": "Disiplin hidup yang Anda jalankan menopang kebugaran.",
            "studi": "Cocok untuk ujian kedinasan, sertifikasi profesi, dan jenjang akademik yang terstruktur.",
        },
        "risiko": {
            "karier": "Beban tanggung jawab bertambah berat: target tinggi, jam kerja panjang, dan politik kantor. Waspadai fitnah jabatan dan 'teman' yang menjatuhkan di belakang; kesalahan kecil bisa dibesar-besarkan hingga berujung sanksi, demosi, atau PHK.",
            "keuangan": "Pengeluaran mengikuti gengsi jabatan (mobil, jamuan, gaya hidup) bisa menggerus tabungan. Waspadai gratifikasi yang berbau pelanggaran.",
            "asmara": "Jadwal padat membuat rumah tangga diabaikan; pasangan bisa merasa ditinggalkan. Hubungan dengan bawahan/rekan lawan jenis perlu batas tegas.",
            "kesehatan": "Stres, tekanan darah tinggi, asam lambung, dan sakit kepala tegang — penyakit 'orang sibuk' yang sering diabaikan sampai parah.",
            "studi": "Belajar terburu-buru karena kesibukan; ujian bisa gagal karena kurang persiapan, bukan karena kemampuan.",
        },
        "risiko_utama": "Tekanan jabatan, fitnah, dan kesehatan yang dikorbankan demi karier — jaga keseimbangan.",
        "penangkal": [
            "Dokumentasikan setiap pekerjaan (email, laporan, Cc atasan) — bukti adalah perisai terbaik melawan fitnah.",
            "Patuhi aturan secara ketat; jangan sekali pun menerima gratifikasi atau 'jalan pintas'.",
            "Kelola stres: olahraga rutin, cukup tidur, dan jadwalkan waktu keluarga sebagai prioritas tetap.",
            "Cek tekanan darah & asam lambung secara berkala; jangan menunda kontrol kesehatan.",
            "Batasi hubungan kerja dengan lawan jenis di luar konteks profesional.",
        ],
        "saran": "Jaga nama baik dan patuhi aturan; disiplin adalah kunci — tetapi jangan korbankan kesehatan dan keluarga.",
    },
    "七杀": {
        "tema": "tahun tantangan, tekanan, dan persaingan. Medan pertempuran sedang terbuka.",
        "peluang": {
            "karier": "Kinerja di bawah tekanan luar biasa dihargai: peluang promosi cepat, menang dalam persaingan sengit, dan menaklukkan proyek yang ditakuti orang lain.",
            "keuangan": "Berani mengambil peluang besar bisa membawa pendapatan melonjak; bonus dan komisi tinggi menggiurkan.",
            "asmara": "Daya tarik 'pemimpin' Anda kuat; hubungan bisa menjadi lebih intens dan berapi-api.",
            "kesehatan": "Adrenalin membuat Anda kuat menahan beban — modal mental untuk melewati masa sulit.",
            "studi": "Target ambisius bisa tercapai jika dikerjakan dengan organisasi ketat.",
        },
        "risiko": {
            "karier": "Tahun paling rawan konflik terbuka: persaingan tidak sehat, atasan yang memusuhi, ancaman demosi atau PHK. Keputusan cepat di bawah tekanan berisiko salah besar dan disesali.",
            "keuangan": "Kerugian mendadak bisa terjadi: aset rusak, penipuan, atau utang yang membebani. Jangan mengambil pinjaman besar tahun ini.",
            "asmara": "Pertengkaran hebat dan perpisahan mengancam; ego dua belah pihak bisa menghancurkan hubungan yang sebenarnya baik. Waspadai kekerasan verbal.",
            "kesehatan": "PALING RAWAN: kecelakaan, cedera, patah tulang, luka sayat, kecelakaan berkendara, dan penyakit mendadak. Operasi non-darurat sebaiknya dihindari di periode 冲/刑.",
            "studi": "Tekanan ujian bisa memicu blunder; jawaban terburu-buru, salah baca soal, dan kehilangan fokus.",
        },
        "risiko_utama": "Bahaya fisik (kecelakaan/luka), konflik terbuka, dan kerugian mendadak — tahun yang menuntut kewaspadaan ekstra.",
        "penangkal": [
            "Keselamatan nomor satu: patuhi rambu, jangan berkendara dengan emosi atau lelah, hindari olahraga ekstrem dan perjalanan malam sendirian.",
            "Lakukan medical check-up menyeluruh; tangani gejala kecil sebelum menjadi besar.",
            "Jangan ambil keputusan besar saat emosi memuncak — tunda 24 jam sebelum menandatangani apa pun.",
            "Salurkan agresivitas lewat olahraga teratur (lari, bela diri, angkat beban) agar tidak meledak ke orang sekitar.",
            "Hindari konfrontasi di tempat kerja; kendalikan lidah; pilih berunding daripada melawan.",
            "Perkuat unsur 喜用 Anda (warna/angka/arah) dan lakukan amal/sedekah — secara tradisional menenangkan energi 七杀.",
        ],
        "saran": "Hadapi tantangan dengan kepala dingin, jaga keselamatan fisik, dan jangan pernah mengambil keputusan dalam keadaan marah.",
    },
    "正财": {
        "tema": "tahun rezeki utama: gaji, usaha, dan hasil kerja keras. Energi uang sedang mengalir.",
        "peluang": {
            "karier": "Kinerja dihargai: kenaikan gaji, bonus, target tercapai, dan ekspansi usaha berjalan lancar.",
            "keuangan": "Keuangan membaik nyata — waktu tepat menabung, investasi aman, dan melunasi utang. Arus kas positif.",
            "asmara": "Hubungan stabil dan kokoh; bagi pria energi 'istri' positif — cocok menikah atau memperkuat rumah tangga.",
            "kesehatan": "Kondisi fisik baik; tubuh merespons pola hidup yang teratur.",
            "studi": "Disiplin belajar membuahkan nilai bagus dan jenjang akademik yang jelas.",
        },
        "risiko": {
            "karier": "Kesuksesan membuat Anda dianggap 'sumber uang' oleh rekan: sering dimintai bantuan, dititipi tanggung jawab orang lain, sampai dibebani kerja ekstra tanpa imbalan.",
            "keuangan": "Pengeluaran gaya hidup ikut naik bersama penghasilan (makan di luar, gadget, gengsi). Utang konsumtif dan cicilan bisa menggerus sampai terlilit; jangan pinjamkan uang dalam jumlah besar — risikonya tak kembali dan merusak hubungan.",
            "asmara": "Pasangan bisa merasa nilai Anda diukur dari uang; komunikasi yang dangkal memicu jarak emosional.",
            "kesehatan": "Pola makan saat perayaan — kolesterol, asam urat, dan obesitas mengintai di akhir tahun.",
            "studi": "Terlalu sibuk mencari penghasilan membuat waktu belajar terabaikan.",
        },
        "risiko_utama": "Gaya hidup ikut naik & orang lain menganggap Anda 'atm berjalan' — jaga arus kas dan batas diri.",
        "penangkal": [
            "Sisihkan tabungan & investasi di awal bulan (min. 20%), sebelum pengeluaran lain.",
            "Tetapkan batas tegas: jangan meminjamkan uang yang Anda butuhkan; tolak dengan sopan.",
            "Catat pengeluaran harian; waspadai cicilan baru yang 'kecil-kecil tapi banyak'.",
            "Batasi perayaan: jaga porsi makan, kurangi alkohol, periksa kolesterol & asam urat.",
            "Jadwalkan quality time tanpa bahasan uang bersama pasangan.",
        ],
        "saran": "Kerja keras Anda akan dibayar — kelola pemasukan dengan bijak dan jangan biarkan gengsi menguras rekening.",
    },
    "偏财": {
        "tema": "tahun rezeki sampingan: bisnis, peluang besar, dan kejutan finansial.",
        "peluang": {
            "karier": "Peluang usaha sampingan, proyek besar, dan tawaran menggiurkan bermunculan. Karisma bisnis Anda naik; orang mudah percaya pada Anda.",
            "keuangan": "Potensi untung besar dari bisnis, komisi, dan investasi yang dikelola baik — cuan berlipat sangat mungkin.",
            "asmara": "Karisma meningkat, banyak perhatian; yang lajang mudah menarik pasangan.",
            "kesehatan": "Energi sosial yang tinggi membuat Anda aktif dan bersemangat.",
            "studi": "Cocok untuk beasiswa, kompetisi, dan lomba bergengsi — nama Anda bisa mencuat.",
        },
        "risiko": {
            "karier": "Godaan 'jalan pintas' menguat: proyek ilegal, suap, atau kerja sama dengan pihak tak jelas. Reputasi bisa hancur dalam semalam.",
            "keuangan": "RISIKO TERBESAR: penipuan investasi, judi, spekulasi berisiko tinggi, dan kerugian besar karena serakah. Uang cepat masuk juga cepat keluar; hutang piutang bisa berantakan.",
            "asmara": "Godaan selingkuh dan perhatian dari pihak ketiga sangat kuat; keharmonisan rumah tangga bisa goyah karena kesibukan dan kedekatan baru.",
            "kesehatan": "Pola hidup hura-hura: alkohol, kurang tidur, makan berlebihan — hati dan metabolisme terbebani.",
            "studi": "Mudah teralihkan oleh tawaran uang cepat; fokus akademik bisa hancur.",
        },
        "risiko_utama": "Serakah = bumerang: penipuan, spekulasi, dan godaan di luar komitmen — pasang batas sebelum bermain.",
        "penangkal": [
            "Tetapkan batas kerugian (stop-loss) SEBELUM memulai investasi/bisnis; jangan pernah mempertaruhkan dana darurat.",
            "Cek legalitas semua tawaran (ijin OJK/Kemenkumham); jangan percaya 'jaminan untung' apa pun bentuknya.",
            "Pisahkan uang bisnis dan uang keluarga; catat semua transaksi.",
            "Jaga komitmen: batasi kedekatan dengan lawan jenis, perkuat komunikasi pasangan, jangan sembunyikan aktivitas.",
            "Batasi alkohol dan pesta; tidur cukup; jaga pola makan.",
            "Jika rezeki besar datang, sisihkan 30% untuk tabungan & amal sebelum membelanjakan sisanya.",
        ],
        "saran": "Tangkap peluang besar, tapi pasang batas kerugian dan jaga komitmen — serakah adalah awal kehancuran.",
    },
    "比肩": {
        "tema": "tahun kemandirian, persaingan, dan teman. Energi 'sesama' sedang kuat.",
        "peluang": {
            "karier": "Kemandirian menguat: cocok membangun usaha sendiri, freelance, atau mengambil peran pemimpin tim. Saingan membuat Anda lebih tajam.",
            "keuangan": "Penghasilan dari kerja mandiri dan usaha pribadi bisa melonjak.",
            "asmara": "Hubungan setara dan saling menghargai; waktu baik mempertegas komitmen.",
            "kesehatan": "Cukup baik — tubuh kuat menahan aktivitas padat.",
            "studi": "Belajar mandiri sangat efektif; kelompok belajar yang sehat saling menguatkan.",
        },
        "risiko": {
            "karier": "Persaingan tidak sehat: rekan berebut posisi, proyek disabotase halus, dan hasil kerja diklaim orang lain — kerugian nyata bagi karier Anda. Ego membuat Anda sulit bekerja sama dan berisiko ditinggalkan tim.",
            "keuangan": "Pengeluaran untuk relasi membengkak (traktiran, sumbangan, pinjaman teman yang tak kembali). Menjadi penjamin utang orang lain adalah jebakan terbesar.",
            "asmara": "Ego dan gengsi memicu pertengkaran; sulit mengalah membuat masalah kecil membesar. Waspadai persaingan dengan pasangan.",
            "kesehatan": "Kelelahan karena terlalu banyak aktivitas sosial; tubuh dipaksa terus 'on'.",
            "studi": "Terlalu yakin diri: malas bertanya, mengabaikan bimbingan, dan nilai terkoreksi karena kesombongan.",
        },
        "risiko_utama": "Ego & gengsi: konflik rekan, jadi penjamin utang, dan pertengkaran karena harga diri.",
        "penangkal": [
            "JANGAN menjadi penjamin/pemberi pinjaman untuk teman tahun ini — tolak dengan sopan dan tegas.",
            "Pisahkan uang pribadi, uang usaha, dan urusan pertemanan; catat setiap transaksi.",
            "Latih mengalah: pilih menang dalam hubungan daripada menang dalam argumen.",
            "Kurangi acara yang menguras energi; tidur cukup; tahu kapan harus pulang.",
            "Di tempat kerja: akui kontribusi orang lain dan minta pengakuan Anda secara tertulis (email/report).",
        ],
        "saran": "Berdiri di atas kaki sendiri, tapi jaga relasi — menang sendirian tidak ada artinya jika kehilangan orang-orang terdekat.",
    },
    "劫财": {
        "tema": "tahun pengeluaran tak terduga dan relasi yang menguras. Berhati-hatilah dengan 'teman'.",
        "peluang": {
            "karier": "Jaringan Anda meluas; semangat dan keberanian tinggi untuk memulai hal baru.",
            "keuangan": "Bantuan teman dan koneksi bisa membuka pintu rezeki (referensi kerja, order, informasi lowongan).",
            "asmara": "Kehidupan sosial ramai; keberanian menyatakan perasaan meningkat.",
            "kesehatan": "Energi fisik cenderung tinggi; semangat juang kuat untuk aktivitas dan olahraga — asal dijaga keteraturannya.",
            "studi": "Kerja kelompok bisa mempercepat pemahaman materi.",
        },
        "risiko": {
            "karier": "Rezeki ada tetapi cepat bocor; mitra 'teman' bisa bermasalah — janji palsu, proyek mangkrak, atau mengambil porsi hasil lebih besar. Waspadai pengkhianatan rekan.",
            "keuangan": "TAHUN PALING RAWAN BOCOR: uang hilang, dicuri, ditipu, dipinjam tak kembali, atau hilang karena pengeluaran impulsif. Rekening bisa terkuras tanpa disadari.",
            "asmara": "PIHAK KETIGA MENGANCAM: godaan selingkuh, orang lain ikut campur rumah tangga, dan perselingkuhan pasangan — rumah tangga rawan retak bahkan cerai.",
            "kesehatan": "Pencernaan terganggu, kecenderungan alkohol berlebih, dan cedera kecil karena kecerobohan.",
            "studi": "Ajakan teman menggoyahkan fokus; bolos, begadang, dan gengsi sosial merusak target.",
        },
        "risiko_utama": "Bocornya uang (ditipu/dicuri/dipinjam) & pihak ketiga dalam asmara — tahun paling harus menjaga batas.",
        "penangkal": [
            "Catat setiap rupiah; kurangi membawa uang tunai besar; kunci aset dan dokumen penting.",
            "Jangan pernah meminjamkan uang; jangan tanda tangan apa pun sebagai penjamin.",
            "Perkuat komunikasi dengan pasangan: transparansi jadwal, hindari rahasia, pertegas batas dengan lawan jenis.",
            "Hindari alkohol dan judi; batasi 'traktiran' dan pengeluaran impulsif.",
            "Konsultasikan semua investasi/kerja sama dengan pihak yang benar-benar netral.",
            "Perkuat unsur 喜用 (warna/angka/arah) dan beramal secara teratur untuk menstabilkan energi.",
        ],
        "saran": "Disiplin anggaran, jaga batas pertemanan, dan pegang erat komitmen — jangan biarkan orang lain menguras apa yang Anda bangun.",
    },
    "食神": {
        "tema": "tahun kreativitas, karya, dan kenikmatan hidup. Rezeki datang dari bakat.",
        "peluang": {
            "karier": "Cocok meluncurkan produk, karya seni, konten, atau inovasi — hasil kerja Anda diapresiasi publik. Karier kreatif bersinar.",
            "keuangan": "Rezeki mengalir dari karya dan keahlian; usaha kuliner, seni, dan konten kreatif sangat menguntungkan.",
            "asmara": "Suasana hangat dan romantis; waktu terbaik quality time, lamaran, atau mempererat ikatan.",
            "kesehatan": "Energi positif dan kreatif — pemulihan cepat.",
            "studi": "Belajar terasa ringan; hasilkan karya tulis/proyek yang bisa dipamerkan dan dinilai.",
        },
        "risiko": {
            "karier": "Karya Anda berisiko ditiru, dibajak, atau diklaim orang lain tanpa izin. Terlalu santai ('nanti saja') membuat peluang besar lewat di depan mata.",
            "keuangan": "Nafsu makan dan gaya hidup 'menikmati hidup' menguras: makan di luar, hobi mahal, dan pembelian impulsif 'self reward'.",
            "asmara": "Terlalu nyaman bisa terkesan tidak serius; pasangan mungkin merasa kurang diperjuangkan.",
            "kesehatan": "Berat badan naik, kolesterol, gula darah, dan asam urat — kenikmatan kuliner adalah musuh terbesar tahun ini.",
            "studi": "Kemalasan manis: menunda tugas, mengerjakan seadanya, dan puas dengan nilai pas-pasan.",
        },
        "risiko_utama": "Karya dibajak/diklaim orang lain & pola makan 'menikmati hidup' yang menggerus kesehatan.",
        "penangkal": [
            "Daftarkan kekayaan intelektual (HAKI/merek) untuk karya Anda; simpan bukti proses kreatif.",
            "Tetap disiplin waktu: jadwal produksi ketat, jangan menunda ide yang sudah matang.",
            "Kendalikan porsi makan; kurangi gula & alkohol; olahraga teratur; pantau berat badan.",
            "Tetapkan anggaran 'kesenangan' bulanan agar kenikmatan tidak menjadi pemborosan.",
            "Tunjukkan keseriusan pada pasangan: rencana masa depan yang konkret.",
        ],
        "saran": "Salurkan kreativitas, lindungi karya Anda, dan jangan biarkan kenikmatan hidup menguasai kesehatan dan tabungan.",
    },
    "伤官": {
        "tema": "tahun bakat, inovasi, dan keinginan bebas. Energi 'membongkar' sedang aktif.",
        "peluang": {
            "karier": "Ide cemerlang bertebaran — lomba, karya ilmiah, inovasi produk, dan proyek kreatif berpeluang besar meraih pengakuan.",
            "keuangan": "Pendapatan dari bakat dan keterampilan khusus bisa sangat baik; tawaran proyek berdatangan.",
            "asmara": "Daya tarik kuat dan percakapan hidup; hubungan bergairah.",
            "kesehatan": "Energi muda yang tinggi untuk aktivitas fisik dan olahraga baru — tubuh merespons dengan baik selama dijaga keteraturannya.",
            "studi": "Kreativitas tinggi: cocok olimpiade, lomba karya tulis, dan penelitian inovatif.",
        },
        "risiko": {
            "karier": "PALING RAWAN KONFLIK DENGAN ATASAN/ATURAN: kritik pedas, surat peringatan, demosi, bahkan kehilangan pekerjaan. Pernyataan publik yang 'blak-blakan' bisa menjadi senjata makan tuan.",
            "keuangan": "Pendapatan besar tapi gaya hidup boros; risiko denda, denda pajak, atau biaya hukum karena kelalaian administrasi.",
            "asmara": "Emosi naik-turun; kata-kata tajam bisa melukai pasangan — risiko putus/cerai karena ucapan, bukan karena perasaan hilang.",
            "kesehatan": "Gangguan tenggorokan (suara, amandel), kulit (jerawat/eksim), dan kecenderungan begadang yang merusak imun.",
            "studi": "Kritik terhadap dosen/pembimbing bisa berbalik: nilai dihambat, proyek dihentikan, atau tuduhan pelanggaran.",
        },
        "risiko_utama": "Lidah adalah pedang: konflik dengan otoritas (SP/demosi/PHK), perkataan melukai pasangan, dan risiko hukum.",
        "penangkal": [
            "Kendalikan lidah: sampaikan kritik secara tertulis (email yang sopan), bukan di forum atau media sosial.",
            "Jangan pernah berkomentar negatif tentang atasan di depan kolega — bisa kembali sebagai bumerang.",
            "Dokumentasikan semua komunikasi kerja; jaga administrasi & pajak tetap rapi.",
            "Jangan mengambil keputusan emosional untuk mengundurkan diri/menikah/cerai dalam keadaan marah.",
            "Jaga tenggorokan & kulit; tidur sebelum jam 23:00; hindari begadang beruntun.",
            "Salurkan energi 'membongkar' lewat karya: tulis kritik membangun, buat karya inovatif, bukan konfrontasi.",
        ],
        "saran": "Salurkan energi lewat karya, kendalikan lidah, dan jangan pernah berperang dengan aturan saat emosi memuncak.",
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
# PENANGKAL (agar bahaya batal terjadi)
# ---------------------------------------------------------------------------

def penangkal_flags(flags: list) -> list:
    """Penangkal khusus interaksi tahun (冲/刑/害/空亡/桃花)."""
    out = []
    for f in flags:
        if f.startswith("冲"):
            out.append("Energi 冲 (benturan) → tunda keputusan besar di periode cabang bentrok: "
                       "pindah rumah, menikah, operasi non-darurat, tanda tangan kontrak besar. "
                       "Redam dengan perkuatan unsur 喜用 Anda.")
        elif "刑" in f:
            out.append("Energi 刑 (hukuman) → hindari konfrontasi hukum dan perkara; periksa "
                       "kontrak & dokumen dua kali; jaga kesehatan ekstra.")
        elif "害" in f:
            out.append("Energi 害 (gangguan) → waspada fitnah dan orang dekat yang diam-diam "
                       "merugikan; jangan bercerita terlalu terbuka; simpan bukti transaksi.")
        elif "空亡" in f:
            out.append("Kena 空亡 (cabang kosong) → jangan mengejar hasil instan di bidang yang "
                       "'kosong'; bereskan urusan lama yang menggantung; perkuat bidang unsur 喜用.")
        elif "桃花" in f:
            out.append("桃花 aktif (bunga cinta) → jaga komitmen dan komunikasi dengan pasangan; "
                       "hindari kedekatan ambigu; batasi hubungan yang tidak jelas arahnya.")
    return out


def penangkal_elemen(chart: Chart) -> list:
    """Penangkal berbasis unsur keberuntungan (喜用): warna/angka/arah."""
    out = []
    for el in chart.favorable:
        luck = element_lucky(el)
        out.append(f"Perkuat unsur {el} ({ELEMENT_NAME[el]}): warna {luck['color']}, "
                   f"angka {luck['number']}, arah {luck['direction']}.")
    return out


def penangkal_umum(score: int) -> list:
    if score >= 70:
        return ["Tahun positif — kunci keberhasilannya: tetap disiplin, jangan jemawa, dan "
                "sisihkan sebagian rezeki untuk tabungan & amal agar keberuntungan bertahan."]
    if score <= 44:
        return ["Tahun berat — kunci keselamatannya: kurangi ekspansi, perbanyak cadangan dana, "
                "jaga kesehatan preventif, dan jangan mengambil keputusan besar di bawah tekanan."]
    return ["Tahun campuran — jalani dengan tenang: catat pengeluaran, jaga pola tidur, dan "
            "selesaikan satu prioritas dalam satu waktu."]


# ---------------------------------------------------------------------------
# UTILITAS FORMAT
# ---------------------------------------------------------------------------

def bar(value: float, total: float, width: int = 18) -> str:
    ratio = value / total if total else 0
    filled = int(round(ratio * width))
    return "█" * filled + "░" * (width - filled)


def wlen(s: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)


def pad(s, width: int) -> str:
    return s + " " * max(0, width - wlen(str(s)))


def line(char: str = "-", width: int = 72) -> str:
    return char * width


def center(text: str, width: int = 72, fill: str = "=") -> str:
    p = max(0, width - len(text))
    left = p // 2
    return fill * left + text + fill * (p - left)


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
    """流年 dengan narasi LENGKAP & LUGAS: peluang, risiko, penangkal, saran."""
    s = []
    s.append(f"  Rentang: {year_from}-{year_to} (usia {year_from - chart.birth.year}–"
             f"{year_to - chart.birth.year} tahun). Skor 0-100; semakin tinggi semakin baik.")
    s.append("")
    ASPEK = ["karier", "keuangan", "asmara", "kesehatan", "studi"]
    for ln in lns:
        shio = SHIO[BRANCHES.index(ln.branch)]
        s.append(f"  {line('-', 68)}")
        s.append(f"  {ln.year} — {ln.gan_zhi} ({ELEMENT_NAME[ln.stem_element]} "
                 f"{ln.stem_element}, shio {shio}) — usia {ln.age} th — "
                 f"SKOR {ln.score}/100 — {ln.grade}")
        info = TEN_GOD_YEAR.get(ln.ten_god_stem)
        if info:
            s.append(f"  Tema besar : {info['tema']}")
            s.append("  - PELUANG & KEBAIKAN:")
            for k in ASPEK:
                s.append(f"      {k.capitalize():<9}: {info['peluang'][k]}")
            s.append("  ! RISIKO & TANDA BAHAYA (jangan diabaikan):")
            for k in ASPEK:
                s.append(f"      {k.capitalize():<9}: {info['risiko'][k]}")
            s.append("  # PENANGKAL (agar bahaya batal terjadi):")
            for p in info["penangkal"]:
                s.append(f"      - {p}")
            pn_flags = penangkal_flags(ln.flags)
            if pn_flags:
                s.append("  # Penangkal khusus interaksi tahun ini:")
                for p in pn_flags:
                    s.append(f"      - {p}")
            s.append(f"  - Saran     : {info['saran']}")
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
        "    Uraian risiko di atas adalah peringatan simbolis agar Anda lebih waspada —\n"
        "    bukan vonis. Dengan sikap hati-hati dan penangkal yang dijalankan, sebagian\n"
        "    besar 'bahaya' dapat dibatalkan.\n"
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