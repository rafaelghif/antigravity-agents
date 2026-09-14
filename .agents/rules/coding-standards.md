# Coding Standards & Quality Guidelines

Aturan ini berlaku saat melakukan penulisan, modifikasi, atau refactoring kode di repositori ini.

---

## 1. Kualitas Kode (Code Quality)

- **Simplicity & Readability**: Kode harus mudah dipahami, memiliki penamaan variabel/fungsi yang jelas dan bermakna (intention-revealing).
- **Single Responsibility Principle (SRP)**: Setiap fungsi atau modul harus memiliki satu tanggung jawab utama.
- **Fail Fast & Graceful Error Handling**: Validasi input di awal fungsi dan tangani error dengan jelas tanpa membiarkan exception tersembunyi (*swallowing exceptions*).

---

## 2. Integritas Kode & Dokumentasi

- **Preserve Existing Docs**: Jangan menghapus komentar fungsional, lisensi, atau docstrings yang sudah ada.
- **Self-Documenting Code**: Utamakan kode yang mengekspresikan maksudnya sendiri; tambahkan komentar pada logika kompleks, edge cases, atau *non-obvious rationale*.

---

## 3. Tool Calling & File Modifications

- Saat melakukan edit file, utamakan penggantian blok terkecil yang presisi (*targeted replacement*).
- Hindari penulisan ulang seluruh file jika perubahan hanya menyangkut beberapa baris.
- Pastikan indentation, trailing comma, dan formatting konsisten dengan style yang sudah ada di file terkait.
