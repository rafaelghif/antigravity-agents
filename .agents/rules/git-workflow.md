# Git Workflow & Commit Guidelines

Aturan ini memandu standarisasi riwayat git dan integrasi kode di repositori ini.

---

## 1. Conventional Commits

Gunakan format commit pesan standar:
- `feat: <deskripsi singkat>`: Fitur baru
- `fix: <deskripsi singkat>`: Perbaikan bug
- `docs: <deskripsi singkat>`: Perubahan dokumentasi
- `refactor: <deskripsi singkat>`: Restrukturisasi kode tanpa mengubah fungsionalitas
- `chore: <deskripsi singkat>`: Tugas maintenance, build script, konfigurasi
- `test: <deskripsi singkat>`: Penambahan atau perbaikan unit/integration tests

---

## 2. Atomic Commits

- Buat commit yang bersifat atomik (satu commit menyelesaikan satu konteks logika).
- Hindari mencampuradukkan perubahan format (beautify) dengan perubahan logika bisnis dalam satu commit yang sama.
- Pastikan repository selalu dalam keadaan dapat di-build dan dites pada setiap commit.
