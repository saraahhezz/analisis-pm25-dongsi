import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="PM2.5 Dongsi, Beijing", page_icon="🌫️", layout="wide")
sns.set_theme(style="whitegrid", rc={"axes.grid.axis": "y"})

# Path dibuat relatif terhadap file ini agar jalan di lokal maupun Streamlit Cloud
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

NAMA_BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
URUT_ANGIN = ["≤1 (sangat lemah)", "1-2 (lemah)", "2-3 (sedang)", "3-5 (cukup kuat)", ">5 (kuat)"]
URUT_KUADRAN = ["Utara-Timur Laut", "Timur-Tenggara", "Selatan-Barat Daya", "Barat-Barat Laut"]
URUT_MUSIM = ["Semi", "Panas", "Gugur", "Dingin"]
BATAS_KAT = [0, 35, 75, 115, 150, 250, np.inf]
NAMA_KAT = ["Baik sekali (≤35)", "Baik (35-75)", "Ringan (75-115)", "Sedang (115-150)",
            "Berat (150-250)", "Sangat berat (>250)"]
WARNA_KAT = ["#2E8B57", "#9BCB6A", "#F4D03F", "#E67E22", "#C0392B", "#6C1D2E"]
TEKS_KAT = ["white", "#222", "#222", "white", "white", "white"]
MIN_JAM_HARIAN = 20
MIN_N_SEL = 100


@st.cache_data
def muat_data():
    df = pd.read_csv(os.path.join(BASE_DIR, "main_data.csv"), parse_dates=["datetime", "tanggal"])
    df["kelas_angin"] = pd.Categorical(df["kelas_angin"], categories=URUT_ANGIN, ordered=True)
    df["kuadran"] = pd.Categorical(df["kuadran"], categories=URUT_KUADRAN, ordered=True)
    return df


df = muat_data()

# ---------------- Sidebar: filter ----------------
st.sidebar.header("Filter")
tgl_min, tgl_max = df["tanggal"].min().date(), df["tanggal"].max().date()
rentang = st.sidebar.date_input("Rentang tanggal", value=(tgl_min, tgl_max), min_value=tgl_min, max_value=tgl_max)
musim_pilih = st.sidebar.multiselect("Musim", URUT_MUSIM, default=URUT_MUSIM)
batas = st.sidebar.slider("Ambang PM2.5 (µg/m³) untuk indikator 'tinggi'", 35, 150, 75, step=5,
                          help="Default 75 µg/m³ = batas harian Tingkat II standar China (perlu diverifikasi ke dokumen resmi).")

if isinstance(rentang, tuple) and len(rentang) == 2:
    awal, akhir = rentang
else:
    awal, akhir = tgl_min, tgl_max

f = df[(df["tanggal"].dt.date >= awal) & (df["tanggal"].dt.date <= akhir) & (df["musim"].isin(musim_pilih))]

st.title("🌫️ Kualitas Udara (PM2.5) Stasiun Dongsi, Beijing")
st.caption("Data per jam, 1 Mar 2013 - 28 Feb 2017 (dataset PRSA). Hasil bersifat asosiasi dari satu stasiun, bukan bukti sebab-akibat.")

if f["PM2.5"].dropna().empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Ubah rentang tanggal atau musim.")
    st.stop()

# ---------------- KPI ----------------
harian = (f.groupby("tanggal").agg(pm25=("PM2.5", "mean"), n=("PM2.5", "count"))
            .query("n >= @MIN_JAM_HARIAN"))
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rata-rata PM2.5", f"{f['PM2.5'].mean():.1f} µg/m³")
c2.metric("Median PM2.5", f"{f['PM2.5'].median():.1f} µg/m³")
c3.metric(f"% jam > {batas} µg/m³", f"{(f['PM2.5'].dropna() > batas).mean() * 100:.1f}%")
c4.metric(f"% hari > {batas} µg/m³", f"{(harian['pm25'] > batas).mean() * 100:.1f}%" if len(harian) else "n/a",
          help=f"Dihitung dari {len(harian):,} hari dengan minimal {MIN_JAM_HARIAN} jam data valid.")

tab1, tab2, tab3, tab4 = st.tabs(["Q1: Pola waktu", "Q2: Angin", "Analisis lanjutan", "Catatan data"])

