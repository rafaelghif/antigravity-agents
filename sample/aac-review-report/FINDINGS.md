<div align="center">

# 🛰️ Antigravity Agent Core — Findings & Fix Report

**Security review · bug triage · cross-platform fixes**

[![Security](https://img.shields.io/badge/Security-Passed-2ea44f?logo=shieldsdotio&logoColor=white)](#-keamanan)
[![Bugs Fixed](https://img.shields.io/badge/Bugs_Fixed-6-blue?logo=bugatti&logoColor=white)](#-bug-ditemukan--diperbaiki)
[![Tests](https://img.shields.io/badge/Tests-22%2F22-brightgreen?logo=pytest&logoColor=white)](#-status-akhir)
[![Platform](https://img.shields.io/badge/Platform-Windows_11-0078D6?logo=windows&logoColor=white)](#)
[![Maturity](https://img.shields.io/badge/Upstream-Early_Stage-orange?logo=github&logoColor=white)](#)

<sub>Reviewer: <b>SURIOTA</b> — PT Surya Inovasi Prioritas · 📅 2026-06-16</sub>

</div>

---

## 📑 Daftar Isi

- [🎯 Ringkasan Eksekutif](#-ringkasan-eksekutif)
- [🔒 Keamanan](#-keamanan)
- [🐛 Bug Ditemukan & Diperbaiki](#-bug-ditemukan--diperbaiki)
- [📝 Temuan Lain](#-temuan-lain)
- [💸 Penilaian Klaim "Hemat 80%"](#-penilaian-klaim-hemat-80)
- [📂 File yang Dimodifikasi](#-file-yang-dimodifikasi)
- [✅ Status Akhir](#-status-akhir)
- [🧭 Rekomendasi](#-rekomendasi)

---

## 🎯 Ringkasan Eksekutif

> [!NOTE]
> **AAC** adalah framework *agent workspace protocol* (**Shell ~71%** + **Python ~28%**)
> yang mengklaim menghemat **hingga 80% biaya token** via *model-side prompt caching*,
> plus *module locking*, validasi, dan automasi Git.

| Aspek | Verdict | Catatan |
|:------|:-------:|:--------|
| 🔒 **Keamanan** | ✅ **AMAN** | Tanpa exfiltrasi, `curl\|bash` tersembunyi, atau koneksi pihak ketiga |
| 🧪 **Fungsional** | ✅ **100%** | 22/22 test lulus *setelah* perbaikan |
| 🪟 **Windows (bawaan)** | ⚠️ **GAGAL** | Installer & beberapa modul crash; butuh 6 fix |
| 📈 **Kematangan** | 🔸 **Early-stage** | 1 ⭐, 1 author, tanpa CI Windows |

---

## 🔒 Keamanan

> [!TIP]
> **Hasil: bersih.** Tidak ditemukan satupun indikator berbahaya.

- ✅ **Tidak ada exfiltrasi kredensial** — API key hanya dikirim ke SDK *resmi* Google/OpenAI.
- ✅ **Tidak ada `curl | bash`** tersembunyi, `base64 -d`, atau reverse shell.
- ✅ **`.gitignore` otomatis** menutup `api_keys`, `active_api_keys`, `git_profiles`.
- ✅ Satu-satunya network call: `git fetch origin` (mode batch, timeout 5 s).

> [!CAUTION]
> Minor — `eval` / `shell=True` dipakai untuk menjalankan command linter/test/build
> dari config. *Aman di repo sendiri*, **berisiko di repo yang confignya tak dipercaya.**

---

## 🐛 Bug Ditemukan & Diperbaiki

<div align="center">

| # | Severity | Lokasi | Dampak | Status |
|:-:|:--------:|:-------|:-------|:------:|
| 1 | 🔴 **Blocker** | `bootstrap.sh:38,57` | `CYAN: unbound variable` saat *non-TTY* → gagal di **semua OS** | ✅ |
| 2 | 🔴 **Blocker** | `bootstrap.sh:163` | `mkdir` ketinggalan → `No such file or directory` (**semua OS**) | ✅ |
| 3 | 🟠 **High** | `docs-sync/main.py:200` | `re.error: bad escape \U` — path Windows di `re.sub` | ✅ |
| 4 | 🟠 **High** | `doctor.py`, `api-rotator/main.py` | `WinError 193` — exec `.sh` langsung | ✅ |
| 5 | 🟡 **Med** | `test_skill_*` | `WinError 193` — exec `.py` by-path tanpa interpreter | ✅ |
| 6 | 🟡 **Med** | `test_clean_command.py` | Assertion `/` vs `os.path.join` `\` | ✅ |

</div>

<details>
<summary><b>🔧 Detail patch (klik untuk membuka diff)</b></summary>

### Bug 1 — `CYAN` unbound variable
`set -euo pipefail` + `CYAN` dipakai di banner tapi tak pernah didefinisikan.
Saat output di-*pipe* (`curl | bash`), blok `tput` dilewati → `set -u` abort.

```diff
- RED=''  GREEN=''  YELLOW=''  BLUE=''  BOLD=''  NC=''
+ RED=''  GREEN=''  YELLOW=''  BLUE=''  CYAN=''  BOLD=''  NC=''
+         CYAN='\033[0;36m'
```

### Bug 2 — `mkdir` block ketinggalan *(compile drift)*
`bootstrap.sh` (auto-generated) **tidak sinkron** dengan isi repo terbaru.

```diff
+ mkdir -p .agents/skills/api-rotator/scripts
+ mkdir -p .agents/scripts/cli/commands
```

### Bug 3 — `bad escape \U` di docs-sync
String `replacement` berisi path Windows `C:\Users\...`; `re.sub` menafsirkan `\U` sebagai escape.

```diff
- target_content = pattern.sub(replacement, target_content)
+ target_content = pattern.sub(lambda _m: replacement, target_content)
```

### Bug 4 — `WinError 193` (exec `.sh` langsung)
Windows tak bisa eksekusi `.sh` via `subprocess.run([script])`.

```diff
+ cmd = ["bash", validate_sh] if os.name == "nt" else [validate_sh]
+ proc = subprocess.run(cmd)
```

### Bug 5 — test exec `.py` by-path
```diff
- subprocess.run([self.script_path, "--help"], ...)
+ subprocess.run([sys.executable, self.script_path, "--help"], ...)
```

### Bug 6 — separator path di assertion
```diff
- mock_remove.assert_any_call("/mock/agents/locks/other.lock")
+ mock_remove.assert_any_call(os.path.join("/mock/agents", "locks", "other.lock"))
```

</details>

> [!IMPORTANT]
> Setelah fix *source*, `bootstrap.sh` di-**regenerate** via
> `scratch/compile_bootstrap.py` agar perbaikan ikut ter-*embed* ke installer.

---

## 📝 Temuan Lain

> [!WARNING]
> **Installer ship skill tidak lengkap.** Hanya **8 dari 11 skill** ter-package.
> `docs-sync`, `pr-scaffolder`, `adr-wizard` ada di repo + diuji test, tapi
> **tidak ikut ter-install** ke project user.

- 🧹 **Self-cleanup** — `bootstrap.sh` / `.ps1` menghapus dirinya sendiri setelah sukses *(normal)*.
- 🐧 **Arsitektur bash-centric** — wajib **Git Bash + Python di PATH** untuk Windows.

---

## 💸 Penilaian Klaim "Hemat 80%"

> [!NOTE]
> **Tidak ada benchmark/data** di repo yang membuktikan angka 80%.

- ✅ Desain caching **valid**: `AGENTS.md` memerintahkan baca file urut
  *Most Static → Most Dynamic* (`AGENTS → rules → schema → memory`).
- ⚠️ **Realita:** penghematan ~90% hanya berlaku pada **porsi konteks statis**
  (terukur **~6.835 token**). Prompt nyata didominasi file + diff *(dinamis,
  tak ter-cache)* → klaim *"80% dari total budget"* = **best-case marketing**.

> 📊 Angka lengkap → [`BENCHMARK_REPORT.md`](./BENCHMARK_REPORT.md)

---

## 📂 File yang Dimodifikasi

```text
bootstrap.sh                                  → Bug 1, 2 + regenerate
.agents/bootstrap.sh                          → copy hasil regenerate
.agents/skills/docs-sync/scripts/main.py      → Bug 3
.agents/scripts/cli/commands/doctor.py        → Bug 4
.agents/skills/api-rotator/scripts/main.py    → Bug 4
tests/test_skill_docs_sync.py                 → Bug 5
tests/test_skill_pr_scaffolder.py             → Bug 5
tests/test_clean_command.py                   → Bug 6
```

---

## ✅ Status Akhir

- [x] Review keamanan — **bersih**
- [x] Identifikasi 6 bug (2 blocker · 2 runtime Windows · 2 test)
- [x] Perbaiki seluruh bug
- [x] Regenerate installer
- [x] Verifikasi: **22/22 test** + clean install **EXIT 0**

---

## 🧭 Rekomendasi

1. 📚 **Layak dipelajari, belum layak produksi** *(khususnya Windows)*.
2. ⚡ Untuk hemat token nyata: setup CC Anda **sudah punya prompt caching bawaan**.
3. 🔀 Jika ingin kontribusi: PR 6 fix + CI matrix Windows + daftarkan 3 skill hilang.

---

<div align="center">
<sub>🛰️ <b>SURIOTA</b> · PT Surya Inovasi Prioritas · Internal Technical Review · 2026-06-16</sub>
</div>
