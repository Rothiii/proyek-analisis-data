"""Dashboard E-Commerce Public Dataset (Olist), Proyek Analisis Data Dicoding.

Menjawab 3 pertanyaan bisnis:
  1. Kategori produk dengan revenue tertinggi & terendah
  2. Tren jumlah pesanan & pendapatan bulanan
  3. Sebaran geografis pelanggan (state) di Brazil
Plus analisis lanjutan: segmentasi pelanggan berbasis RFM.

Jalankan dengan:  streamlit run dashboard.py
"""

import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────── KONFIGURASI HALAMAN ───────────────────────────
st.set_page_config(
    page_title="Dashboard E-Commerce Olist",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Palet colorblind-safe (Okabe-Ito), konsisten dengan notebook
PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7",
           "#E69F00", "#56B4E9", "#F0E442", "#000000"]

# Koordinat centroid tiap negara bagian (diturunkan dari dataset geolocation Olist)
STATE_COORD = {
    "AC": (-9.7026, -68.4519), "AL": (-9.5997, -36.0520), "AM": (-3.3493, -60.5374),
    "AP": (0.0860, -51.2343), "BA": (-13.0494, -39.5606), "CE": (-4.3632, -39.0041),
    "DF": (-15.8109, -47.9696), "ES": (-20.1051, -40.5032), "GO": (-16.5776, -49.3342),
    "MA": (-3.7990, -44.8186), "MG": (-19.8646, -44.4216), "MS": (-20.7650, -54.5321),
    "MT": (-14.1565, -55.7090), "PA": (-2.6312, -49.4859), "PB": (-7.0883, -35.8217),
    "PE": (-8.1791, -35.7589), "PI": (-5.7550, -42.5095), "PR": (-24.7936, -50.8797),
    "RJ": (-22.7435, -43.1555), "RN": (-5.8567, -35.9901), "RO": (-10.3413, -62.7206),
    "RR": (2.7171, -60.6729), "RS": (-29.6792, -52.0327), "SC": (-27.2225, -49.6179),
    "SE": (-10.8662, -37.1812), "SP": (-23.1553, -47.0841), "TO": (-9.5037, -48.3487),
}


# ─────────────────────────── LOAD DATA ───────────────────────────
@st.cache_data(show_spinner="Memuat data...")
def load_data():
    main = pd.read_csv(os.path.join(BASE_DIR, "main_data.csv"))
    rfm = pd.read_csv(os.path.join(BASE_DIR, "rfm_data.csv"))
    main["order_purchase_timestamp"] = pd.to_datetime(main["order_purchase_timestamp"])
    main["order_date"] = main["order_purchase_timestamp"].dt.date
    return main, rfm


main_df, rfm_df = load_data()

# ─────────────────────────── SIDEBAR FILTER ───────────────────────────
st.sidebar.header("🔎 Filter Data")

d_min = main_df["order_date"].min()
d_max = main_df["order_date"].max()

date_range = st.sidebar.date_input(
    "Rentang tanggal pembelian",
    value=(d_min, d_max),
    min_value=d_min,
    max_value=d_max,
)
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = d_min, d_max

all_states = sorted(main_df["customer_state"].unique())
sel_states = st.sidebar.multiselect("Negara bagian (state)", all_states, default=all_states)

all_cats = sorted(main_df.loc[main_df["product_category_name_english"] != "unknown",
                              "product_category_name_english"].unique())
sel_cats = st.sidebar.multiselect(
    "Kategori produk",
    all_cats,
    default=all_cats,
    help=("Kategori tanpa nama ('unknown', ~1% pendapatan) disertakan saat semua "
          "kategori dipilih, dan otomatis dikecualikan saat Anda memilih kategori tertentu."),
)

sel_pay = st.sidebar.multiselect(
    "Metode pembayaran",
    sorted(main_df["payment_type"].dropna().unique()),
    default=sorted(main_df["payment_type"].dropna().unique()),
)

st.sidebar.caption(
    f"Periode data tersedia: **{d_min:%d %b %Y}** s.d. **{d_max:%d %b %Y}**  \n"
    "Sumber: E-Commerce Public Dataset (Olist), pesanan berstatus *delivered*."
)

