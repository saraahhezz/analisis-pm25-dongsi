# Analisis Kualitas Udara (PM2.5) Stasiun Dongsi, Beijing

Proyek analisis data: pola waktu dan pengaruh angin terhadap PM2.5, data per jam 1 Maret 2013 - 28 Februari 2017 (dataset PRSA, stasiun Dongsi).

## Pertanyaan Bisnis
1. Pada bulan dan jam berapa rata-rata PM2.5 tertinggi, dan berapa persen hari masuk tiap kategori kualitas udara di setiap periode Maret-Februari?
2. Bagaimana perbedaan rata-rata PM2.5 menurut kecepatan dan arah angin, dan kombinasi mana yang tertinggi?

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

## Menjalankan di Lokal
```bash
# 1) (opsional) buat virtual environment
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 2) pasang dependensi
pip install -r requirements.txt

# 3) jalankan dashboard
streamlit run dashboard/dashboard.py
```
`main_data.csv` sudah disertakan. Untuk membuatnya ulang, jalankan seluruh sel `notebook.ipynb` dari folder `submission` (perlu `jupyter`).

## Deploy ke Streamlit Community Cloud
1. Unggah folder `submission` ke repositori GitHub (publik).
2. Buka https://share.streamlit.io, pilih **Create app**, lalu pilih repositori dan branch.
3. Isi **Main file path** dengan `dashboard/dashboard.py`.
4. Setelah deploy berhasil, tempel tautan aplikasi ke `url.txt`.

`dashboard.py` membaca `main_data.csv` lewat path relatif terhadap file itu sendiri, sehingga aman dijalankan dari folder mana pun.

## Ringkasan Temuan
- PM2.5 konsisten lebih tinggi pada **Oktober-Maret** daripada April-September di keempat periode. Bulan terburuk berganti antar periode, jadi yang stabil adalah pola musim, bukan satu bulan.
- Selisih musim terutama berasal dari **episode polusi berat yang lebih sering** di musim dingin; median PM2.5 hampir sama di semua musim.
- PM2.5 turun tajam seiring naiknya kecepatan angin; angin lemah (≤2 m/s) dari sektor Timur-Tenggara memberi peluang jam PM2.5 tinggi tertinggi.

## Teknik Analisis Lanjutan
*Manual grouping* dan *binning* (kategori kualitas udara harian, kelas kecepatan angin, kuadran arah angin, musim, blok waktu) dan matriks risiko angin. RFM dan geospasial **tidak dipakai** karena dataset tidak memiliki pelanggan maupun beberapa lokasi.

## Catatan dan Keterbatasan
- Titik batas kategori AQI (35/75/115/150/250) dan syarat minimal 20 jam valid per hari berasal dari ingatan terhadap standar China dan **perlu diverifikasi** ke dokumen resmi sebelum dikutip.
- Hasil adalah asosiasi dari satu stasiun dan empat tahun data, bukan bukti sebab-akibat.
