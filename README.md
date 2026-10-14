# Proyek Analisis Data — E-Commerce Public Dataset (Olist)

Proyek akhir untuk Submission **Dicoding Academy 555 — Belajar Fundamental Analisis Data**.
Analisis menyeluruh atas **109.880 baris transaksi** e-commerce Brazil periode
**September 2016 – Agustus 2018**, dari proses data wrangling sampai dashboard
interaktif yang dapat difilter.

Dibuat oleh **Rafid Al Khairy**.

---

## Daftar Isi

- [Deskripsi Proyek](#deskripsi-proyek)
- [Dataset](#dataset)
- [Pertanyaan Bisnis](#pertanyaan-bisnis)
- [Struktur Proyek](#struktur-proyek)
- [Cara Menjalankan](#cara-menjalankan)
- [Deploy Dashboard](#deploy-dashboard)
- [Temuan Utama](#temuan-utama)
- [Metodologi](#metodologi)
- [Kesimpulan](#kesimpulan)

---

## Deskripsi Proyek

Proyek ini menganalisis data transaksi marketplace Brazil (**Olist**) untuk menjawab
tiga pertanyaan bisnis, ditambah satu analisis lanjutan segmentasi pelanggan.
Seluruh alur kerja terdokumentasi di `notebook.ipynb` (41 sel, **sudah dijalankan
dan seluruh outputnya tersimpan**), dari pengumpulan data hingga kesimpulan.

Output akhirnya berupa **dashboard interaktif berbasis Streamlit** yang mendukung
filter tanggal, negara bagian, kategori produk, dan metode pembayaran.

## Dataset

**E-Commerce Public Dataset (Olist)** — dataset transaksi marketplace Brasil,
terbit 2018, mencakup 9 tabel CSV:

| Tabel | Isi |
|---|---|
| `customers_dataset.csv` | Data pelanggan & lokasi |
| `orders_dataset.csv` | Data pesanan & status |
| `order_items_dataset.csv` | Rincian item tiap pesanan |
| `order_payments_dataset.csv` | Transaksi pembayaran |
| `order_reviews_dataset.csv` | Ulasan & skor pelanggan |
| `products_dataset.csv` | Katalog produk |
| `sellers_dataset.csv` | Data penjual |
| `product_category_name_translation.csv` | Terjemahan kategori (PT → EN) |
| `geolocation_dataset.csv` | Koordinat geografis (dipakai untuk derivasi peta) |

Analisis difokuskan pada pesanan berstatus **`delivered`** (96.211 pesanan) agar
revenue yang dihitung benar-benar merepresentasikan transaksi yang berhasil.

## Pertanyaan Bisnis

1. **Kategori produk apa yang menyumbang pendapatan tertinggi, dan mana yang terendah?**
   → Mengarahkan fokus stok, promosi, dan keputusan portofolio kategori.

2. **Bagaimana tren jumlah pesanan dan pendapatan dari waktu ke waktu, dan bagaimana
   sebaran geografis pelanggan?**
   → Menentukan kebutuhan ekspansi dan lokasi pembangunan pusat distribusi.

3. **Bagaimana pengaruh keterlambatan pengiriman terhadap skor review pelanggan?**
   → Menguji hipotesis bahwa layanan logistik adalah driver utama kepuasan.

Ditambah **analisis lanjutan**: segmentasi pelanggan berbasis **RFM**
(*Recency, Frequency, Monetary*).

## Struktur Proyek

```
Proyek-Analisis-Data/
├── data/                   # Dataset mentah (8 CSV Olist)
├── dashboard/
│   ├── dashboard.py        # Aplikasi Streamlit
│   ├── main_data.csv       # Tabel analisis (di-generate oleh notebook)
│   └── rfm_data.csv        # Hasil segmentasi RFM (di-generate oleh notebook)
├── notebook.ipynb          # Notebook analisis lengkap (41 sel, sudah dijalankan)
├── requirements.txt        # Dependensi Python
├── url.txt                 # Tautan dashboard yang sudah di-deploy
└── README.md
```

## Cara Menjalankan

**Prasyarat:** Python 3.9–3.12.

```bash
# 1. Buat virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Instal dependensi
pip install -r requirements.txt

# 3. Jalankan dashboard
streamlit run dashboard/dashboard.py
```

Dashboard otomatis terbuka di `http://localhost:8501`.

> **Catatan:** `main_data.csv` dan `rfm_data.csv` sudah disertakan dalam repositori,
> sehingga dashboard dapat langsung dijalankan tanpa menjalankan notebook lebih dahulu.
> Jika ingin membuatnya ulang dari dataset mentah, jalankan seluruh sel di `notebook.ipynb`.

## Deploy Dashboard

Dashboard di-deploy ke **Streamlit Community Cloud** (gratis).

1. Push repositori ini ke **GitHub**.
2. Buka [share.streamlit.io](https://share.streamlit.io), login dengan GitHub.
3. **New app** → pilih repositori → isi:
   - *Main file path*: `dashboard/dashboard.py`
   - *Python version*: `3.12`
4. Deploy, lalu **salin URL dashboard** dan simpan ke dalam `url.txt`.

## Temuan Utama

**Pendapatan**
- Total pendapatan **R$ 13.181.027,13** dari 96.211 pesanan, dengan rata-rata
  nilai pesanan (AOV) **R$ 137,00**.
- Pendapatan tumbuh **~7,5× pada 2017**, memuncak di **November 2017**
  (**R$ 987.765,37**, 7.289 pesanan) bertepatan dengan musim promo akhir tahun,
  lalu **melandai dan stabil** di kisaran R$ 826.437 – 977.545 per bulan sepanjang 2018.

**Kategori produk**
- 5 kategori teratas menyumbang **40,41%** pendapatan, didominasi
  `health_beauty`, `watches_gifts`, dan `bed_bath_table`.
- 5 kategori terbawah hanya **0,026%** — kandidat untuk dievaluasi ulang.

**Geografis**
- **São Paulo (SP)** menyumbang **38,36%** pendapatan; 5 negara bagian teratas
  (**SP, RJ, MG, RS, PR**) mencapai **73,94%**.
- Pelanggan tersebar di **4.083 kota**, namun wilayah Norden & Timur Laut
  berkontribusi kecil **dan** memiliki waktu pengiriman terpanjang.

**Layanan pengiriman**
- **delivery_days** memiliki korelasi negatif terkuat terhadap skor review
  (**r = −0,305**), disusul `delay_days` (r = −0,233). Harga praktis tidak
  berpengaruh (r = 0,003).
- Pesanan terlambat (**6,79%**) mendapat skor **2,26**, sedangkan pesanan tepat
  waktu mendapat **4,21** — selisih **1,95 poin**. Karena keterlambatan hanya
  terjadi pada sebagian kecil pesanan, perbaikan di titik ini memberi dampak besar
  dengan biaya yang terbatas.

**Segmentasi RFM**
- **97% pelanggan hanya bertransaksi sekali** — ini masalah retensi terbesar.
- Namun pelanggan yang *repeat* rata-rata membelanjakan hampir **2× lebih besar**.
- Segmen **`Hibernating (High Value)`** (nilai tinggi, sudah lama tidak aktif) adalah
  target utama kampanye *win-back*, sementara **`Champions`** perlu program loyalitas.

## Metodologi

**Data Wrangling**
- *Gathering* — 9 dataset Olist, digabung dengan `merge` berjenjang.
- *Assessing* — audit kualitas data: missing value, duplikasi, dan nilai anomali
  pada setiap kolom.
- *Cleaning* —
  - Agregasi `order_payments` menjadi **satu baris per order** (99.440 baris) untuk
    mencegah *over-count* akibat pembayaran cicilan.
  - Deduplikasi `order_reviews`: buang duplikat `review_id`, lalu pertahankan
    **review terbaru per `order_id`** → 99.224 review bersih dengan skor diskret 1–5.
  - Terjemahkan nama kategori dari Portugis ke Inggris.
  - Penghapusan duplikat dan baris tidak valid.
  - Nilai *outlier* harga dan ongkos kirim **tidak dihapus** — nilainya valid dan
    justru menjadi temuan penting (contoh: ongkos kirim ke wilayah terpencil).

**Analisis**
- Exploratory Data Analysis univariat, bivariat, dan multivariat (matriks korelasi).
- Visualisasi deskriptif dan eksplanatif untuk ketiga pertanyaan bisnis.
- Segmentasi RFM dengan *scoring* berbasis **kuartil** (R & M) dan **binning
  manual** (F, karena distribusi F sangat *skewed*), lalu pengelompokan
  **berjenjang (*rule-based*)** menjadi 8 segmen dengan cakupan 100%.
  Pendekatan ini **sengaja tanpa machine learning** agar hasil tetap
  mudah dijelaskan dan diaudit.

## Kesimpulan

Tiga rekomendasi utama:

1. **Kurangi ketergantungan pada São Paulo** dengan membangun pusat distribusi
   di wilayah Selatan dan Timur Laut — 73,94% pendapatan terkonsentrasi di 5
   negara bagian, namun wilayah yang dilayani saat ini lambat dan mahal.
2. **Prioritaskan keunggulan operasional pada 5 kategori teratas** yang menyumbang
   40,41% pendapatan, sekaligus tinjau ulang 5 kategori terbawah yang nyaris
   tidak berkontribusi.
3. **Perbaiki ketepatan waktu pengiriman sebagai prioritas layanan.** Selisih
   skor review 1,95 poin antara pesanan terlambat dan tepat waktu menunjukkan
   ini adalah perbaikan cepat (*quick win*) dengan dampak paling besar per unit usaha.

---

**Dibuat oleh:** Rafid Al Khairy
**Sumber data:** E-Commerce Public Dataset (Olist)
**Kursus:** Dicoding Academy 555 — Belajar Fundamental Analisis Data