# ─────────────────────────── TERAPKAN FILTER ───────────────────────────
filtered = main_df[
    (main_df["order_date"] >= start_date)
    & (main_df["order_date"] <= end_date)
    & (main_df["customer_state"].isin(sel_states))
    & (main_df["payment_type"].isin(sel_pay))
].copy()

# Filter kategori:
# - Bila semua kategori terpilih (kondisi default), baris 'unknown' ikut dipertahankan
#   agar total pendapatan tetap utuh dan konsisten dengan notebook.
# - Bila pengguna mempersempit ke kategori tertentu, baris 'unknown' ikut dibuang
#   supaya angka KPI benar-benar merepresentasikan kategori yang dipilih.
_cat_mask = filtered["product_category_name_english"].isin(sel_cats)
if set(sel_cats) == set(all_cats):
    _cat_mask |= filtered["product_category_name_english"] == "unknown"
filtered = filtered[_cat_mask]

# ─────────────────────────── HEADER ───────────────────────────
st.title("🛒 Dashboard Analisis E-Commerce Olist (Brazil)")
st.markdown(
    "Analisis data transaksi **E-Commerce Public Dataset (Olist)** untuk periode "
    "**September 2016 - Agustus 2018**. Dashboard ini menjawab tiga pertanyaan bisnis "
    "kategori produk, tren penjualan bulanan, dan sebaran geografis pelanggan "
    "serta dilengkapi segmentasi pelanggan berbasis **RFM**."
)

if filtered.empty:
    st.warning("Tidak ada data yang sesuai dengan filter. Silakan longgarkan filter di sidebar.")
    st.stop()

# ─────────────────────────── KPI ───────────────────────────
total_revenue = filtered["price"].sum()
total_orders = filtered["order_id"].nunique()
total_customers = filtered["customer_unique_id"].nunique()
avg_review = filtered["review_score"].mean()
avg_delivery = filtered["delivery_days"].mean()
late_orders = filtered.loc[filtered["delay_days"] > 0, "order_id"].nunique()
late_pct = late_orders / total_orders * 100 if total_orders else 0
aov = total_revenue / total_orders if total_orders else 0

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Pendapatan", f"R$ {total_revenue:,.0f}".replace(",", "."))
k2.metric("Jumlah Pesanan", f"{total_orders:,}".replace(",", "."))
k3.metric("Pelanggan Unik", f"{total_customers:,}".replace(",", "."))
k4.metric("Rata-rata Nilai Pesanan", f"R$ {aov:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
k5.metric("Rata-rata Skor Review", f"{avg_review:.2f} / 5" if pd.notna(avg_review) else "-")

st.caption(
    f"Rata-rata waktu pengiriman **{avg_delivery:.1f} hari** · "
    f"Pesanan terlambat **{late_orders:,}** pesanan (**{late_pct:.2f}%**)".replace(",", ".")
)
st.divider()

# ─────────────────────────── TABS ───────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Pertanyaan 1: Tren Bulanan",
    "🏷️ Pertanyaan 2: Kategori Produk",
    "🗺️ Pertanyaan 3: Sebaran Geografis",
    "🧩 Analisis Lanjutan: RFM",
])

