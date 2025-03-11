import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick

st.set_page_config(page_title="Dashboard E-Commerce", layout="wide")

st.title('📊 Dashboard E-Commerce: Produk Terlaris & Metode Pembayaran')

# ---------- Load Data ----------
@st.cache_data
def load_data():
    order_items = pd.read_csv("../data/order_items_dataset.csv")
    products = pd.read_csv("../data/products_dataset.csv")
    product_category_name_translation = pd.read_csv("../data/product_category_name_translation.csv")
    order_payments = pd.read_csv("../data/order_payments_dataset.csv")
    return order_items, products, product_category_name_translation, order_payments

order_items, products, product_category_name_translation, order_payments = load_data()

# ---------- Produk Terlaris ----------
st.header("📈 Top & Bottom 5 Kategori Produk Terlaris")

# Merge dan proses data
merged_order_product = pd.merge(order_items, products, on="product_id")
merged_order_product = pd.merge(merged_order_product, product_category_name_translation, on="product_category_name")
sales_per_category = merged_order_product.groupby("product_category_name_english")["order_item_id"].sum().reset_index()
sales_per_category.rename(columns={"product_category_name_english": "name_product", "order_item_id": "terjual"}, inplace=True)
sales_per_category = sales_per_category.sort_values(by="terjual", ascending=False)

# Top dan Bottom 5
top_5_products = sales_per_category.head(5)
bottom_5_products = sales_per_category.tail(5)

# Visualisasi
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(14, 6))

# Warna
top_colors = ["#72BCD4"] * 5
bottom_colors = ["#D98880"] * 5

# Barplot Top 5
sns.barplot(x="terjual", y="name_product", data=top_5_products, palette=top_colors, ax=axes[0])
axes[0].set_title("Top 5 Produk Terlaris", fontsize=14)
axes[0].set_xlabel("Total Terjual", fontsize=12)
axes[0].set_ylabel("Kategori Produk", fontsize=12)
for index, value in enumerate(top_5_products["terjual"]):
    axes[0].text(value + max(top_5_products["terjual"]) * 0.02, index, f"{value:,}", va="center", fontsize=10)

# Barplot Bottom 5
sns.barplot(x="terjual", y="name_product", data=bottom_5_products, palette=bottom_colors, ax=axes[1])
axes[1].set_title("Bottom 5 Produk Terlaris", fontsize=14)
axes[1].set_xlabel("Total Terjual", fontsize=12)
axes[1].set_ylabel("")
for index, value in enumerate(bottom_5_products["terjual"]):
    axes[1].text(value + max(bottom_5_products["terjual"]) * 0.05, index, f"{value:,}", va="center", fontsize=10)

plt.tight_layout()
st.pyplot(fig)

with st.expander("ℹ️ Penjelasan Data Produk Terlaris"):
    st.write("""
    Grafik ini menampilkan lima kategori produk dengan jumlah penjualan tertinggi dan terendah. 
    Informasi ini berguna untuk menentukan strategi pemasaran dan pengelolaan produk.
    """)

# ---------- Metode Pembayaran ----------
st.header("💳 Total Nilai Transaksi Berdasarkan Metode Pembayaran")

# Summarize data pembayaran
payment_summary = order_payments.groupby("payment_type")["payment_value"].sum().reset_index()

# Urutkan kategori
payment_summary["payment_type"] = pd.Categorical(
    payment_summary["payment_type"],
    ["credit_card", "boleto", "voucher", "debit_card", "not_defined"]
)

# Warna
colors_ = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Visualisasi
fig, ax = plt.subplots(figsize=(8, 5))
ax = sns.barplot(
    x="payment_type",
    y="payment_value",
    data=payment_summary.sort_values(by="payment_value", ascending=False),
    palette=colors_
)

# Format angka di axis Y
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,}'))

plt.title("Total Nilai Transaksi Berdasarkan Metode Pembayaran", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='x', labelsize=12)

st.pyplot(fig)

with st.expander("ℹ️ Penjelasan Metode Pembayaran"):
    st.write("""
    Grafik ini menampilkan total nilai transaksi berdasarkan metode pembayaran yang digunakan pelanggan. 
    Informasi ini membantu memahami preferensi pelanggan dan menentukan metode pembayaran yang perlu difokuskan.
    """)
