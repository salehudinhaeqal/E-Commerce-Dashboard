import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Load dataset
full_df = pd.read_csv("dashboard/all_data.csv")
full_df['order_purchase_timestamp'] = pd.to_datetime(full_df['order_purchase_timestamp'])
translation_df = pd.read_csv("E-commerce-public-dataset/product_category_name_translation.csv")

# Fungsi untuk mendapatkan arti nama produk 
def get_product_category_english(product_category_name):
    translation = translation_df[translation_df['product_category_name'] == product_category_name]['product_category_name_english'].values
    if len(translation) > 0:
        return translation[0]
    else:
        return "Nama kategori tidak ditemukan"

# Inisialisasi session state untuk navigasi halaman
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

# Sidebar untuk filter dan navigasi
with st.sidebar:
    # Menampilkan logo besar di dalam lingkaran
    st.markdown(
        """
        <div style='text-align: center;'>
            <div style='
                display: flex; 
                justify-content: center; 
                align-items: center; 
                width: 150px; 
                height: 150px; 
                background-color: #ffffff; 
                border-radius: 50%; 
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                margin: auto;
            '>
                <span style='font-size: 80px;'>🛒</span>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

    st.header("📊 E-Commerce Dashboard")
    
    # Filter tanggal
    min_date = full_df['order_purchase_timestamp'].min().date()
    max_date = full_df['order_purchase_timestamp'].max().date()
    start_date, end_date = st.date_input("📅 Pilih Rentang Tanggal", [min_date, max_date], min_value=min_date, max_value=max_date)
    
    # Filter dataset berdasarkan tanggal
    filtered_df = full_df[(full_df['order_purchase_timestamp'].dt.date >= start_date) & (full_df['order_purchase_timestamp'].dt.date <= end_date)]
    
    # Fitur terjemahan kategori produk
    st.markdown("🌐 Terjemahan Kategori Produk ", unsafe_allow_html=True) # Menggunakan markdown untuk judul
    category_name = st.selectbox("Pilih Kategori Produk:", full_df['product_category_name'].unique())
    english_name = get_product_category_english(category_name)

    # Kotak khusus untuk menampilkan arti nama produk
    st.markdown(f"""
        <div style='
            background-color: var(--background-secondary-color);
            color: var(--text-color);
            padding: 10px; 
            border-radius: 5px;
            margin-top: -10px;
        '>
            <strong>Arti dari {category_name}:</strong> {english_name}
        </div>
    """, unsafe_allow_html=True)

    # Tombol untuk melihat data mentah
    if st.button("📜 Lihat Data Mentah"):
        st.session_state.page = "data"
        st.rerun()

    # Copyright
    st.caption('Copyright (c) Haeqal Salehudin 2025')

# Halaman Data Mentah
if st.session_state.page == "data":
    st.title("📜 Data Mentah")
    st.dataframe(filtered_df)

    # Tombol kembali ke dashboard
    if st.button("⬅ Kembali ke Dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()

    st.stop()

# Halaman Dashboard
st.title("📈 Dashboard Analisis E-commerce")

# ---- 1. METRICS (Ringkasan Data) ----
col1, col2, col3 = st.columns(3)
col1.metric("🛒 Total Pesanan", f"{filtered_df['order_id'].nunique():,}")
col2.metric("📦 Total Produk", f"{filtered_df['product_id'].nunique():,}")
col3.metric("💰 Total Pendapatan", f"Rp {filtered_df['price'].sum():,.2f}")

# ---- 2. PRODUK TERLARIS ----
st.subheader("🏆 6 Produk Terlaris")
product_counts = filtered_df['product_id'].value_counts().reset_index()
product_counts.columns = ['product_id', 'purchase_count']
top_products = product_counts.head(10)
product_names = filtered_df[['product_id', 'product_category_name']].drop_duplicates()
top_products = pd.merge(top_products, product_names, on='product_id')

plt.figure(figsize=(12, 6))
norm = plt.Normalize(top_products['purchase_count'].min(), top_products['purchase_count'].max())
colors = plt.cm.Blues(norm(top_products['purchase_count']))
ax = sns.barplot(
    x="product_category_name", y="purchase_count", data=top_products,
    palette=colors, errorbar=None, hue="product_category_name", legend=False
)
for p in ax.patches:
    ax.annotate(f"{int(p.get_height())}", (p.get_x() + p.get_width() / 2.0, p.get_height()),
                ha="center", va="center", xytext=(0, 10), textcoords="offset points")
plt.title("6 Produk Terlaris")
plt.xticks(rotation=45, ha="right")
st.pyplot(plt)

st.write(f"➡ Produk dengan pembelian tertinggi adalah **{top_products.iloc[0]['product_category_name']}** dengan **{top_products.iloc[0]['purchase_count']}** transaksi.")

# ---- 3. KATEGORI PRODUK TERLARIS ----
st.subheader("📌 20 Kategori Produk Terlaris")
category_sales = filtered_df['product_category_name'].value_counts().reset_index()
category_sales.columns = ['product_category_name', 'sales_count']
top_categories = category_sales.head(20)

plt.figure(figsize=(12, 8))
sns.barplot(x='sales_count', y='product_category_name', data=top_categories, palette='viridis', hue='product_category_name', legend=False)
plt.title('20 Kategori Produk Terlaris')
plt.xlabel('Jumlah Penjualan')
plt.ylabel('Kategori Produk')
st.pyplot(plt)

st.write(f"➡ Kategori produk dengan penjualan tertinggi adalah **{top_categories.iloc[0]['product_category_name']}** dengan **{top_categories.iloc[0]['sales_count']}** transaksi.")

# ---- 4. POLA PEMBELIAN BERDASARKAN WAKTU ----
st.subheader("⏳ Pola Pembelian Berdasarkan Waktu")
filtered_df['purchase_day_of_week'] = filtered_df['order_purchase_timestamp'].dt.day_name()
filtered_df['purchase_month'] = filtered_df['order_purchase_timestamp'].dt.month_name()

day_sales = filtered_df['purchase_day_of_week'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
month_sales = filtered_df['purchase_month'].value_counts().reindex(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])

# Visualisasi hari
plt.figure(figsize=(12, 6))
max_day = day_sales.idxmax()
bars = plt.bar(day_sales.index, day_sales.values, color='skyblue')
bars[day_sales.index.get_loc(max_day)].set_color('royalblue')
plt.title('Pola Pembelian Berdasarkan Hari dalam Seminggu')
st.pyplot(plt)

st.write(f"➡ Hari dengan transaksi terbanyak adalah **{max_day}** dengan **{day_sales[max_day]}** transaksi.")

# Visualisasi bulan
plt.figure(figsize=(12, 6))
max_month = month_sales.idxmax()
bars = plt.bar(month_sales.index, month_sales.values, color='skyblue')
bars[month_sales.index.get_loc(max_month)].set_color('royalblue')
plt.title('Pola Pembelian Berdasarkan Bulan dalam Setahun')
st.pyplot(plt)

st.write(f"➡ Bulan dengan transaksi tertinggi adalah **{max_month}** dengan **{month_sales[max_month]}** transaksi.")