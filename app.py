import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image("logoMATS.png", width=250)  # Gambar 40px
with col2:
    st.markdown("## Aplikasi Visualisasi Data Penjualan")


# Tabs
tab1, tab2 = st.tabs(["📁 Upload Data", "📈 Dashboard"])

# State
if "df" not in st.session_state:
    st.session_state.df = None
if "col_nama" not in st.session_state:
    st.session_state.col_nama = None
if "col_tanggal" not in st.session_state:
    st.session_state.col_tanggal = None
if "col_jumlah" not in st.session_state:
    st.session_state.col_jumlah = None

# ============== TAB 1: Upload File ==============
with tab1:
    st.header("Unggah File Penjualan")
    uploaded_file = st.file_uploader("Upload file (.csv atau .xlsx)", type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.write("Preview data:")
        st.dataframe(df.head())

        st.markdown("### Pilih Kolom")
        col_nama = st.selectbox("Kolom Nama Produk", df.columns)
        col_tanggal = st.selectbox("Kolom Tanggal", df.columns)
        col_jumlah = st.selectbox("Kolom Jumlah Penjualan", df.columns)

        # Opsional kolom tambahan
        col_kategori = st.selectbox("Kolom Kategori (Opsional)", ["-"] + list(df.columns))
        col_wilayah = st.selectbox("Kolom Wilayah (Opsional)", ["-"] + list(df.columns))
        col_staf = st.selectbox("Kolom Staf Penjualan (Opsional)", ["-"] + list(df.columns))

        # Simpan ke session_state
        st.session_state.df = df
        st.session_state.col_nama = col_nama
        st.session_state.col_tanggal = col_tanggal
        st.session_state.col_jumlah = col_jumlah
        st.session_state.col_kategori = col_kategori if col_kategori != "-" else None
        st.session_state.col_wilayah = col_wilayah if col_wilayah != "-" else None
        st.session_state.col_staf = col_staf if col_staf != "-" else None

        st.success("✅ Data berhasil disimpan. Lanjut ke tab Dashboard.")

# ============== TAB 2: Dashboard ==============
with tab2:
    st.header("📊 Dashboard Visualisasi Data")

    if st.session_state.df is None:
        st.warning("Silakan upload data di tab pertama.")
    else:
        df = st.session_state.df.copy()
        col_nama = st.session_state.col_nama
        col_tanggal = st.session_state.col_tanggal
        col_jumlah = st.session_state.col_jumlah
        col_kategori = st.session_state.col_kategori
        col_wilayah = st.session_state.col_wilayah
        col_staf = st.session_state.col_staf

        df[col_jumlah] = pd.to_numeric(df[col_jumlah], errors='coerce')
        df[col_tanggal] = pd.to_datetime(df[col_tanggal], errors='coerce')
        df = df.dropna(subset=[col_jumlah, col_tanggal])

        if df.empty:
            st.error("❌ Tidak ada data valid.")
        else:
            # Summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📦 Total Penjualan", int(df[col_jumlah].sum()))
            with col2:
                st.metric("🛒 Jumlah Jenis Produk", df[col_nama].nunique())
            with col3:
                st.metric("🗓️ Rentang Waktu", f"{df[col_tanggal].min().date()} ➡ {df[col_tanggal].max().date()}")

            # Filter tanggal
            st.markdown("---")
            st.subheader("📅 Filter Rentang Tanggal")
            tgl_min = df[col_tanggal].min()
            tgl_max = df[col_tanggal].max()
            start_date, end_date = st.date_input("Pilih Tanggal", [tgl_min, tgl_max], min_value=tgl_min, max_value=tgl_max)
            df = df[(df[col_tanggal] >= pd.to_datetime(start_date)) & (df[col_tanggal] <= pd.to_datetime(end_date))]

            # Total penjualan per waktu
            st.markdown("---")
            st.subheader("📈 Total Penjualan per Waktu")
            df_harian = df.groupby(col_tanggal)[col_jumlah].sum().reset_index()
            fig1 = px.line(df_harian, x=col_tanggal, y=col_jumlah)
            st.plotly_chart(fig1, use_container_width=True)

            # Produk terlaris
            st.subheader("🏆 Produk Terlaris")
            df_produk = df.groupby(col_nama)[col_jumlah].sum().reset_index().sort_values(by=col_jumlah, ascending=False)
            fig2 = px.bar(df_produk, x=col_nama, y=col_jumlah)
            st.plotly_chart(fig2, use_container_width=True)

            # Wilayah (jika ada)
            if col_wilayah:
                st.subheader("📍 Penjualan per Wilayah")
                df_wil = df.groupby(col_wilayah)[col_jumlah].sum().reset_index().sort_values(by=col_jumlah, ascending=False)
                fig3 = px.bar(df_wil, x=col_wilayah, y=col_jumlah)
                st.plotly_chart(fig3, use_container_width=True)

            # Staf (jika ada)
            if col_staf:
                st.subheader("👤 Penjualan per Staf")
                df_staf = df.groupby(col_staf)[col_jumlah].sum().reset_index().sort_values(by=col_jumlah, ascending=False)
                fig4 = px.bar(df_staf, x=col_staf, y=col_jumlah)
                st.plotly_chart(fig4, use_container_width=True)

            # Kategori (donut chart)
            if col_kategori:
                st.subheader("📂 Donut Chart Penjualan per Kategori")
                df_kat = df.groupby(col_kategori)[col_jumlah].sum().reset_index()
                fig5 = go.Figure(data=[go.Pie(labels=df_kat[col_kategori], values=df_kat[col_jumlah], hole=0.5)])
                fig5.update_traces(textinfo='percent+label')
                st.plotly_chart(fig5, use_container_width=True)

            # CSO Table (jika ada kolom staf dan wilayah)
            if col_staf and col_wilayah:
                st.subheader("📋 Tabel Kinerja Staf per Wilayah")
                df_cso = df.groupby([col_staf, col_wilayah])[col_jumlah].sum().reset_index()
                st.dataframe(df_cso.sort_values(by=col_jumlah, ascending=False))
