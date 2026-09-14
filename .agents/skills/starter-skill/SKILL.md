---
name: starter-skill
description: >-
  Provides a standard workflow template for performing tasks and validations
  in this project. Use when introducing new features, scripts, or operational procedures.
---

# Starter Skill Template

Dokumen ini adalah contoh implementasi resmi Antigravity Skill. Skill berfungsi sebagai runbook atau SOP berorientasi langkah (step-by-step procedure) yang hanya dibaca secara mendalam oleh model ketika relevan (*Progressive Disclosure*).

---

## Prosedur Kerja

1. **Persiapan & Analisis Kebutuhan**:
   - Telusuri konteks file terkait sebelum membuat modifikasi.
   - Periksa apakah ada dependensi eksternal yang dibutuhkan.

2. **Eksekusi**:
   - Jalankan script atau perintah yang diperlukan.
   - Buat file atau edit kode sesuai spesifikasi.

3. **Verifikasi & Testing**:
   - Jalankan linter atau test suite untuk memastikan tidak ada regresi:
     ```powershell
     # Contoh: verifikasi status git atau eksekusi test
     git status
     ```

---

## Praktik Terbaik (Skill Best Practices)

- **Third-Person Description**: Deskripsi pada frontmatter wajib menggunakan sudut pandang orang ketiga dan menjelaskan secara spesifik *kapan* skill ini harus dipicu.
- **Progressive Disclosure**: Jangan memuat seluruh dokumentasi tebal di `SKILL.md`. Taruh file referensi panjang di folder `references/` dan buat link ke file tersebut.
- **Executable Helpers**: Taruh script bantuan di folder `scripts/`.
