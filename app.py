# streamlit_dashboard_auto_flow.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set layout
st.set_page_config(layout="wide")

# Init session
if "step" not in st.session_state:
    st.session_state.step = "upload"
if "df" not in st.session_state:
    st.session_state.df = None
if "company_name" not in st.session_state:
    st.session_state.company_name = "Nama Perusahaan"

# Upload Section (Langsung tampil saat buka)
st.title("📊 Visualisasi Data Penjualan")
st.markdown("Upload data untuk mulai:")
uploaded_file = st.file_uploader("Upload file (.csv / .xlsx)", type=["csv", "xlsx"])
company_name = st.text_input("Nama Perusahaan", value=st.session_state.company_name)

if uploaded_file:
    st.session_state.company_name = company_name
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    st.session_state.df = df
    st.session_state.step = "select_columns"
    st.query_params["scroll"] = "yes"
    st.experimental_rerun()

# Select Columns Section
if st.session_state.step == "select_columns" and st.session_state.df is not None:
    df = st.session_state.df
    st.markdown("---")
    st.subheader("🛠️ Pilih Kolom")
    col_nama = st.selectbox("Kolom Nama Produk", df.columns)
    col_tanggal = st.selectbox("Kolom Tanggal", df.columns)
    col_jumlah = st.selectbox("Kolom Jumlah Penjualan", df.columns)
    col_kategori = st.selectbox("Kolom Kategori (Opsional)", ["-"] + list(df.columns))
    col_wilayah = st.selectbox("Kolom Wilayah (Opsional)", ["-"] + list(df.columns))
    col_staf = st.selectbox("Kolom Staf Penjualan (Opsional)", ["-"] + list(df.columns))

    if st.button("Tampilkan Visualisasi"):
        st.session_state.col_nama = col_nama
        st.session_state.col_tanggal = col_tanggal
        st.session_state.col_jumlah = col_jumlah
        st.session_state.col_kategori = col_kategori if col_kategori != "-" else None
        st.session_state.col_wilayah = col_wilayah if col_wilayah != "-" else None
        st.session_state.col_staf = col_staf if col_staf != "-" else None
        st.session_state.step = "visualize"
        st.query_params["scroll"] = "yes"
        st.experimental_rerun()

# Visualization Section
if st.session_state.step == "visualize" and st.session_state.df is not None:
    df = st.session_state.df.copy()
    nama = st.session_state.col_nama
    tanggal = st.session_state.col_tanggal
    jumlah = st.session_state.col_jumlah
    kategori = st.session_state.col_kategori
    wilayah = st.session_state.col_wilayah
    staf = st.session_state.col_staf

    st.title(f"📈 Dashboard – {st.session_state.company_name}")
    df[jumlah] = pd.to_numeric(df[jumlah], errors='coerce')
    df[tanggal] = pd.to_datetime(df[tanggal], errors='coerce')
    df.dropna(subset=[jumlah, tanggal], inplace=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("📦 Total Penjualan", int(df[jumlah].sum()))
    col2.metric("🛒 Jenis Produk", df[nama].nunique())
    col3.metric("🗓️ Periode", f"{df[tanggal].min().date()} ➡ {df[tanggal].max().date()}")

    st.markdown("---")
    tgl_min = df[tanggal].min()
    tgl_max = df[tanggal].max()
    start_date, end_date = st.date_input("📅 Filter Tanggal", [tgl_min, tgl_max], min_value=tgl_min, max_value=tgl_max)
    df = df[(df[tanggal] >= pd.to_datetime(start_date)) & (df[tanggal] <= pd.to_datetime(end_date))]

    st.subheader("📈 Penjualan per Waktu")
    st.plotly_chart(px.line(df.groupby(tanggal)[jumlah].sum().reset_index(), x=tanggal, y=jumlah), use_container_width=True)

    st.subheader("🏆 Produk Terlaris")
    st.plotly_chart(px.bar(df.groupby(nama)[jumlah].sum().reset_index().sort_values(by=jumlah, ascending=False), x=nama, y=jumlah), use_container_width=True)

    if wilayah:
        st.subheader("📍 Penjualan per Wilayah")
        st.plotly_chart(px.bar(df.groupby(wilayah)[jumlah].sum().reset_index(), x=wilayah, y=jumlah), use_container_width=True)

    if staf:
        st.subheader("👤 Penjualan per Staf")
        st.plotly_chart(px.bar(df.groupby(staf)[jumlah].sum().reset_index(), x=staf, y=jumlah), use_container_width=True)

    if kategori:
        st.subheader("📂 Kategori Penjualan")
        df_kat = df.groupby(kategori)[jumlah].sum().reset_index()
        st.plotly_chart(go.Figure(data=[go.Pie(labels=df_kat[kategori], values=df_kat[jumlah], hole=0.5)]).update_traces(textinfo='percent+label'), use_container_width=True)

    if staf and wilayah:
        st.subheader("📋 Kinerja Staf per Wilayah")
        df_cso = df.groupby([staf, wilayah])[jumlah].sum().reset_index()
        st.dataframe(df_cso.sort_values(by=jumlah, ascending=False))
