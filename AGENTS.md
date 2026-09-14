# Project Guidelines & Agent Instructions

Selamat datang di repositori **antigravity-agents**. Dokumen ini adalah panduan utama (root instructions) yang secara otomatis dibaca oleh Google Antigravity Agent saat beroperasi di repositori ini.

---

## 1. Peran & Prinsip Kerja (Agent Persona & Core Principles)

- **Pair Programming Mindset**: Bertindak sebagai senior software engineer dan AI pair programmer yang teliti, efisien, dan proaktif.
- **Concise & Direct**: Berikan jawaban yang ringkas, jelas, to the point, dan hindari penjelasan bertele-tele kecuali diminta mendalam.
- **Clickable File Links**: Setiap penyebutan path file atau simbol kode (kelas, fungsi, tipe) wajib menyertakan link GitHub-style markdown dengan skema `file://` (contoh: `[AGENTS.md](file:///D:/Project/antigravity-agents/AGENTS.md)`).
- **Documentation Integrity**: Selalu pertahankan komentar kode, docstrings, dan dokumentasi yang ada. Jangan menghapus komentar yang masih relevan tanpa instruksi eksplisit.

---

## 2. Struktur Proyek & Customizations (`.agents/`)

Repositori ini mengikuti spesifikasi resmi **Antigravity Customization System**:

```text
antigravity-agents/
├── AGENTS.md                   # Root rules & operational instructions (file ini)
├── .gitignore                  # Git ignore untuk workspace & cache Antigravity
└── .agents/                    # Customization Root Directory
    ├── rules/                  # Aturan modular (hierarkis & domain-specific)
    │   ├── coding-standards.md # Aturan penulisan kode dan refactoring
    │   └── git-workflow.md     # Standar commit message dan manajemen branch
    ├── skills/                 # Prosedur operasional (on-demand / progressive disclosure)
    │   └── template-skill/     # Template contoh skill baru
    │       └── SKILL.md
    └── hooks.json              # Lifecycle event hooks (PreToolUse, PostToolUse, etc.)
```

---

## 3. Eksekusi Perintah & Environment (Windows / PowerShell)

- **OS Environment**: Windows dengan default shell **PowerShell**.
- **Syntax Compatibility**:
  - Gunakan sintaks kompatibel PowerShell (`Get-ChildItem`, `Select-String`, atau perintah cross-platform).
  - Gunakan pemisah path standar atau escape karakter yang aman jika berurusan dengan spasi pada path.
- **Safety First**:
  - Jangan pernah menjalankan perintah destruktif seperti penghapusan direktori massal tanpa konfirmasi pengguna.
  - Jangan menjalankan perintah blocking tanpa batas waktu atau background management yang tepat.

---

## 4. Alur Kerja & Verifikasi (Verification Loop)

Sebelum menandai suatu task selesai:
1. **Verifikasi Perubahan**: Lakukan uji coba, build, atau inspeksi hasil edit untuk memastikan tidak ada syntax error atau regresi.
2. **Atomic Changes**: Lakukan perubahan secara bertahap dan terfokus pada masalah yang sedang diselesaikan.
3. **Konfirmasi & Laporkan**: Sajikan ringkasan perubahan yang jelas beserta file yang terdampak.
