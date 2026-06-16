<div align="center">

# ⚖️ Agent CLI & Framework Comparison

**🤖 Claude Code** &nbsp;·&nbsp; **🟢 OpenAI Codex** &nbsp;·&nbsp; **🛰️ Antigravity Agent Core**

[![Claude Code](https://img.shields.io/badge/Claude_Code-Opus_4.8-D97757?logo=anthropic&logoColor=white)](#2--head-to-head-langsung-task-identik)
[![Codex](https://img.shields.io/badge/Codex-gpt--5.5-412991?logo=openai&logoColor=white)](#2--head-to-head-langsung-task-identik)
[![AAC](https://img.shields.io/badge/AAC-framework_layer-orange?logo=github&logoColor=white)](#3--posisi-aac-framework-bukan-agent)
[![Benchmark](https://img.shields.io/badge/Benchmark-Live_Tested-2ea44f?logo=githubactions&logoColor=white)](#2--head-to-head-langsung-task-identik)

<sub>📅 2026-06-16 · Basis: <a href="./FINDINGS.md">FINDINGS</a> + <a href="./BENCHMARK_REPORT.md">BENCHMARK</a> + run Codex live</sub>

</div>

---

> [!NOTE]
> **Konteks.** Claude Code & Codex = **agent CLI**. AAC = **framework layer** yang
> bisa duduk di atas agent CLI mana pun. Perbandingan dipecah jadi: (§2) head-to-head
> agent pada task identik, (§3) posisi AAC, (§4) matriks fitur, (§5) rekomendasi.

## 📑 Daftar Isi

- [1 · Ringkasan](#1--ringkasan)
- [2 · Head-to-Head Langsung (task identik)](#2--head-to-head-langsung-task-identik)
- [3 · Posisi AAC (framework, bukan agent)](#3--posisi-aac-framework-bukan-agent)
- [4 · Matriks Fitur 3-Arah](#4--matriks-fitur-3-arah)
- [5 · Rekomendasi Final](#-5--rekomendasi-final-untuk-suriota)

---

## 1 · Ringkasan

<div align="center">

| | 🤖 Claude Code | 🟢 Codex | 🛰️ AAC |
|:--|:-:|:-:|:-:|
| **Jenis** | Agent CLI | Agent CLI | Framework |
| **Model uji** | Opus 4.8 | gpt-5.5 | — |
| **Fix bug identik?** | ✅ | ✅ | n/a |
| **Caching otomatis** | ✅ | ✅ | Manual |
| **Sandbox eksekusi** | Permission mode | **Overlay sandbox** | — |
| **Cocok untuk Anda** | ✅ Primary | ✅ Secondary | ⚠️ Opsional |

</div>

---

## 2 · Head-to-Head Langsung (task identik)

> [!TIP]
> **Benchmark nyata, bukan spec.** Bug AAC #3 (`re.error: bad escape \U`) direproduksi
> dalam repro minimal + pytest gagal. Kedua agent diminta memperbaikinya.

<div align="center">

| Metrik | 🤖 Claude Code (Opus 4.8) | 🟢 Codex (gpt-5.5) |
|:-------|:-------------------------:|:------------------:|
| **Hasil** | ✅ test pass | ✅ test pass |
| **Fix dihasilkan** | `lambda _match: replacement` | `lambda _match: replacement` |
| **Percobaan** | 1 | 1 |
| **⏱️ Waktu** | **34.4 s** *(api 22.2 s)* | **75.0 s** |
| **🔁 Turns / loop** | 5 turn | 1 turn *(9 shell cmd · 1 patch)* |
| **💵 Cost** | **$0.5176** *(diemit CLI)* | **~$0.38** *(est. dari token)* |
| **🎟️ Token fresh** *(non-cached)* | ~68.9k *(in 30.4k + cw 37.5k + out 958)* | ~44.3k *(in 42.1k + out 2.1k)* |
| **🎟️ Token cache-read** *(ditagih ~10%)* | 213.9k | 208.3k |
| **🎟️ Token total** | 282.836 | 252.516 |
| **Sentuh file test?** | ❌ (benar) | ❌ (benar) |
| **Loop kerja** | read → diagnose → patch → verify | ls → read → pytest(RED) → patch → pytest(GREEN) |

</div>

> [!WARNING]
> **Token apple-to-apple — KEDUANYA cache-read berat.** Diukur metrik sama (termasuk
> cache-read), total Codex **252.516** vs Claude **282.836** → **sebanding**. Angka
> **34.181** di review lama menyesatkan: itu hanya *fresh token* Codex (non-cached),
> bukan total — kalau dibandingkan dengan total Claude jadi seolah "8× lebih ramping".
> Karena cache-read ditagih ~10%, biaya efektif keduanya didominasi *fresh token*:
> Claude ~68.9k vs Codex ~44.3k. Pembanding adil = **waktu, cost, & korektif**.

> [!IMPORTANT]
> **Parity korektif.** Keduanya mendiagnosis akar masalah persis sama (`re.sub`
> menafsirkan `\U` di replacement) dan menghasilkan **fix identik** — `re.sub`
> dengan callback. **Kualitas hasil setara**; Claude **~2.2× lebih cepat** (34.4 s vs 75.0 s),
> namun Codex **~27% lebih murah** (est. **$0.38** vs $0.5176).

> [!NOTE]
> **Estimasi cost Codex** (CLI tak emit $) — tarif `gpt-5.5` standard
> (input `$5/M`, output `$30/M`, cached `$0.50/M`):
> `42.1k×$5 + 208.3k×$0.50 + 2.1k×$30` (per 1M) = **$0.2107 + $0.1041 + $0.0638 ≈ $0.38**.
> Input 250.4k `<` 272k → bukan tarif long-context 2×.

<details>
<summary><b>🟢 Transkrip ringkas run Codex (live)</b></summary>

```text
model: gpt-5.5 · approval: never · sandbox: workspace-write · reasoning: high
1. intro message (rencana)
2. Get-ChildItem -Force (eksplor repo) + cek rg
3. Get-Content buggy.py + test_buggy.py
4. python -m pytest -q          → 1 failed (bad escape \U)   ← RED
5. apply patch: pattern.sub(lambda _match: replacement, ...)
6. python -m pytest -q          → 1 passed                   ← GREEN
1 turn · 9 shell cmd · 1 patch · wall 75.0s
tokens: fresh in 42.1k / out 2.1k · cache-read 208.3k · total 252.516
```

</details>

> [!CAUTION]
> **Catatan teknis Codex di Windows:** Codex menjalankan command di *overlay sandbox*
> (`C:\Users\CodexSandboxOffline\.codex\.sandbox\…`) sehingga muncul warning
> `.pytest_cache: Access is denied` *(WinError 5)* — **benign**, tak memengaruhi hasil.
> Mode headless juga **menggantung jika stdin tidak ditutup** (`'' | codex exec …`).

---

## 3 · Posisi AAC (framework, bukan agent)

> [!NOTE]
> AAC **tidak bersaing** dengan Claude Code / Codex — ia *layer protokol* di atasnya.

- 🛰️ Keuntungan caching AAC **sudah otomatis** di **kedua** agent CLI → redundan untuk hemat token.
- ✅ Nilai unik AAC tetap: **module locking**, **ADR terstruktur**, **token budget ledger**.
- ⚠️ Di Windows, AAC butuh **6 fix** (sudah kami patch) sebelum jalan.

---

## 4 · Matriks Fitur 3-Arah

<div align="center">

| Dimensi | 🤖 Claude Code | 🟢 Codex | 🛰️ AAC |
|:--------|:-------------:|:--------:|:------:|
| Prompt caching | ✅ Otomatis | ✅ Otomatis | 🔸 Manual |
| Memory lintas sesi | ✅ claude-mem | 🔸 session resume | 🔸 `memory.md` |
| Sub-agent / workflow | ✅ Kuat | 🔸 Terbatas | ❌ |
| Eksekusi tersandbox | 🔸 Permission mode | ✅ Overlay sandbox | ❌ |
| Skills / plugins | ✅ Puluhan | 🔸 mcp/plugin | 🔸 8 (3 hilang) |
| Code review headless | ✅ skill | ✅ `codex review` | 🔸 `validate.sh` |
| Module locking | ❌ | ❌ | ✅ |
| ADR / decision log | 🔸 manual | 🔸 manual | ✅ |
| Token budget tracker | ❌ | 🔸 tokens used | ✅ |
| Dukungan Windows | ✅ Native | ✅ Native | ⚠️ Perlu patch |
| Kematangan | ✅ Matang | ✅ Matang | 🔸 1 ⭐ |

<sub>✅ kuat/native · 🔸 ada tapi terbatas · ❌ tidak ada</sub>

</div>

---

## 🧭 5 · Rekomendasi Final untuk SURIOTA

> [!IMPORTANT]
> **Claude Code = primary, Codex = secondary/cross-check, AAC = ambil polanya saja.**

- [x] **Claude Code** sebagai agent utama — ekosistem skill/agent/MCP + memory terkuat.
- [x] **Codex** sebagai *second opinion* / cross-verifikasi — terbukti hasil setara pada
      task identik; *overlay sandbox*-nya bagus untuk eksekusi berisiko.
- [x] **AAC** — **jangan adopsi sebagai tool**; curi 4 polanya (lock, ADR, budget, AGENTS.md ordering).
- [ ] *(Opsional)* Kirim PR 6 fix AAC ke upstream.

> [!TIP]
> **Pola pakai bareng:** Claude Code untuk implementasi + orkestrasi, lalu
> `codex review` / `codex exec` untuk *adversarial second-pass* sebelum merge.

---

## 📎 Lampiran — Data Mentah

<div align="center">

| Item | Nilai |
|:-----|:------|
| 🟢 Codex versi | `0.139.0` · model `gpt-5.5` |
| 🟢 Codex run | `75.0 s` · 1 turn/9 cmd · fresh ~44.3k + cache-read 208.3k · total `252.516` · est. `~$0.38` · 1 pass |
| 🤖 Claude Code versi | `2.1.170` · model `claude-opus-4-8` |
| 🤖 Claude Code run | `34.4 s` · `$0.5176` · 5 turns · fresh ~68.9k + cache-read 213.9k · total `282.836` · 1 pass |
| 🛰️ AAC test (patched) | `22/22` · install `EXIT 0` |
| 🐛 Bug uji | AAC #3 — `re.error: bad escape \U` |
| 📦 Artefak mentah | [`raw-data/claude_run.json`](./raw-data/claude_run.json) · [`raw-data/codex_events.jsonl`](./raw-data/codex_events.jsonl) |

</div>

---

<div align="center">
<sub>⚖️ <b>SURIOTA</b> · PT Surya Inovasi Prioritas · Internal Technical Review · 2026-06-16</sub>
</div>