# ═══════════════ TAB 1: TREN BULANAN ═══════════════
with tab1:
    st.subheader("Tren Jumlah Pesanan & Pendapatan Bulanan")

    trend = (filtered.groupby("order_month")
             .agg(revenue=("price", "sum"), orders=("order_id", "nunique"))
             .reset_index()
             .sort_values("order_month"))
    trend["mom_pct"] = trend["revenue"].pct_change() * 100

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=trend["order_month"], y=trend["revenue"], mode="lines+markers",
        name="Total Pendapatan (R$)", line=dict(color=PALETTE[0], width=3),
        fill="tozeroy", fillcolor="rgba(0,114,178,0.12)",
        hovertemplate="<b>%{x}</b><br>Pendapatan: R$ %{y:,.0f}<extra></extra>",
    ))
    if trend["revenue"].notna().any():
        peak = trend.loc[trend["revenue"].idxmax()]
        fig1.add_annotation(
            x=peak["order_month"], y=peak["revenue"],
            text=f"Puncak: {peak['order_month']}<br>R$ {peak['revenue']:,.0f}",
            showarrow=True, arrowhead=2, yshift=28, font=dict(size=11),
        )
    fig1.update_layout(
        title="Total Pendapatan Bulanan", xaxis_title="Bulan", yaxis_title="Pendapatan (R$)",
        hovermode="x unified", height=420, margin=dict(l=10, r=10, t=60, b=10),
    )
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.bar(
        trend, x="order_month", y="orders", text="orders",
        title="Jumlah Pesanan Bulanan", labels={"order_month": "Bulan", "orders": "Jumlah Pesanan"},
        color_discrete_sequence=[PALETTE[2]],
    )
    fig2.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig2.update_layout(height=400, margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig2, use_container_width=True)

    with st.expander("Lihat tabel data tren bulanan"):
        st.dataframe(
            trend.assign(mom_pct=trend["mom_pct"].round(2)).rename(columns={
                "order_month": "Bulan", "revenue": "Pendapatan (R$)",
                "orders": "Jumlah Pesanan", "mom_pct": "Perubahan MoM (%)",
            }),
            use_container_width=True, hide_index=True,
        )

    c1, c2, c3 = st.columns(3)
    if trend["revenue"].notna().any():
        c1.metric("Bulan dengan pendapatan tertinggi",
                  f"{trend.loc[trend['revenue'].idxmax(), 'order_month']}",
                  f"R$ {trend['revenue'].max():,.0f}".replace(",", "."))
        c2.metric("Pendapatan rata-rata per bulan",
                  f"R$ {trend['revenue'].mean():,.0f}".replace(",", "."))
    if trend["mom_pct"].notna().any():
        c3.metric("Pertumbuhan MoM tertinggi",
                  "%.2f%%" % trend["mom_pct"].max(),
                  f"{trend.loc[trend['mom_pct'].idxmax(), 'order_month']}")

    st.info(
        "**Insight:** Pendapatan tumbuh ~7,5× dari Januari 2017 menuju puncak "
        "**November 2017 (Black Friday)**, lalu melandai dan relatif stabil sepanjang 2018. "
        "Pola lonjakan akhir tahun perlu diantisipasi dengan kapasitas logistik tambahan."
    )

# ═══════════════ TAB 2: KATEGORI ═══════════════
with tab2:
    st.subheader("Kontribusi Pendapatan per Kategori Produk")

    cat = (filtered[filtered["product_category_name_english"] != "unknown"]
           .groupby("product_category_name_english")
           .agg(revenue=("price", "sum"),
                qty=("price", "count"),
                orders=("order_id", "nunique"))
           .sort_values("revenue", ascending=False))
    cat["share_pct"] = cat["revenue"] / cat["revenue"].sum() * 100

    n_show = st.slider("Tampilkan berapa kategori (teratas)", 5, min(30, len(cat)), 10)

    top = cat.head(n_show).sort_values("revenue")
    fig3 = px.bar(
        top, x="revenue", y=top.index, orientation="h",
        title=f"{n_show} Kategori dengan Pendapatan Tertinggi",
        labels={"revenue": "Total Pendapatan (R$)", "y": "Kategori Produk"},
        color_discrete_sequence=[PALETTE[0]], text=top["revenue"],
    )
    fig3.update_traces(texttemplate="R$ %{text:,.0f}", textposition="outside")
    fig3.update_layout(height=520, margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig3, use_container_width=True)

    bot = cat.tail(5).sort_values("revenue", ascending=False)
    fig4 = px.bar(
        bot, x="revenue", y=bot.index, orientation="h",
        title="5 Kategori dengan Pendapatan Terendah",
        labels={"revenue": "Total Pendapatan (R$)", "y": "Kategori Produk"},
        color_discrete_sequence=[PALETTE[1]], text=bot["revenue"],
    )
    fig4.update_traces(texttemplate="R$ %{text:,.2f}", textposition="outside")
    fig4.update_layout(height=380, margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig4, use_container_width=True)

    with st.expander("Lihat tabel lengkap kategori"):
        st.dataframe(
            cat.assign(share_pct=cat["share_pct"].round(2)).rename(columns={
                "revenue": "Pendapatan (R$)", "qty": "Jumlah Item",
                "orders": "Jumlah Pesanan", "share_pct": "Porsi (%)",
            }),
            use_container_width=True,
        )

    ca, cb = st.columns(2)
    ca.metric("Kontribusi 5 kategori teratas", f"{cat.head(5)['share_pct'].sum():.2f}%",
              f"dari {len(cat)} kategori")
    unknown_rev = filtered.loc[filtered["product_category_name_english"] == "unknown", "price"].sum()
    cb.metric("Pendapatan tanpa nama kategori", f"R$ {unknown_rev:,.2f}")

    st.info(
        "**Insight:** 5 kategori teratas (`health_beauty`, `watches_gifts`, "
        "`bed_bath_table`, `sports_leisure`, `computers_accessories`) menyumbang sekitar "
        "**40%** total pendapatan, sementara 5 kategori terbawah hanya **0,026%**. "
        "Pendapatan cukup terkonsentrasi → prioritas stok dan promosi sebaiknya "
        "difokuskan pada kategori teratas."
    )

