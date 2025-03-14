import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick

# ---------- Setup Dashboard ----------
st.set_page_config(page_title="Dashboard E-Commerce", layout="wide")
st.title('Dashboard E-Commerce: Produk Terlaris & Metode Pembayaran')

# ---------- Load Data ----------
@st.cache_data
def load_data():
    order_items = pd.read_csv("/data/order_items_dataset.csv")
    products = pd.read_csv("/data/products_dataset.csv")
    product_category_name_translation = pd.read_csv("/data/product_category_name_translation.csv")
    order_payments = pd.read_csv("/data/order_payments_dataset.csv")
    return order_items, products, product_category_name_translation, order_payments

order_items, products, product_category_name_translation, order_payments, orders = load_data()

# ---------- Preprocess Order Date ----------
orders['order_date'] = pd.to_datetime(orders['order_purchase_timestamp']).dt.date

# Sidebar Filter Rentang Tanggal

st.sidebar.header("Muhammad Izzuddin Al Fatih")
st.sidebar.header("Filter Rentang Tanggal")

min_date = orders["order_date"].min()
max_date = orders["order_date"].max()

date_range = st.sidebar.date_input(
    "Silakan pilih rentang tanggal (Pilih tanggal awal & tanggal akhir):",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

# ---------- Validasi Input Tanggal ----------
if len(date_range) != 2:
    st.sidebar.warning("Harap pilih **dua tanggal** (awal dan akhir) untuk melihat data.")
    st.stop()  # Stop eksekusi jika tanggal belum lengkap

start_date, end_date = date_range

# ---------- Filter Data ----------
filtered_orders = orders[(orders['order_date'] >= start_date) & (orders['order_date'] <= end_date)]
filtered_order_items = pd.merge(order_items, filtered_orders[['order_id', 'order_date']], on='order_id', how='inner')
filtered_order_payments = pd.merge(order_payments, filtered_orders[['order_id', 'order_date']], on='order_id', how='inner')

# ---------- Produk Terlaris ----------
st.header("Top & Bottom 5 Kategori Produk Terlaris")

# Merge data produk
merged_order_product = pd.merge(filtered_order_items, products, on="product_id")
merged_order_product = pd.merge(merged_order_product, product_category_name_translation, on="product_category_name")

# Hitung penjualan per kategori
sales_per_category = merged_order_product.groupby("product_category_name_english")["order_item_id"].sum().reset_index()
sales_per_category.rename(columns={"product_category_name_english": "name_product", "order_item_id": "terjual"}, inplace=True)
sales_per_category = sales_per_category.sort_values(by="terjual", ascending=False)

# Top & Bottom 5
top_5_products = sales_per_category.head(5)
bottom_5_products = sales_per_category.tail(5)

# Layout kolom 2 bagian
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 5 Produk Terlaris")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x="terjual", y="name_product", data=top_5_products, palette="Blues_r", ax=ax)
    ax.set_xlabel("Total Terjual")
    ax.set_ylabel("Kategori Produk")
    st.pyplot(fig)

with col2:
    st.subheader("Bottom 5 Produk Terlaris")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(x="terjual", y="name_product", data=bottom_5_products, palette="Reds_r", ax=ax)
    ax.set_xlabel("Total Terjual")
    ax.set_ylabel("Kategori Produk")
    st.pyplot(fig)

# ---------- Metode Pembayaran ----------
st.header("Total Nilai Transaksi Berdasarkan Metode Pembayaran")



payment_summary = filtered_order_payments.groupby("payment_type")["payment_value"].sum().reset_index()
payment_summary["payment_type"] = pd.Categorical(
    payment_summary["payment_type"],
    ["credit_card", "boleto", "voucher", "debit_card", "not_defined"]
)



fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(
    x="payment_type",
    y="payment_value",
    data=payment_summary.sort_values(by="payment_value", ascending=False),
    palette="pastel"
)


ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.title("Total Nilai Transaksi Berdasarkan Metode Pembayaran", fontsize=15)
plt.xlabel("Metode Pembayaran")
plt.ylabel("Total Transaksi (Rp)")

st.pyplot(fig)

# ---------- Kesimpulan & Rekomendasi ----------
# ---------- Kesimpulan & Rekomendasi Otomatis ----------

st.subheader("Kesimpulan & Rekomendasi")

# ------------------ Kesimpulan ------------------

# Cek metode pembayaran dominan
if not payment_summary.empty:
    top_payment_method = payment_summary.sort_values(by="payment_value", ascending=False).iloc[0]["payment_type"]
else:
    top_payment_method = "Tidak ada transaksi"

# Produk terlaris
if not top_5_products.empty:
    best_selling_product = top_5_products.iloc[0]["name_product"]
else:
    best_selling_product = "Tidak ada produk terjual"

# Produk tidak laris
if not bottom_5_products.empty:
    worst_selling_product = bottom_5_products.iloc[0]["name_product"]
else:
    worst_selling_product = "Tidak ada produk tercatat"

# Total produk terjual
total_sales = sales_per_category["terjual"].sum()

# ------------------ Penulisan Kesimpulan ------------------

st.markdown(f"""
**Kesimpulan:**
- Metode pembayaran yang paling banyak digunakan dalam periode **{start_date} hingga {end_date}** adalah **{top_payment_method}**.
- Produk dengan penjualan terbanyak adalah **{best_selling_product}**.
- Produk dengan penjualan terendah adalah **{worst_selling_product}**.
- Total seluruh produk yang terjual pada periode ini adalah **{total_sales:,} unit**.
""")

# ------------------ Rekomendasi Berdasarkan Data ------------------

rekomendasi = []

# Rekomendasi berdasarkan metode pembayaran
if top_payment_method == "credit_card":
    rekomendasi.append("- **Optimalkan promosi dan kemudahan penggunaan kartu kredit** untuk meningkatkan transaksi.")
elif top_payment_method == "boleto":
    rekomendasi.append("- Tingkatkan edukasi dan promosi metode pembayaran **Boleto** agar lebih banyak digunakan.")
elif top_payment_method == "voucher":
    rekomendasi.append("- **Pertimbangkan campaign voucher diskon** untuk menarik lebih banyak pembeli.")
elif top_payment_method == "debit_card":
    rekomendasi.append("- Perbanyak kerjasama dengan bank untuk **program diskon kartu debit**.")
else:
    rekomendasi.append("- **Perlu perhatian khusus**, metode pembayaran belum jelas mendominasi. Evaluasi metode pembayaran yang tersedia.")

# Rekomendasi jika ada produk tidak laris
if worst_selling_product != "Tidak ada produk tercatat":
    rekomendasi.append(f"- **Evaluasi produk '{worst_selling_product}'**: pertimbangkan diskon, bundling, atau penghentian produk.")

# Rekomendasi jika ada produk laris
if best_selling_product != "Tidak ada produk terjual":
    rekomendasi.append(f"- **Pastikan stok cukup** untuk produk terlaris '{best_selling_product}', dan pertimbangkan promosi tambahan.")

# Rekomendasi jika penjualan total kecil
if total_sales < 50:  # Threshold bisa kamu ubah sesuai dataset
    rekomendasi.append("- **Perlu strategi pemasaran baru**, karena total penjualan masih rendah pada periode ini.")

# ------------------ Penulisan Rekomendasi ------------------

st.markdown("**Rekomendasi:**")
for item in rekomendasi:
    st.markdown(item)
