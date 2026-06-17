# Antigravity Agent Core: Layman User Guide & Onboarding Manual 🚀

Selamat datang di **Antigravity Agent Core (AAC)**! Panduan ini dirancang khusus untuk membantu pengembang dan pengguna awam memahami cara menggunakan Agent AI, melakukan *prompting*, mengelola autentikasi, serta memahami mekanisme otomatis rotasi kunci API dan profil Git.

---

## 1. Apa itu Antigravity Agent Core & `antigravity-cli`?

* **Antigravity Agent Core (AAC)** adalah struktur workspace dan aturan protokol pengkodean (terkumpul di folder `.agents/`) yang membuat Agent AI (seperti Gemini atau OpenAI) bekerja secara disiplin, aman, dan hemat token di dalam folder proyek Anda.
* **`antigravity-cli` (diakses dengan perintah `agy`)** adalah program CLI utama yang terpasang di komputer Anda. Perintah ini bertindak sebagai pembungkus (*wrapper*) untuk memicu Agent AI, mengelola sesi, dan menghubungkan komputer lokal Anda ke server Agent.
* **Helper Script (`.\.agents\scripts\helper.ps1` untuk Windows atau `./.agents/scripts/helper.sh` untuk Linux/macOS)** adalah skrip lokal di dalam repositori Anda yang digunakan untuk menjalankan perintah-perintah repositori seperti manajemen issue, mengunci modul, validasi kode, commit, dan push. Perintah repositori lokal dijalankan lewat skrip helper ini, bukan lewat perintah global `agy`.

---

## 2. Cara Masuk & Autentikasi Sesi (`agy auth`)

Sebelum bisa menggunakan Agent AI, Anda harus masuk (*log in*) terlebih dahulu menggunakan akun Anda. Ada dua cara masuk tergantung pada lingkungan terminal Anda:

### A. Masuk di Komputer Lokal (Browser & Keyring OS)
Jika Anda menggunakan laptop atau komputer lokal secara langsung:
1. Ketik perintah **`agy`** di terminal Anda.
2. Jika Anda belum masuk, sistem akan **secara otomatis membuka web browser default** Anda.
3. Masuk menggunakan akun terdaftar Anda di halaman browser.
4. Setelah berhasil, browser akan menyimpan kunci sesi (*session token*) Anda secara aman di **Keyring bawaan sistem operasi** Anda:
   * **Windows**: Windows Credential Manager
   * **macOS**: Apple Keychain
   * **Linux**: Secret Service API (melalui dbus)
5. **Silent Sign-In**: Selanjutnya, setiap kali Anda mengetik `agy`, sistem akan langsung mendeteksi kunci di Keyring secara senyap tanpa perlu membuka browser lagi.

### B. Masuk Lewat Koneksi SSH (Remote Server)
Jika Anda mengoperasikan server jarak jauh lewat SSH (di mana browser tidak bisa dibuka otomatis):
1. Jalankan perintah **`agy`** di terminal SSH remote Anda.
2. CLI akan mendeteksi koneksi SSH dan mencetak sebuah **URL otorisasi unik** yang aman di terminal.
3. **Salin URL tersebut**, lalu buka dan jalankan di web browser di laptop lokal Anda.
4. Selesaikan login di browser Anda. Browser akan menampilkan **Authorization Code** (kode alfanumerik unik).
5. **Salin kode alfanumerik** tersebut, kembali ke terminal SSH Anda, tempel (*paste*) kode ke dalam input prompt, dan tekan Enter.

### C. Cara Keluar Sesi (*Logging Out*)
Jika Anda ingin mengganti akun atau menghapus kredensial tersimpan dari komputer:
* Cukup ketik perintah berikut di dalam kotak chatbox Agent CLI Anda:
  ```bash
  /logout
  ```
* Ini akan menghapus token sesi dari Keyring OS Anda dan membersihkan folder cache lokal secara instan.

---

## 3. Bagaimana Cara Menggunakan Agent & Prompting?

Setelah berhasil masuk, Anda dapat langsung berinteraksi dengan Agent AI melalui chatbox `agy`.

### A. Alur Kerja Menulis Fitur / Memperbaiki Bug
Untuk menjaga kebersihan kode utama (`main` branch) dan memastikan semua perubahan aman, Agent AI mengikuti alur **Issue-Driven Development** (Pengembangan Berbasis Masalah) secara otomatis.

> [!NOTE]
> Jalankan perintah lokal di bawah ini menggunakan `./.agents/scripts/helper.sh` (Linux/macOS) atau `.\.agents\scripts\helper.ps1` (Windows PowerShell).

1. **Membuat Issue**: Anda atau Agent membuat issue untuk mendaftarkan tugas baru:
   ```bash
   ./.agents/scripts/helper.sh issue create "Membuat skema database inventory" "Deskripsi detail..."
   ```
2. **Pindah Branch**: Agent berpindah ke branch terisolasi agar kode utama tidak terganggu:
   ```bash
   ./.agents/scripts/helper.sh issue checkout <nomor_issue>
   ```
