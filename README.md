# Analisis Kualitas Udara (PM2.5) Stasiun Dongsi, Beijing

Proyek analisis data: pola waktu dan pengaruh angin terhadap PM2.5, data per jam 1 Maret 2013 - 28 Februari 2017 (dataset PRSA, stasiun Dongsi).

## Pertanyaan Bisnis
1. Selama periode Maret 2013 – Februari 2017, pada bulan dan jam berapa rata-rata PM2.5 di stasiun Dongsi paling tinggi, dan berapa persen hari yang masuk tiap kategori kualitas udara di setiap periode Maret–Februari?
2. Selama periode Maret 2013 – Februari 2017, bagaimana perbedaan rata-rata PM2.5 menurut kecepatan angin dan arah angin, dan kombinasi mana yang menghasilkan PM2.5 tertinggi?

## Struktur Direktori
```
submission
├───dashboard
| ├───main_data.csv        # data bersih (keluaran notebook)
| └───dashboard.py
├───data
| └───PRSA_Data_Dongsi_20130301-20170228.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Lingkungan yang Diuji
- **Python 3.12 dan 3.13** (minimal **Python 3.11**, karena pandas 3.0, numpy 2.4, dan streamlit 1.66 mensyaratkan Python 3.11 ke atas).
- Versi library dipatok pada `requirements.txt` dan diuji pada virtual environment bersih (dashboard pada Python 3.12 dan 3.13; notebook pada Python 3.13): pandas 3.0.2, numpy 2.4.4, matplotlib 3.10.8, seaborn 0.13.2, streamlit 1.66.1.
- **Google Colab:** notebook memakai paket bawaan Colab, bukan `requirements.txt`. Notebook juga diuji pada pandas 2.2.2 dan numpy 2.0.2 (Python 3.12) dan menghasilkan data bersih yang sama (selisih hanya pembulatan floating-point ±1e-14).
- `requirements.txt` hanya mematok library. Versi Python tidak dapat dipatok melalui berkas ini, sehingga dicatat di sini.

Periksa versi di lingkungan Anda dengan `python --version` dan `pip freeze` (di Colab: `!python --version` dan `!pip list`).

## Menjalankan di Lokal
```bash
# 1) buat virtual environment (disarankan)
python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2) pasang dependensi
pip install -r requirements.txt

# 3) jalankan dashboard
streamlit run dashboard/dashboard.py
```
`main_data.csv` sudah disertakan. Untuk membuatnya ulang, jalankan seluruh sel `notebook.ipynb` (perlu `jupyter`; di luar `requirements.txt` karena hanya dipakai untuk notebook).

## Deploy ke Streamlit Community Cloud
1. Unggah isi folder `submission` ke repositori GitHub publik (`requirements.txt` harus berada di root repositori).
2. Buka https://share.streamlit.io, pilih **Create app**, lalu pilih repositori dan branch.
3. Isi **Main file path** dengan `dashboard/dashboard.py`.
4. Jika build gagal karena versi Python, pilih Python 3.12 pada pengaturan lanjutan (*Advanced settings*) saat membuat aplikasi.
5. Setelah deploy berhasil, tempel tautan aplikasi ke `url.txt`.

`dashboard.py` membaca `main_data.csv` melalui path relatif terhadap file itu sendiri, sehingga dapat dijalankan dari folder mana pun.

## Ringkasan Temuan
- PM2.5 konsisten lebih tinggi pada **Oktober–Maret** daripada April–September di keempat periode. Bulan terburuk berganti antar periode, sehingga yang stabil adalah pola musim, bukan satu bulan.
- Selisih musim terutama berasal dari **episode polusi berat yang lebih sering** di musim dingin; median PM2.5 hampir sama di semua musim.
- PM2.5 turun tajam seiring naiknya kecepatan angin; angin lemah (≤2 m/s) dari sektor Timur-Tenggara memberi peluang jam PM2.5 tinggi tertinggi.

## Teknik Analisis Lanjutan
*Manual grouping* dan *binning* (kategori kualitas udara harian, kelas kecepatan angin, kuadran arah angin, musim, blok waktu) serta matriks risiko angin. RFM dan geospasial tidak digunakan karena dataset tidak memiliki pelanggan maupun beberapa lokasi.

## Sumber Standar
- Kementerian Perlindungan Lingkungan Hidup RRT. (2012). *HJ 633—2012 Technical Regulation on Ambient Air Quality Index (on trial)*, Tabel 1 dan 2 (titik batas dan kategori).
- Standar Nasional RRT. (2012). *GB 3095—2012 Ambient Air Quality Standards*, Tabel 1 (batas PM2.5 24 jam) dan Tabel 4 (minimal 20 jam data per hari).

Tautan lengkap tercantum pada notebook, bagian EDA Pertanyaan 1.

## Batasan
- Kategori kualitas udara ditentukan dari sub-indeks PM2.5 saja (bukan AQI gabungan) dengan titik batas HJ 633—2012; standar tersebut telah digantikan oleh HJ 633—2026.
- Hasil merupakan asosiasi dari satu stasiun dan empat tahun data, bukan bukti sebab-akibat.