# ═══════════════ TAB 3: GEOGRAFIS ═══════════════
with tab3:
    st.subheader("Sebaran Geografis Pelanggan di Brazil")

    state = (filtered.groupby("customer_state")
             .agg(revenue=("price", "sum"), orders=("order_id", "nunique"),
                  customers=("customer_unique_id", "nunique"))
             .sort_values("revenue", ascending=False))
    state["share_pct"] = state["revenue"] / state["revenue"].sum() * 100

    top_state = state.head(10).reset_index()
    fig5 = px.bar(
        top_state, x="customer_state", y="revenue", text=top_state["share_pct"].round(1),
        title="10 Negara Bagian dengan Pendapatan Tertinggi",
        labels={"customer_state": "Negara Bagian (state)", "revenue": "Total Pendapatan (R$)"},
        color_discrete_sequence=[PALETTE[0]],
    )
    fig5.update_traces(texttemplate="%{text}%", textposition="outside")
    fig5.update_layout(height=440, yaxis=dict(rangemode="tozero"),
                       margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig5, use_container_width=True)

    # Peta bubble: ukuran menandakan pendapatan
    geo = state.reset_index()
    geo["lat"] = geo["customer_state"].map(lambda s: STATE_COORD.get(s, (np.nan, np.nan))[0])
    geo["lon"] = geo["customer_state"].map(lambda s: STATE_COORD.get(s, (np.nan, np.nan))[1])
    geo = geo.dropna(subset=["lat", "lon"])

    fig6 = px.scatter_geo(
        geo, lat="lat", lon="lon", size="revenue", color="revenue",
        hover_name="customer_state",
        hover_data={"revenue": ":,.0f", "orders": ":,", "share_pct": ":.2f",
                    "lat": False, "lon": False},
        color_continuous_scale="Blues", size_max=55,
        title="Peta Sebaran Pendapatan per Negara Bagian di Brazil",
        labels={"revenue": "Pendapatan (R$)", "orders": "Pesanan"},
    )
    fig6.update_geos(scope="south america", showcountries=True, countrycolor="#999999",
                     landcolor="#F2F2F2", showland=True)
    fig6.update_layout(height=560, margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig6, use_container_width=True)

    with st.expander("Lihat tabel lengkap per negara bagian"):
        st.dataframe(
            state.assign(share_pct=state["share_pct"].round(2)).rename(columns={
                "revenue": "Pendapatan (R$)", "orders": "Pesanan",
                "customers": "Pelanggan", "share_pct": "Porsi (%)",
            }),
            use_container_width=True,
        )

    ga, gb, gc = st.columns(3)
    ga.metric("State dengan pendapatan terbesar", state.index[0],
              f"R$ {state['revenue'].iloc[0]:,.0f}".replace(",", "."))
    gb.metric("Kontribusi 5 state teratas", f"{state.head(5)['share_pct'].sum():.2f}%")
    gc.metric("Jumlah kota unik", f"{filtered['customer_city'].nunique():,}".replace(",", "."))

    st.info(
        "**Insight:** **São Paulo (SP)** sangat dominan (~38% pendapatan), dan 5 state "
        "teratas menyumbang **~74%** total pendapatan. Pelanggan tersebar di ribuan kota, "
        "namun wilayah Utara/Timur Laut berkontribusi kecil **dan** waktu pengirimannya "
        "paling lama → peluang pembangunan pusat distribusi tambahan di luar SP."
    )