# ---------------- Tab 1 ----------------
with tab1:
    st.subheader("Pada bulan dan jam berapa PM2.5 tertinggi?")
    col_a, col_b = st.columns(2)

    with col_a:
        m = f.groupby("month")["PM2.5"].mean().reindex(range(1, 13))
        fig, ax = plt.subplots(figsize=(6, 4))
        warna = ["#C0392B" if i in {10, 11, 12, 1, 2, 3} else "#B8C0C8" for i in m.index]
        ax.bar(NAMA_BULAN, m.values, color=warna)
        ax.axhline(f["PM2.5"].mean(), color="#333", ls="--", lw=1)
        ax.set_ylabel("PM2.5 (µg/m³)")
        ax.set_title("Rata-rata PM2.5 per bulan (merah = Okt-Mar)", loc="left", fontsize=11)
        sns.despine(); plt.tight_layout(); st.pyplot(fig); plt.close(fig)

    with col_b:
        fig, ax = plt.subplots(figsize=(6, 4))
        pal = {"Dingin": "#C0392B", "Gugur": "#7F8C8D", "Semi": "#E69F00", "Panas": "#0072B2"}
        for s in ["Dingin", "Gugur", "Semi", "Panas"]:
            if s in musim_pilih:
                d = f[f["musim"] == s].groupby("hour")["PM2.5"].mean()
                ax.plot(d.index, d.values, color=pal[s], lw=2.4 if s == "Dingin" else 1.7, label=s)
        ax.set_xticks(range(0, 24, 3)); ax.set_ylim(bottom=0)
        ax.set_xlabel("Jam"); ax.set_ylabel("PM2.5 (µg/m³)")
        ax.set_title("Pola harian PM2.5 per musim", loc="left", fontsize=11)
        ax.legend(frameon=False, ncol=4, fontsize=8, loc="lower center")
        sns.despine(); plt.tight_layout(); st.pyplot(fig); plt.close(fig)

    st.markdown("**Sebaran kategori kualitas udara harian per periode Maret-Februari**")
    hp = (f.groupby("tanggal").agg(pm25=("PM2.5", "mean"), n=("PM2.5", "count"), periode=("periode", "first"))
            .query("n >= @MIN_JAM_HARIAN"))
    if hp.empty:
        st.info("Tidak ada hari dengan data valid yang memadai pada filter ini.")
    else:
        hp["kategori"] = pd.cut(hp["pm25"], bins=BATAS_KAT, labels=NAMA_KAT)
        share = (hp.groupby("periode")["kategori"].value_counts(normalize=True).unstack()
                   .reindex(columns=NAMA_KAT).fillna(0) * 100)
        fig, ax = plt.subplots(figsize=(10, 3.6))
        share.plot(kind="barh", stacked=True, color=WARNA_KAT, ax=ax, width=0.7)
        for cont, tc in zip(ax.containers, TEKS_KAT):
            ax.bar_label(cont, labels=[f"{v:.0f}%" if v >= 4 else "" for v in cont.datavalues],
                         label_type="center", fontsize=8, color=tc)
        ax.invert_yaxis(); ax.set_xlim(0, 100); ax.set_xlabel("% hari valid"); ax.set_ylabel("")
        ax.legend(bbox_to_anchor=(1.01, 1), loc="upper left", frameon=False, fontsize=8)
        sns.despine(); plt.tight_layout(); st.pyplot(fig); plt.close(fig)
        st.caption("Titik batas kategori (35/75/115/150/250) dari ingatan terhadap standar AQI China dan perlu diverifikasi ke dokumen resmi.")

# ---------------- Tab 2 ----------------
with tab2:
    st.subheader("Bagaimana PM2.5 berbeda menurut kecepatan dan arah angin?")
    col_a, col_b = st.columns(2)

    with col_a:
        a = f.groupby("kelas_angin", observed=False)["PM2.5"].agg(["mean", "count"])
        fig, ax = plt.subplots(figsize=(6, 4.2))
        bars = ax.bar(a.index.astype(str), a["mean"], color="#2C7FB8")
        for b, (mu, n) in zip(bars, a.values):
            if n > 0 and not np.isnan(mu):
                ax.text(b.get_x() + b.get_width() / 2, mu + 2, f"{mu:.0f}\n(n={int(n):,})", ha="center", fontsize=8)
        ax.set_ylim(0, np.nanmax(a["mean"].values) * 1.25)
        ax.set_xlabel("Kecepatan angin (m/s)"); ax.set_ylabel("PM2.5 (µg/m³)")
        ax.set_title("Rata-rata PM2.5 menurut kecepatan angin", loc="left", fontsize=11)
        plt.setp(ax.get_xticklabels(), fontsize=8)
        sns.despine(); plt.tight_layout(); st.pyplot(fig); plt.close(fig)

    with col_b:
        ar = f.groupby("wd")["PM2.5"].mean().sort_values()
        fig, ax = plt.subplots(figsize=(6, 4.2))
        warna = ["#C0392B" if i >= len(ar) - 3 else "#2C7FB8" if i < 3 else "#B8C0C8" for i in range(len(ar))]
        ax.barh(ar.index, ar.values, color=warna)
        ax.set_xlabel("PM2.5 (µg/m³)")
        ax.set_title("Menurut arah angin (merah = 3 tertinggi)", loc="left", fontsize=11)
        plt.setp(ax.get_yticklabels(), fontsize=8)
        sns.despine(); plt.tight_layout(); st.pyplot(fig); plt.close(fig)

    st.markdown("**Kecepatan angin x musim (rata-rata PM2.5)**")
    silang = (f.pivot_table(index="kelas_angin", columns="musim", values="PM2.5", aggfunc="mean", observed=False)
                .reindex(columns=[s for s in URUT_MUSIM if s in musim_pilih]))
    fig, ax = plt.subplots(figsize=(7, 3.6))
    sns.heatmap(silang, annot=True, fmt=".0f", cmap="YlOrRd", linewidths=0.5, ax=ax,
                cbar_kws={"label": "PM2.5 (µg/m³)"})
    ax.set_xlabel("Musim"); ax.set_ylabel("Kecepatan angin (m/s)")
    plt.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.caption("Arah dan kecepatan angin saling terkait (angin barat laut cenderung lebih kencang), "
               "sehingga arah sebaiknya dibaca bersama kecepatan pada tab Analisis lanjutan.")

