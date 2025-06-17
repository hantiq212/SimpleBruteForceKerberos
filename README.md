
# 🔐 AS-REP Roasting Full Chain

AS-REP Roasting adalah teknik serangan Kerberos yang memungkinkan attacker mendapatkan hash NTLM user **tanpa perlu login atau password**, selama user tersebut **tidak mengaktifkan pre-authentication**.

Script ini menjalankan seluruh proses roasting secara otomatis:
1. Kirim permintaan AS-REQ ke KDC
2. Ambil AS-REP response dari user yang vulnerable
3. Ekstrak hash
4. Crack hash menggunakan `hashcat`
5. Tampilkan hasilnya langsung

---

## 🚀 Fitur Utama

✅ Kompatibel dengan Impacket terbaru  
✅ Tidak memerlukan kredensial (pre-auth bypass)  
✅ Format hash langsung kompatibel dengan hashcat  
✅ Crack otomatis + tampilkan hasil (`--show`)  
✅ Output disimpan ke file `asrep_hashes.txt`  

---

## 📦 Kebutuhan Sistem

- Python 3.8+
- Hashcat

### 🛠️ Instalasi dengan Virtual Environment (Direkomendasikan):

```bash
# 1. Buat dan aktifkan virtual environment
python3 -m venv venv
source ./venv/bin/activate

# 2. Install dependensi
python3 -m pip install -r requirements.txt

# 3. Install hashcat jika belum tersedia
sudo apt install hashcat
```

---

## 📁 Struktur File biar lebih mudah, tapi kalau ingin custom juga bisa

```
.
├── KerberosBrute.py     # script utama
├── requirements.txt       # dependensi Python
├── userlist.txt           # daftar user target (1 per baris)
└── rockyou.txt            # wordlist untuk hashcat
```

---

## ✍️ Contoh Isi `userlist.txt`

```
admin
labuser
test123
```

---

## ▶️ Cara Menjalankan

```bash
python3 asrep_fullchain.py <DOMAIN> <KDC_IP> <USERLIST.TXT> <WORDLIST.TXT>
```

### Contoh:

```bash
python3 asrep_fullchain.py domain.local 192.168.1.10 userlist.txt rockyou.txt
```

---

## 📤 Output

### ✅ File Hash (asrep_hashes.txt)

```
$krb5asrep$23$admin@domain.local:4c40c57dbac79b3b...$a7ac...
```

### ✅ Password yang Berhasil Ditemukan

Setelah proses cracking selesai:

```
$krb5asrep$23$admin@domain.local:...:SuperSecret123
```

---

## 💡 Tips

- Coba wordlist lokal yang lebih spesifik dari target (nama, tanggal, pola umum).
- Jalankan di mesin dengan GPU agar cracking lebih cepat.
- Gunakan opsi tambahan `hashcat` jika perlu: `--status`, `--session`, dll.

---

## ❗ Legal Disclaimer

> 🛡️ This tool is for **educational purposes** and **authorized security testing only**.  
> Do **NOT** use against systems you don't own or don't have explicit permission to test.

---

## 👨‍💻 Credits

Script dibuat oleh hantiq untuk keperluan bootcamp & edukasi  
Menggunakan [Impacket](https://github.com/fortra/impacket) & [Hashcat](https://hashcat.net/hashcat/)