# ═══════════════ TAB 4: RFM ═══════════════
with tab4:
    st.subheader("Segmentasi Pelanggan berbasis RFM")
    st.markdown(
        "Segmentasi menggunakan **Recency**, **Frequency**, dan **Monetary** dengan "
        "*scoring* berbasis **kuartil** (R & M) dan **binning manual** (F), lalu "
        "dikelompokkan menjadi **8 segmen** dengan aturan berjenjang (*rule-based*, "
        "tanpa machine learning). Segmentasi dihitung dari **seluruh periode data** "
        "sehingga tidak terpengaruh filter tanggal."
    )

    seg = (rfm_df.groupby("segment")
           .agg(jumlah_pelanggan=("customer_unique_id", "count"),
                total_revenue=("monetary", "sum"),
                rata_recency=("recency", "mean"),
                rata_frequency=("frequency", "mean"),
                rata_monetary=("monetary", "mean"))
           .sort_values("total_revenue", ascending=False))
    seg["pct_pelanggan"] = seg["jumlah_pelanggan"] / len(rfm_df) * 100
    seg["pct_revenue"] = seg["total_revenue"] / rfm_df["monetary"].sum() * 100

    r1, r2, r3 = st.columns(3)
    r1.metric("Total Pelanggan", f"{len(rfm_df):,}".replace(",", "."))
    r2.metric("Pelanggan Sekali Beli",
              f"{(rfm_df['frequency'] == 1).mean() * 100:.1f}%",
              f"{(rfm_df['frequency'] == 1).sum():,} orang".replace(",", "."))
    r3.metric("Jumlah Segmen", f"{rfm_df['segment'].nunique()}")

    fig7 = px.bar(
        seg.sort_values("pct_revenue").reset_index(),
        x="pct_revenue", y="segment", orientation="h", text="pct_revenue",
        title="Kontribusi Pendapatan per Segmen RFM",
        labels={"pct_revenue": "Porsi Total Pendapatan (%)", "segment": "Segmen"},
        color="pct_revenue", color_continuous_scale="Blues",
    )
    fig7.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig7.update_layout(height=460, coloraxis_showscale=False,
                       margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig7, use_container_width=True)

    fig8 = px.scatter(
        rfm_df, x="recency", y="monetary", color="segment",
        title="Peta Pelanggan: Recency vs Monetary per Segmen",
        labels={"recency": "Recency: hari sejak pembelian terakhir",
                "monetary": "Monetary: total belanja (R$)"},
        color_discrete_sequence=PALETTE, opacity=0.4,
    )
    fig8.update_yaxes(type="log")
    fig8.update_traces(marker=dict(size=6))
    fig8.update_layout(height=560, margin=dict(l=10, r=10, t=60, b=10))
    st.plotly_chart(fig8, use_container_width=True)

    st.dataframe(
        seg.round(2).rename(columns={
            "jumlah_pelanggan": "Jumlah Pelanggan", "total_revenue": "Total Revenue (R$)",
            "rata_recency": "Rata-rata Recency (hari)", "rata_frequency": "Rata-rata Frequency",
            "rata_monetary": "Rata-rata Monetary (R$)", "pct_pelanggan": "% Pelanggan",
            "pct_revenue": "% Revenue",
        }),
        use_container_width=True,
    )

    st.info(
        "**Insight:** **97%** pelanggan hanya bertransaksi **satu kali**, masalah retensi "
        "terbesar platform. Namun pelanggan *repeat* rata-rata membelanjakan hampir "
        "**2× lebih besar**. Segmen **`Hibernating (High Value)`** (pelanggan bernilai "
        "tinggi namun sudah ~1 tahun tidak aktif) adalah target utama kampanye *win-back*, "
        "sedangkan **`Champions`** perlu program loyalitas."
    )

st.divider()
st.caption(
    "Dibuat oleh **Rafid Al Khairy** · Dataset: E-Commerce Public Dataset (Olist) · "
    "Submission Proyek Analisis Data, Dicoding Academy"
)