# ---------------- Tab 3 ----------------
with tab3:
    st.subheader("Matriks risiko: peluang jam PM2.5 tinggi menurut arah dan kecepatan angin")
    st.write(f"Persentase jam dengan PM2.5 > **{batas} µg/m³** untuk tiap kombinasi kuadran arah dan kelas kecepatan "
             f"(sel dengan n < {MIN_N_SEL} ditutup abu-abu).")
    dk = f.dropna(subset=["kuadran", "PM2.5"]).copy()
    dk["tinggi"] = dk["PM2.5"] > batas
    risiko = dk.pivot_table(index="kuadran", columns="kelas_angin", values="tinggi", aggfunc="mean", observed=False) * 100
    jumlah = dk.pivot_table(index="kuadran", columns="kelas_angin", values="tinggi", aggfunc="count", observed=False).fillna(0)
    kecil = jumlah < MIN_N_SEL
    label = risiko.round(0).fillna(0).astype(int).astype(str) + "%\n(n=" + jumlah.astype(int).astype(str) + ")"
    fig, ax = plt.subplots(figsize=(9, 4.2))
    sns.heatmap(risiko, annot=label, fmt="", cmap="YlOrRd", vmin=0, vmax=100, mask=kecil | risiko.isna(),
                linewidths=0.5, linecolor="white", ax=ax, cbar_kws={"label": f"% jam > {batas} µg/m³"})
    for i in range(kecil.shape[0]):
        for j in range(kecil.shape[1]):
            if kecil.iloc[i, j]:
                ax.add_patch(plt.Rectangle((j, i), 1, 1, color="#E5E7EA", zorder=2))
                ax.text(j + 0.5, i + 0.5, f"n={int(jumlah.iloc[i, j])}\n(terlalu sedikit)", ha="center",
                        va="center", fontsize=8, color="#555", zorder=3)
    ax.set_xlabel("Kecepatan angin (m/s)"); ax.set_ylabel("Kuadran arah angin")
    plt.tight_layout(); st.pyplot(fig); plt.close(fig)
    st.caption("Kuadran adalah manual grouping berdasarkan derajat kompas (N=0°, E=90°, S=180°, W=270°, batas kiri tertutup). "
               "Ambang per jam hanya indikator, bukan pelanggaran standar harian.")

# ---------------- Tab 4 ----------------
with tab4:
    st.subheader("Catatan kualitas data dan keterbatasan")
    st.markdown(
        """
- **Missing value:** PM2.5 yang hilang hanya diisi (interpolasi waktu) jika celahnya ≤ 6 jam. Sisanya dibiarkan kosong.
- **PM2.5 > PM10** terjadi pada ±6% baris, diberi penanda dan **tidak dihapus**. Uji sensitivitas di notebook tidak mengubah kesimpulan.
- **Outlier PM2.5 > 500** dipertahankan karena kemungkinan besar episode polusi nyata.
- **CO dan NO2** tidak dianalisis karena celah data sangat panjang (hingga 1.517 jam).
- **Satu stasiun, empat tahun:** hasil tidak otomatis berlaku untuk seluruh Beijing, dan hubungan angin-PM2.5 adalah asosiasi, bukan sebab-akibat.
- Rincian lengkap ada di `notebook.ipynb`.
        """
    )
    st.write(f"Data terfilter: **{len(f):,}** jam, **{f['PM2.5'].isna().sum():,}** jam PM2.5 kosong.")