3. **Penguncian Folder (Locking)**: Agent mengunci folder kerja untuk mencegah tabrakan kode dengan proses lain:
   ```bash
   ./.agents/scripts/helper.sh lock <nama_folder>
   ```
4. **Menulis Kode & Validasi**: Agent menulis kode, lalu melakukan pengecekan kualitas otomatis dengan perintah:
   ```bash
   ./.agents/scripts/helper.sh validate
   ```
5. **Penggabungan Kode (Merge)**: Jika semua tes lulus, Agent menggabungkan kembali kodenya ke branch utama:
   ```bash
   ./.agents/scripts/helper.sh issue merge <nomor_issue>
   ```

### B. Tips Prompting bagi Pemula
* **Fokus pada Satu Tugas**: Mintalah Agent untuk melakukan satu hal dalam satu waktu (misal: *"buatkan unit test untuk fitur login saja"*).
* **Gunakan Context yang Jelas**: Sebutkan nama file atau fungsi secara spesifik (contoh: *"lihat berkas [helper.py](file://./.agents/scripts/cli/helper.py) dan tambahkan error handling"*).
* **Gunakan Fitur `/grill-me`**: Jika Anda bingung menentukan struktur desain atau skema database, ketik **/grill-me** di chatbox. Agent akan mewawancarai Anda secara interaktif untuk memilih solusi terbaik.

---

## 4. Mekanisme Rotasi Kunci API (LLM)

Saat melakukan prompting yang sangat sering, Anda bisa terkena pembatasan kuota gratis atau *Rate Limit* (HTTP 429). Antigravity mengatasi hal ini secara otomatis.

### A. Bagaimana Cara Mengaktifkan Auto-Rotate Kunci API?
Anda dapat mendaftarkan beberapa kunci API cadangan (baik dari akun Google Gemini atau OpenAI lainnya) agar sistem dapat berganti kunci secara otomatis ketika kunci utama limit.

1. Buka file konfigurasi lokal di folder [.agents/api_keys](file://./../.agents/api_keys).
2. Tulis beberapa profil berbeda dengan format `nama_profil.GEMINI_API_KEY=nilai_kunci`, contoh:
   ```ini
   # Akun Utama
   utama.GEMINI_API_KEY=AIzaSy_kunci_satu
   utama.OPENAI_API_KEY=sk-proj-kunci_openai_satu
   
   # Akun Cadangan
   cadangan.GEMINI_API_KEY=AIzaSy_kunci_dua
   cadangan.OPENAI_API_KEY=sk-proj-kunci_openai_dua
   ```
3. Simpan file tersebut.

### B. Alur Rotasi Otomatis (Auto-Rotate)
Saat Anda sedang mengetik di chatbox `agy` dan kunci API Anda habis limit:
1. Sistem CLI mendeteksi error *Rate Limit* dari server AI.
2. Tanpa menghentikan chat Anda, CLI secara otomatis memutar profil aktif ke kunci cadangan berikutnya.
3. CLI langsung mengulang pengiriman prompt Anda secara transparan.

### C. Alur Rotasi Manual (Manual Rotate)
Jika Anda ingin mengganti akun API secara sengaja:
* **Lewat CLI**: Jalankan perintah berikut di terminal (gunakan `./.agents/scripts/helper.sh` atau `.\.agents\scripts\helper.ps1` sesuai OS):
  ```bash
  ./.agents/scripts/helper.sh api-profile rotate
  ```
  Atau langsung pilih nama profil tertentu:
  ```bash
  ./.agents/scripts/helper.sh api-profile cadangan
  ```
* **Lewat Dashboard Menu**: Jalankan skrip helper tanpa argumen untuk membuka menu dashboard:
  ```bash
  ./.agents/scripts/helper.sh menu
  ```
  Pilih nomor **`7`** (**Manage API profiles and keys**), lalu pilih profil yang ingin Anda aktifkan.

---

## 5. Mekanisme Rotasi Profil Git

Selain kunci API, Agent juga dapat memutar profil Git (Username, Email, dan SSH Key) agar identitas pembuat komit (*commit author*) tetap sesuai dengan akun yang Anda gunakan untuk repositori publik maupun privat.

### A. Konfigurasi Profil Git
Tulis profil Git Anda di file [.agents/git_profiles](file://./../.agents/git_profiles), contoh:
```ini
kerja.name=Nama Kantor
kerja.email=work@company.com
kerja.ssh_key=~/.ssh/id_rsa_work

pribadi.name=Nama Asli Anda
pribadi.email=personal@gmail.com
pribadi.ssh_key=~/.ssh/id_rsa_personal
```

### B. Cara Kerja Rotasi Git
* **Rotasi Saat Commit**: Setiap kali Anda atau Agent menjalankan perintah `agy commit` untuk menyimpan perubahan, sistem akan memutar konfigurasi lokal repositori (`git config user.name`/`user.email`) ke profil berikutnya secara bergantian (*round-robin*).
* **Rotasi Saat Sync Issue**: Jika Agent gagal melakukan sinkronisasi issue ke GitLab/Gitea karena masalah hak akses token, sistem akan mendeteksinya dan langsung memutar profil aktif ke akun cadangan berikutnya untuk mencoba kembali sinkronisasi.
