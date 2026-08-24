# Panduan Pemasangan GitHub Profile OS — Rayhan

Paket ini dibuat khusus untuk repository profil:

`rayhanferdiansyah1-alt/rayhanferdiansyah1-alt`

## 1. Pasang seluruh file

Salin struktur berikut ke root repository profilmu:

```text
rayhanferdiansyah1-alt/
├── .github/
│   └── workflows/
│       └── profile-dashboard.yml
├── assets/
│   ├── banner.svg
│   └── live-dashboard.svg
├── scripts/
│   └── build_profile.py
└── README.md
```

Cara paling aman melalui Git:

```bash
git clone https://github.com/rayhanferdiansyah1-alt/rayhanferdiansyah1-alt.git
cd rayhanferdiansyah1-alt

# Salin isi paket ke folder ini, lalu:
git add README.md assets scripts .github
git commit -m "feat(profile): launch self-updating GitHub Profile OS"
git push origin main
```

Setelah push pertama, buka tab **Actions** → **Refresh profile dashboard** → **Run workflow**. Workflow akan memperbarui statistik setiap hari sekitar pukul **07.17 WIB**.

Jika workflow gagal menulis file, buka **Settings → Actions → General → Workflow permissions**, lalu pastikan workflow diizinkan menulis isi repository.

## 2. Perbaiki identitas profil

Gunakan konfigurasi ini pada **Settings → Public profile**:

| Bagian | Isi yang direkomendasikan |
|---|---|
| Name | `Rayhan Ferdiansyah Mardani` |
| Bio | `Systems Analyst • Data & Database • Laravel Builder | Turning complex operations into reliable digital systems.` |
| Location | `Karawang, West Java, Indonesia` |
| Time zone | `Asia/Jakarta` dan aktifkan tampilan waktu lokal |
| Status | `Building reliable systems ⚙️` |
| Website | URL portofolio setelah deployment |
| Social links | LinkedIn, portfolio, dan satu kanal kontak profesional |

Gunakan foto profil dengan wajah atau identitas yang terlihat jelas pada ukuran kecil. Foto sekarang memiliki suasana yang menarik, tetapi subjek terlalu jauh dan membelakangi kamera sehingga kurang kuat untuk personal branding profesional.

## 3. Susun ulang pinned repositories

Repo `wpu-git-test` sebaiknya **dilepas dari pin** karena nama dan deskripsinya menunjukkan repository latihan. Tidak perlu menghapusnya; cukup unpin atau archive jika sudah tidak digunakan.

Target akhir pin:

1. `portfolio` — tampilan terbaik dan tautan demo aktif.
2. `education-operations-platform` — sistem pendidikan multi-role.
3. `certificate-qr-verification` — generator sertifikat dan validasi QR.
4. `clinic-workforce-operations` — absensi, shift, cuti, lembur, dan payroll.
5. `sql-data-lab` — query, optimasi, desain skema, dan analisis data.
6. `system-analysis-blueprints` — ERD, LRS, use case, arsitektur, dan keputusan desain.

Jangan membuat enam repository kosong hanya agar pin terlihat penuh. Publikasikan bertahap dan pin hanya repository yang sudah memiliki bukti kerja.

## 4. Standar minimum setiap repository unggulan

Setiap repo yang dipin harus memiliki:

- nama yang bersih dan konsisten;
- satu kalimat deskripsi yang menjelaskan masalah dan hasil;
- minimal 5 topik repository yang relevan;
- README berisi masalah, aktor, fitur, arsitektur, instalasi, dan screenshot;
- gambar social preview;
- demo aktif atau GIF singkat jika memungkinkan;
- skema database atau diagram arsitektur;
- data demo yang aman;
- dokumentasi pengujian;
- lisensi yang sesuai.

## 5. Urutan peningkatan yang paling efektif

### Level 1 — Identity

Pasang paket profil, ubah nama lengkap, bio, foto, lokasi, dan tautan sosial.

### Level 2 — Proof

Rapikan repository Portfolio terlebih dahulu, lalu publikasikan satu case study sistem lengkap. Satu repository matang lebih bernilai daripada banyak repository setengah jadi.

### Level 3 — Authority

Tambahkan dokumentasi keputusan arsitektur, pengujian, data model, changelog, dan kontribusi open source. Di tahap ini profil tidak hanya terlihat bagus, tetapi membuktikan cara berpikirmu sebagai engineer.

## Catatan desain

README sengaja tidak memakai kumpulan trophy, animasi berlebihan, atau terlalu banyak kartu pihak ketiga. Pembeda utamanya adalah narasi engineering yang jelas dan dashboard statistik mandiri yang dihasilkan dari GitHub API. Hasilnya lebih profesional, ringan, dan tidak mudah rusak karena rate limit layanan statistik eksternal.
