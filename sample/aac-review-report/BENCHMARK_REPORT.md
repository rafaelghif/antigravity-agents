<div align="center">

# 📊 Antigravity Agent Core — Benchmark Report

**Functional · installation · caching benchmarks**

[![Test Suite](https://img.shields.io/badge/Test_Suite-22%2F22_(100%25)-2ea44f?logo=pytest&logoColor=white)](#-a--benchmark-fungsional--test-suite-resmi)
[![Clean Install](https://img.shields.io/badge/Clean_Install-EXIT_0-2ea44f?logo=gnubash&logoColor=white)](#-b--benchmark-instalasi--clean-run)
[![Static Context](https://img.shields.io/badge/Static_Context-~6835_tokens-blue?logo=anthropic&logoColor=white)](#-c--verifikasi-klaim-caching-hemat-80)
[![Claim 80%](https://img.shields.io/badge/Claim_80%25-Unverified-orange?logo=target&logoColor=white)](#c4-verdict-klaim)
[![Codex Live](https://img.shields.io/badge/Codex-75.0s_·_total_252.5k-412991?logo=openai&logoColor=white)](#-d--live-agent-benchmark--codex-vs-claude-code)
[![Claude Live](https://img.shields.io/badge/Claude_Code-34.4s_·_%240.52-D97757?logo=anthropic&logoColor=white)](#-d--live-agent-benchmark--codex-vs-claude-code)

<sub>Reviewer: <b>SURIOTA</b> · 📅 2026-06-16 · 🪟 Windows 11 · 🐚 Git Bash · 🐍 Python 3.13</sub>

</div>

---

> [!NOTE]
> **Metodologi.** AAC **tidak menyertakan harness benchmark**. Laporan ini mengukur
> **3 dimensi terverifikasi**: (A) fungsional, (B) instalasi, (C) caching. Benchmark
> A/B token nyata *tidak dijalankan* karena butuh API call berbayar + logging token
> aktual; sebagai gantinya disajikan **matematika caching dari ukuran nyata**.

---

## 📑 Daftar Isi

- [🧪 A · Benchmark Fungsional](#-a--benchmark-fungsional--test-suite-resmi)
- [🚀 B · Benchmark Instalasi](#-b--benchmark-instalasi--clean-run)
- [💾 C · Verifikasi Klaim Caching](#-c--verifikasi-klaim-caching-hemat-80)
- [🤖 D · Live Agent Benchmark — Codex vs Claude Code](#-d--live-agent-benchmark--codex-vs-claude-code)
- [🏁 E · Skoring Akhir](#-e--skoring-akhir)
- [🔁 F · Reproduksi](#-f--reproduksi)

---

## 🧪 A · Benchmark Fungsional — Test Suite Resmi

<div align="center">

| Kondisi | ✅ Pass | ❌ Fail | 📈 Pass Rate |
|:--------|:------:|:------:|:-----------:|
| **Sebelum perbaikan** | 17 | 5 | `77%` |
| **Sesudah perbaikan** | **22** | **0** | **`100%`** 🎉 |

</div>

**Progres perbaikan:** `17` → `20` → **`22`**

<details>
<summary><b>📋 Detail 5 kegagalan awal (semua Windows-specific)</b></summary>

| Test | Error | Akar masalah |
|:-----|:------|:-------------|
| `test_clean_command_execution` | `AssertionError: remove(...) not found` | assertion `/` vs `os.path.join` `\` |
| `docs_sync::test_help_execution` | `WinError 193` | exec `.py` by-path |
| `docs_sync::test_docstring_sync_execution` | `WinError 193` → `bad escape \U` | exec by-path + regex path Windows |
| `docs_sync::test_autodetect_mode` | `WinError 193` | exec `.py` by-path |
| `pr_scaffolder::test_help_execution` | `WinError 193` | exec `.py` by-path |

</details>

---

## 🚀 B · Benchmark Instalasi — Clean Run

> Simulasi `curl … | bash` (*non-interaktif / non-TTY*) di repo dummy bersih.

<div align="center">

| Kondisi | Hasil | Catatan |
|:--------|:-----:|:--------|
| **Sebelum** | ❌ **GAGAL** | 3 bug blocking → butuh patch manual |
| **Sesudah** | ✅ **EXIT 0** | 0 WinError · 0 unbound var · semua dir dibuat |

</div>

```text
[PASS] Git repository initialized.
[PASS] pre-commit / post-commit / commit-msg Git hook installed & executable.
[PASS] helper.sh / recon.sh / validate.sh executable.
Doctor diagnostics: FOUND 1 WARNING   ← validate.sh berjalan benar (bukan crash)
```

> [!TIP]
> `1 WARNING` = hasil validasi **sah** pada repo dummy minimal, **bukan** error eksekusi.

---

## 💾 C · Verifikasi Klaim Caching "Hemat 80%"

### C.1 · Konteks Statis Terukur

<div align="center">

| File | Words | Bytes | ~Tokens |
|:-----|------:|------:|--------:|
| `AGENTS.md` | 2.587 | 19.799 | **~4.949** |
| `.agents/rules/project_rules.md` | 700 | 5.297 | ~1.324 |
| `.agents/memory.md` | 247 | 1.912 | ~478 |
| `.agents/schema.md` | 39 | 339 | ~84 |
| **TOTAL** | | | **🎯 ~6.835** |

</div>

### C.2 · Validitas Desain

> [!NOTE]
> `AGENTS.md` memerintahkan urutan baca **Most Static → Most Dynamic**
> (`AGENTS → rules → schema → memory`) — teknik *prefix caching* yang **benar secara teknis**.

### C.3 · Matematika Penghematan *(Anthropic prompt caching)*

- Token *cache-read* ≈ **10%** harga input normal.
- Sesi **30 turn**, konteks protokol **~6.835 token**:

```text
Tanpa cache : 30 × 6.835            ≈ 205.000 token
Dengan cache: 6.835 + (29 × 684)    ≈  26.600 token
                                    ───────────────────
Hemat pada konteks statis           ≈  ~87%
```

### C.4 · Verdict Klaim

<div align="center">

| Klaim | Status |
|:------|:------:|
| Caching hemat ~90% pada konteks statis | ✅ **Benar** |
| *"Hemat 80% dari TOTAL API budget"* | ❌ **Tidak terbukti** |
| AAC *unik* menghasilkan penghematan ini | ⚠️ **Tidak** (fitur model, bukan eksklusif AAC) |

</div>

> [!WARNING]
> Total prompt nyata **didominasi file + diff dinamis** yang tak ter-cache.
> Angka **80%** adalah *best-case marketing*, bukan hasil terukur.

---

## 🤖 D · Live Agent Benchmark — Codex vs Claude Code

> [!TIP]
> **Benchmark agentik nyata — keduanya dijalankan headless & terisolasi.** Bug AAC #3
> (`re.error: bad escape \U`) direproduksi di repro minimal identik (`buggy.py` +
> `test_buggy.py`, pytest **RED**). Prompt yang **sama persis** diberikan ke
> Claude Code (`claude -p`, model Opus) dan Codex (`codex exec`, model gpt-5.5).

<div align="center">

| Metrik | 🤖 Claude Code (Opus 4.8) | 🟢 Codex (gpt-5.5) |
|:-------|:-------------------------:|:------------------:|
| **Hasil** | ✅ 1 passed | ✅ 1 passed |
| **Fix** | `lambda _match: replacement` | `lambda _match: replacement` |
| **Percobaan** | 1 | 1 |
| **⏱️ Waktu** | **34.4 s** *(api 22.2 s)* | **75.0 s** |
| **🔁 Turns / loop** | 5 turn | 1 turn *(9 shell cmd · 1 patch)* |
| **💵 Cost** | **$0.5176** *(diemit CLI)* | **~$0.38** *(est. dari token)* |
| **🎟️ Token fresh** *(non-cached)* | ~68.9k *(in 30.4k + cw 37.5k + out 958)* | ~44.3k *(in 42.1k + out 2.1k)* |
| **🎟️ Token cache-read** *(ditagih ~10%)* | 213.9k | 208.3k |
| **🎟️ Token total** | 282.836 | 252.516 |
| **Sentuh test?** | ❌ benar | ❌ benar |

</div>

```text
🤖 claude -p --model opus --output-format json --dangerously-skip-permissions
   read → diagnose → patch → pytest(GREEN) → done
   1 passed · 34.4s · 5 turns · $0.5176 · in 30.4k/out 958/cw 37.5k/cr 213.9k

🟢 codex exec --json --sandbox workspace-write (model gpt-5.5, reasoning high)
   intro → ls → read buggy+test → pytest(RED) → apply patch → pytest(GREEN) → report
   1 passed · 75.0s · 1 turn/9 cmd · in 42.1k/out 2.1k/cache-read 208.3k · total 252.5k
```

> [!WARNING]
> **Token apple-to-apple — KEDUANYA pakai cache-read berat.** Diukur dengan metrik
> sama (termasuk cache-read), total Codex **252.516** vs Claude **282.836** → **sebanding**,
> bukan "Codex 8× lebih ramping". Angka **34.181** di review lama hanya menghitung *fresh
> token* Codex (non-cached) sehingga menyesatkan. Cache-read ditagih ~10%, jadi biaya
> efektif keduanya didominasi *fresh token*: Claude ~68.9k vs Codex ~44.3k.

> [!IMPORTANT]
> **Parity korektif** — kedua agent mendiagnosis akar masalah identik & menghasilkan
> **fix yang sama persis** (`re.sub` callback). Kualitas **setara**; Claude **~2.2×
> lebih cepat** (34.4 s vs 75.0 s), tapi Codex **~27% lebih murah** ($0.38 vs $0.52).

<details>
<summary><b>💵 Estimasi cost Codex (CLI tak emit $, dihitung dari token usage)</b></summary>

Tarif **gpt-5.5** (standard, input 250.4k < 272k → bukan long-context 2×):
input `$5.00`/M · output `$30.00`/M · cached input `$0.50`/M *(diskon 90%)*.

```text
fresh input   42.135 × $5.00 /1M  = $0.210675
cache-read   208.256 × $0.50 /1M  = $0.104128
output         2.125 × $30.00/1M  = $0.063750
                                   ───────────
Estimasi cost Codex run            ≈ $0.3786  →  ~$0.38
```

Pembanding: Claude **$0.5176** (diemit CLI, aktual). Codex **~27% lebih murah**
pada task ini — meski **~2.2× lebih lambat**.
</details>

> [!CAUTION]
> Codex di Windows berjalan di *overlay sandbox* (`CodexSandboxOffline\.codex\.sandbox`)
> → warning `.pytest_cache: Access denied` *(WinError 5, benign)*. Headless **menggantung
> jika stdin tak ditutup** → wajib `'' | codex exec …`.

> 📊 Perbandingan fitur lengkap → [`COMPARISON.md`](./COMPARISON.md)

---

## 🏁 E · Skoring Akhir

<div align="center">

| Dimensi | Skor | Keterangan |
|:--------|:----:|:-----------|
| 🔒 Keamanan | `9/10` | Bersih; minor `eval`/`shell=True` |
| 🧪 Fungsional *(setelah fix)* | `10/10` | 22/22 test lulus |
| 🪟 Portabilitas Windows *(bawaan)* | `3/10` | Gagal out-of-the-box; perlu 6 fix |
| 🎯 Akurasi klaim | `4/10` | Caching valid, "80%" overstated |
| 📈 Kematangan proyek | `3/10` | 1 ⭐, no CI Windows, skill drift |
| 💡 Nilai konseptual | `8/10` | Pola `AGENTS.md` + cache ordering layak diadopsi |

</div>

> [!IMPORTANT]
> **Kesimpulan.** Konsep *solid & aman*, eksekusi *early-stage*. Setelah 6 perbaikan
> SURIOTA, tool berfungsi penuh & ter-install bersih di Windows. Klaim hemat token
> valid **hanya pada porsi konteks statis**, bukan total budget.

---

## 🔁 F · Reproduksi

```bash
# 1️⃣  Test suite
cd <repo> && python -m pytest tests/ -q          # → 22 passed

# 2️⃣  Regenerate installer setelah edit source
python scratch/compile_bootstrap.py

# 3️⃣  Clean install (sandbox)
mkdir sandbox && cd sandbox && git init && git commit --allow-empty -m init
cp <repo>/bootstrap.sh . && bash ./bootstrap.sh  # → EXIT 0
```

> [!NOTE]
> Artefak uji (`Desktop\aac-trial*`, `%TEMP%\aac-review`) sudah **dihapus** pasca-review.

---

<div align="center">
<sub>📊 <b>SURIOTA</b> · PT Surya Inovasi Prioritas · Internal Technical Review · 2026-06-16</sub>
</div>
